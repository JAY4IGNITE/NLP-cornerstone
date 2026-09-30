"""Deterministic extractive grounded generator (offline default).

Composes the answer strictly from the retrieved evidence — it selects the
evidence sentences that best match the question and returns them verbatim, with
the chunk ids they came from as citations. It has no external knowledge, cannot
fabricate, and abstains when the evidence does not actually address the question.
This makes it a safe default that satisfies the anti-hallucination mandate
without any API key.

Relevance gate (why abstention triggers):
  A hybrid retriever always returns *something*, and RRF normalization pushes the
  top fused score near 1.0 regardless of quality, so the fused-score threshold
  cannot tell "relevant" from "best of a bad lot". The real relevance decision is
  made here, on lexical grounds the offline provider can actually justify:
    * a matched query token is *distinctive* only if it is not ubiquitous across
      the candidate evidence (a cheap within-evidence IDF), and
    * the chosen answer must cover enough of the question's content words.
  A query whose meaningful words are absent from the evidence (off-topic queries,
  and prompt-injection attempts padded with instruction words) fails the gate and
  abstains, even though retrieval surfaced high-scoring chunks.
"""

from __future__ import annotations

import re
from collections import Counter

from backend.app.core.normalization import tokenize
from backend.app.llm.base import ABSTENTION_MESSAGE, GroundedAnswer, GroundedRequest

# Determiners, quantifiers, question and filler words carry no college-specific
# signal; matching on them must never make an answer look grounded.
_STOP = {
    "the", "a", "an", "of", "for", "in", "on", "to", "is", "are", "how", "many",
    "much", "what", "which", "when", "where", "who", "whom", "whose", "why", "do",
    "does", "did", "i", "my", "we", "our", "us", "you", "your", "can", "could",
    "would", "should", "and", "or", "please", "kindly", "tell", "let", "know",
    "me", "about", "at", "be", "with", "this", "that", "it", "its", "as", "from",
    "there", "will", "any", "all", "each", "every", "per", "get", "give", "want",
    "need", "also", "some", "into", "by",
}
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+|(?<=\|)\s{2,}")
_MIN_OVERLAP = 1
_MAX_SENTENCES = 3
# Relevance gate thresholds.
_MIN_COVERAGE = 0.34  # fraction of the question's content words the answer must cover
_SHORT_QUERY = 2      # queries this short must be (near-)fully covered


def _content_tokens(text: str) -> list[str]:
    # Keep multi-char words and any numeral: single digits like the "4" in
    # "semester 4" or "6 credits" are highly informative in this domain.
    return [t for t in tokenize(text) if t not in _STOP and (len(t) > 1 or t.isdigit())]


def _sentences(text: str) -> list[str]:
    parts = [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]
    return [p for p in parts if len(p) > 2]


class ExtractiveProvider:
    name = "extractive"

    def __init__(self, model: str = "extractive-grounded-v1") -> None:
        self.model = model

    @property
    def available(self) -> bool:
        return True

    def _abstain(self) -> GroundedAnswer:
        return GroundedAnswer("abstained", ABSTENTION_MESSAGE, [], self.name, self.model)

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer:
        if not request.evidence:
            return self._abstain()

        q_content = _content_tokens(request.question)
        q_set = set(q_content)
        if not q_set:  # question was all stopwords; fall back to raw tokens
            q_set = set(tokenize(request.question))
        if not q_set:
            return self._abstain()

        # Within-evidence document frequency: a token in many chunks is not
        # distinctive (acts as a cheap IDF over the candidate set).
        n_ev = len(request.evidence)
        common_cutoff = max(1, n_ev // 2)
        df: Counter[str] = Counter()
        for ev in request.evidence:
            for tok in set(_content_tokens(ev.text)):
                df[tok] += 1

        def is_distinctive(token: str) -> bool:
            return df.get(token, 0) <= common_cutoff

        scored: list[tuple[float, str, str, frozenset[str]]] = []
        for rank, ev in enumerate(request.evidence):
            rank_boost = 1.0 / (1 + rank)
            for sent in _sentences(ev.text):
                s_tokens = set(_content_tokens(sent))
                matched = q_set & s_tokens
                if len(matched) < _MIN_OVERLAP:
                    continue
                weight = sum(1.0 if is_distinctive(t) else 0.25 for t in matched)
                # prefer sentences that contain query numbers / codes verbatim
                digit_bonus = 0.5 if any(re.search(r"\d", t) and t in matched for t in q_set) else 0.0
                score = weight + digit_bonus + 0.1 * rank_boost
                scored.append((score, sent, ev.chunk_id, frozenset(matched)))

        if not scored:
            return self._abstain()

        scored.sort(key=lambda x: (-x[0], x[1]))
        chosen: list[str] = []
        cited: list[str] = []
        seen: set[str] = set()
        matched_all: set[str] = set()
        for _, sent, chunk_id, matched in scored:
            norm = sent.lower()
            if norm in seen:
                continue
            seen.add(norm)
            chosen.append(sent.rstrip("."))
            matched_all |= matched
            if chunk_id not in cited:
                cited.append(chunk_id)
            if len(chosen) >= _MAX_SENTENCES:
                break

        # --- relevance gate: is the question actually answered by this evidence? ---
        distinctive_matched = {t for t in matched_all if is_distinctive(t)}
        coverage = len(matched_all) / len(q_set)
        has_code_or_number = any(re.search(r"\d", t) for t in matched_all)
        # Query content words that occur in NONE of the candidate evidence: the
        # evidence simply does not talk about them.
        absent_from_evidence = {t for t in q_set if df.get(t, 0) == 0}

        if not distinctive_matched and not has_code_or_number:
            # Only ubiquitous filler words overlapped — not grounded.
            return self._abstain()
        if len(q_set) <= _SHORT_QUERY:
            # Terse queries carry no redundancy: every content word is load-
            # bearing. If any of them is absent from the evidence entirely, the
            # evidence is about something else — e.g. "what time is it in
            # London" pivoting on an unrelated exam "reporting time" — so a
            # single generic token must not carry the answer. Require both
            # near-full coverage and no wholly-unaddressed content word.
            if absent_from_evidence or coverage < 0.5:
                return self._abstain()
        elif coverage < _MIN_COVERAGE:
            return self._abstain()

        answer = ". ".join(chosen).strip()
        if not answer.endswith((".", "!", "?")):
            answer += "."
        return GroundedAnswer("answered", answer, cited, self.name, self.model)
