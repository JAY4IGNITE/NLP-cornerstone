"""Ingestion pipeline: registry -> parse -> chunk (fails closed on approval).

Produces chunks plus a per-source manifest (with content hashes) for the index
build manifest / reproducibility.
"""

from __future__ import annotations

import hashlib

from backend.app.core.config import Settings
from backend.app.core.logging import get_logger
from backend.app.ingestion.chunker import chunk_document
from backend.app.ingestion.metadata import DocumentMeta
from backend.app.ingestion.parser import parse_source
from backend.app.ingestion.source_registry import SourceRegistry
from backend.app.retrieval.store import Chunk

logger = get_logger("ingestion")


def ingest_sources(settings: Settings) -> tuple[list[Chunk], list[dict]]:
    registry = SourceRegistry.load(settings.path(settings.source_registry_path))
    approved = registry.approved_sources()
    if not approved:
        logger.warning("no approved sources in registry %s", settings.source_registry_path)
    chunks: list[Chunk] = []
    manifest: list[dict] = []
    for rec in approved:
        if not rec.local_path:
            logger.warning("approved source %s has no local_path; skipped", rec.source_id)
            continue
        path = settings.path(rec.local_path)
        if not path.exists():
            logger.warning("source file missing for %s: %s", rec.source_id, path)
            continue
        parsed = parse_source(path)
        meta = DocumentMeta(
            document_id=rec.source_id,
            document_version=rec.version or "v1",
            title=rec.title,
            source_id=rec.source_id,
            authority=rec.authority,
            document_type=rec.document_type,
            approval_status=rec.approval_status,
            published_at=rec.published_at,
            effective_from=rec.effective_from,
            is_current=True,
        )
        doc_chunks = chunk_document(parsed, meta)
        chunks.extend(doc_chunks)
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        manifest.append(
            {
                "source_id": rec.source_id,
                "title": rec.title,
                "document_type": rec.document_type,
                "version": rec.version,
                "approval_status": rec.approval_status,
                "demo_only": rec.demo_only,
                "chunk_count": len(doc_chunks),
                "content_hash": content_hash,
                "local_path": rec.local_path,
            }
        )
        logger.info("ingested %s -> %d chunks", rec.source_id, len(doc_chunks))
    return chunks, manifest
