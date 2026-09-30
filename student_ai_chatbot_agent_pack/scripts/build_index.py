"""Build and persist the retrieval index from approved sources.

query-time source of truth. Produces artifacts/index/{chunks.jsonl,
embeddings.npy, manifest.json}. Runs fully offline with hash embeddings, or uses
sentence-transformers when the model is available locally.
"""

from __future__ import annotations

import _common

from backend.app.ingestion.pipeline import ingest_sources
from backend.app.retrieval.embeddings import EmbeddingModel
from backend.app.retrieval.store import LocalKnowledgeBase


def main() -> int:
    settings = _common.get_settings()
    _common.configure_logging(settings.log_level)
    _common.banner("Build retrieval index")

    chunks, _manifest = ingest_sources(settings)
    if not chunks:
        _common.fail("no chunks to index")
        return 1

    embedder = EmbeddingModel(settings.embedding_model, settings.embedding_dim, settings.embedding_mode)
    _common.ok(f"embedding backend: {embedder.mode} (dim={embedder.dim})")

    index_dir = settings.path(settings.index_dir)
    kb = LocalKnowledgeBase.build(
        chunks,
        embedder,
        knowledge_base_version=settings.knowledge_base_version,
        index_dir=index_dir,
    )
    _common.ok(f"indexed {kb.size} chunks -> {index_dir}")
    print(f"       kb_version:   {kb.kb_version}")
    print(f"       content_hash: {kb.manifest.get('content_hash')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
