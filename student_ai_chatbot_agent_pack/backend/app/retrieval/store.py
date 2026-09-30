"""Knowledge-base store: chunk records + hybrid index (local, offline-first).

The on-disk index under ``artifacts/index/`` is the reproducible source of
truth for MVP retrieval:

* ``chunks.jsonl``   — one chunk record (metadata + text) per line
* ``embeddings.npy`` — (n_chunks, dim) float32, row-aligned to chunks.jsonl
* ``manifest.json``  — kb version, embedding model/mode/dim, counts, hashes

An optional pgvector-backed store (db.py) exposes the same query interface when
DATABASE_URL is configured.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from backend.app.core.normalization import tokenize
from backend.app.retrieval.bm25 import BM25
from backend.app.retrieval.embeddings import EmbeddingModel
from backend.app.retrieval.vector import VectorIndex


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    document_version: str
    ordinal: int
    heading: str
    location: str
    content: str
    title: str
    source_id: str
    authority: str
    approval_status: str = "approved"
    published_at: str | None = None
    effective_from: str | None = None
    is_current: bool = True
    content_hash: str = ""
    token_count: int = 0

    def __post_init__(self) -> None:
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode("utf-8")).hexdigest()[:16]
        if not self.token_count:
            self.token_count = len(tokenize(self.content))

    def embed_text(self) -> str:
        # Embed title + heading + content (RAG.md §4).
        parts = [p for p in (self.title, self.heading, self.content) if p]
        return "\n".join(parts)


class LocalKnowledgeBase:
    """In-memory hybrid index backed by the local index files."""

    def __init__(self, chunks: list[Chunk], embeddings: np.ndarray, manifest: dict) -> None:
        self.chunks = chunks
        self.embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        self.manifest = manifest
        self._by_id = {c.chunk_id: c for c in chunks}
        self._bm25 = BM25([tokenize(c.embed_text()) for c in chunks])
        self._vector = VectorIndex(self.embeddings)

    # ---- queries ----
    def search_dense(self, query_vec: np.ndarray, n: int) -> list[tuple[str, float]]:
        return [(self.chunks[i].chunk_id, s) for i, s in self._vector.search(query_vec, n)]

    def search_lexical(self, query: str, n: int) -> list[tuple[str, float]]:
        hits = self._bm25.top_n(tokenize(query), n)
        # Max-normalize BM25 scores into [0,1] for interpretable thresholds.
        top = max((s for _, s in hits), default=0.0) or 1.0
        return [(self.chunks[i].chunk_id, s / top) for i, s in hits]

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        return self._by_id.get(chunk_id)

    def all_chunks(self) -> list[Chunk]:
        return self.chunks

    @property
    def size(self) -> int:
        return len(self.chunks)

    @property
    def kb_version(self) -> str:
        return str(self.manifest.get("knowledge_base_version", "unknown"))

    # ---- persistence ----
    @staticmethod
    def build(
        chunks: list[Chunk],
        embedder: EmbeddingModel,
        *,
        knowledge_base_version: str,
        index_dir: Path | None = None,
    ) -> LocalKnowledgeBase:
        texts = [c.embed_text() for c in chunks]
        embeddings = embedder.embed(texts) if texts else np.zeros((0, embedder.dim), np.float32)
        manifest = {
            "knowledge_base_version": knowledge_base_version,
            "embedding_model": embedder.model_name,
            "embedding_mode": embedder.mode,
            "embedding_dim": int(embedder.dim),
            "chunk_count": len(chunks),
            "content_hash": _corpus_hash(chunks),
        }
        kb = LocalKnowledgeBase(chunks, embeddings, manifest)
        if index_dir is not None:
            kb.save(index_dir)
        return kb

    def save(self, index_dir: Path) -> None:
        index_dir.mkdir(parents=True, exist_ok=True)
        with (index_dir / "chunks.jsonl").open("w", encoding="utf-8") as f:
            for c in self.chunks:
                f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
        np.save(index_dir / "embeddings.npy", self.embeddings)
        (index_dir / "manifest.json").write_text(
            json.dumps(self.manifest, indent=2), encoding="utf-8"
        )

    @staticmethod
    def load(index_dir: Path) -> LocalKnowledgeBase:
        chunks_path = index_dir / "chunks.jsonl"
        if not chunks_path.exists():
            raise FileNotFoundError(
                f"index not found at {index_dir}. Run: python scripts/build_index.py"
            )
        chunks = [
            Chunk(**json.loads(line))
            for line in chunks_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        embeddings = np.load(index_dir / "embeddings.npy")
        manifest = json.loads((index_dir / "manifest.json").read_text(encoding="utf-8"))
        return LocalKnowledgeBase(chunks, embeddings, manifest)


def _corpus_hash(chunks: list[Chunk]) -> str:
    h = hashlib.sha256()
    for c in sorted(chunks, key=lambda x: x.chunk_id):
        h.update(c.chunk_id.encode())
        h.update(c.content_hash.encode())
    return h.hexdigest()[:16]
