"""Self-contained BM25 (Okapi) lexical retrieval.

Deterministic, dependency-free (pure NumPy). We implement it directly rather
than depend on ``rank_bm25`` so the core has no extra install and results are
reproducible.
"""

from __future__ import annotations

import math

import numpy as np


class BM25:
    def __init__(self, corpus_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.corpus_tokens = corpus_tokens
        self.n_docs = len(corpus_tokens)
        self.doc_len = np.array([len(d) for d in corpus_tokens], dtype=np.float32)
        self.avgdl = float(self.doc_len.mean()) if self.n_docs else 0.0

        # term frequencies per doc + document frequency per term
        self.tf: list[dict[str, int]] = []
        df: dict[str, int] = {}
        for tokens in corpus_tokens:
            counts: dict[str, int] = {}
            for t in tokens:
                counts[t] = counts.get(t, 0) + 1
            self.tf.append(counts)
            for t in counts:
                df[t] = df.get(t, 0) + 1
        self.df = df
        # BM25+ style idf (always positive) to avoid negative scores on common terms.
        self.idf = {
            t: math.log(1.0 + (self.n_docs - freq + 0.5) / (freq + 0.5)) for t, freq in df.items()
        }

    def get_scores(self, query_tokens: list[str]) -> np.ndarray:
        scores = np.zeros(self.n_docs, dtype=np.float32)
        if self.avgdl == 0.0:
            return scores
        for term in query_tokens:
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i in range(self.n_docs):
                f = self.tf[i].get(term, 0)
                if f == 0:
                    continue
                denom = f + self.k1 * (1.0 - self.b + self.b * self.doc_len[i] / self.avgdl)
                scores[i] += idf * (f * (self.k1 + 1.0)) / denom
        return scores

    def top_n(self, query_tokens: list[str], n: int) -> list[tuple[int, float]]:
        scores = self.get_scores(query_tokens)
        if self.n_docs == 0:
            return []
        n = min(n, self.n_docs)
        # argpartition for speed, then stable sort by (-score, idx) for determinism.
        idx = np.argpartition(-scores, n - 1)[:n]
        ranked = sorted(idx.tolist(), key=lambda i: (-float(scores[i]), i))
        return [(i, float(scores[i])) for i in ranked]
