"""Text embeddings with a deterministic offline fallback.

Two backends behind one interface:

* ``sentence-transformers`` — real ``all-MiniLM-L6-v2`` (384-d), used when the
  ``ml`` extra is installed and the model is available locally.
* ``hash`` — deterministic signed feature-hashing into ``dim`` buckets. No
  network, no model download, stable across runs/machines. This is the default
  so the prototype is fully functional offline.

All vectors are L2-normalized, so cosine similarity == dot product.
"""

from __future__ import annotations

import hashlib

import numpy as np

from backend.app.core.logging import get_logger
from backend.app.core.normalization import tokenize

logger = get_logger("embeddings")


def _hash_token(token: str) -> tuple[int, float]:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    h = int.from_bytes(digest, "little")
    sign = 1.0 if (h >> 63) & 1 else -1.0
    return h, sign


def _normalize_rows(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return mat / norms


class EmbeddingModel:
    def __init__(self, model_name: str, dim: int, mode: str = "auto") -> None:
        self.model_name = model_name
        self.dim = dim
        self.requested_mode = mode
        self._st = None
        self.mode = self._resolve(mode)

    def _resolve(self, mode: str) -> str:
        if mode == "hash":
            return "hash"
        local_only = mode == "auto"
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            kwargs = {}
            if local_only:
                # Never hit the network in auto mode; use cache if present.
                import os

                os.environ.setdefault("HF_HUB_OFFLINE", "1")
                os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            self._st = SentenceTransformer(self.model_name)
            self.dim = int(self._st.get_sentence_embedding_dimension())
            logger.info("loaded sentence-transformers backend")
            return "sentence-transformers"
        except Exception as exc:  # noqa: BLE001 - any failure => deterministic fallback
            logger.warning(
                "sentence-transformers unavailable (%s); using deterministic hash embeddings",
                type(exc).__name__,
            )
            self._st = None
            return "hash"

    def _hash_embed(self, texts: list[str]) -> np.ndarray:
        mat = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            toks = tokenize(text)
            grams = toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:])]
            for g in grams:
                h, sign = _hash_token(g)
                mat[i, h % self.dim] += sign
        return _normalize_rows(mat)

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        if self.mode == "sentence-transformers" and self._st is not None:
            vecs = self._st.encode(
                texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
            )
            return np.asarray(vecs, dtype=np.float32)
        return self._hash_embed(texts)

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]
