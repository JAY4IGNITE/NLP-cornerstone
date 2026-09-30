"""Document metadata used during ingestion (RAG.md §2)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DocumentMeta:
    document_id: str
    document_version: str
    title: str
    source_id: str
    authority: str
    document_type: str
    approval_status: str = "approved"
    published_at: str | None = None
    effective_from: str | None = None
    is_current: bool = True


def chunk_id_for(document_id: str, ordinal: int) -> str:
    return f"{document_id}-C{ordinal:03d}"
