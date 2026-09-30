"""Dense vector search (local NumPy cosine).

Operates on an L2-normalized embedding matrix, so cosine similarity is a single
matrix-vector dot product. This is the offline "edge" vector store; the optional
pgvector backend (store.py) exposes the same ranked output.
"""

from __future__ import annotations

import numpy as np


class VectorIndex:
    def __init__(self, matrix: np.ndarray) -> None:
        # matrix: (n_chunks, dim), each row L2-normalized.
        self.matrix = np.ascontiguousarray(matrix, dtype=np.float32)
        self.n = self.matrix.shape[0]

    def search(self, query_vec: np.ndarray, n: int) -> list[tuple[int, float]]:
        if self.n == 0:
            return []
        q = np.asarray(query_vec, dtype=np.float32).reshape(-1)
        sims = self.matrix @ q  # cosine, since rows and q are normalized
        n = min(n, self.n)
        idx = np.argpartition(-sims, n - 1)[:n]
        ranked = sorted(idx.tolist(), key=lambda i: (-float(sims[i]), i))
        return [(i, float(sims[i])) for i in ranked]
