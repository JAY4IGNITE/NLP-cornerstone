"""Citation validation (RAG.md §8, SECURITY_PRIVACY.md).

The final gate against hallucination. A generated answer is only allowed to
reach the student if every citation it carries points to a chunk that was
*actually retrieved* for this query, and an ``answered`` response carries at
least one such citation. Anything else fails **closed** to abstention.

This defends against two failure modes:
- a provider inventing a chunk id that was never retrieved, and
- a provider claiming to answer while citing nothing verifiable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from backend.app.llm.base import ABSTENTION_MESSAGE, GroundedAnswer


@dataclass
class CitationDecision:
    status: str  # "answered" | "abstained"
    answer: str
    valid_chunk_ids: list[str] = field(default_factory=list)
    dropped_chunk_ids: list[str] = field(default_factory=list)
    reason: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "answered"


class CitationValidator:
    """Verify cited chunks were retrieved; abstain on any failure."""

    def validate(
        self, answer: GroundedAnswer, retrieved_chunk_ids: Iterable[str]
    ) -> CitationDecision:
        allowed = set(retrieved_chunk_ids)

        # A provider that already abstained stays abstained.
        if answer.status != "answered":
            return CitationDecision("abstained", ABSTENTION_MESSAGE, [], [], "provider_abstained")

        valid: list[str] = []
        dropped: list[str] = []
        for cid in answer.cited_chunk_ids:
            if cid in allowed and cid not in valid:
                valid.append(cid)
            elif cid not in allowed:
                dropped.append(cid)

        # An answered response must be backed by at least one real citation.
        if not valid:
            return CitationDecision(
                "abstained", ABSTENTION_MESSAGE, [], dropped, "no_valid_citation"
            )

        if not answer.answer.strip():
            return CitationDecision("abstained", ABSTENTION_MESSAGE, [], dropped, "empty_answer")

        return CitationDecision("answered", answer.answer, valid, dropped, "validated")
