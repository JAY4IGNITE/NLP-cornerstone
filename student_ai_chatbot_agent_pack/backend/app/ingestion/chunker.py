"""Chunking (RAG.md §3).

Word-approximate token windows with overlap, preserving section headings and
locations. Table-like sections (lines with '|') are kept whole so row meaning
is not lost.
"""

from __future__ import annotations

from backend.app.ingestion.metadata import DocumentMeta, chunk_id_for
from backend.app.ingestion.parser import ParsedDocument, Section
from backend.app.retrieval.store import Chunk

TARGET_TOKENS = 450
OVERLAP_TOKENS = 60


def _looks_like_table(text: str) -> bool:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False
    piped = sum(1 for ln in lines if ln.count("|") >= 2)
    return piped >= max(2, len(lines) // 2)


def _split_words(text: str) -> list[str]:
    return text.split()


def _windows(words: list[str], target: int, overlap: int) -> list[list[str]]:
    if len(words) <= target:
        return [words]
    step = max(1, target - overlap)
    out: list[list[str]] = []
    i = 0
    while i < len(words):
        out.append(words[i : i + target])
        if i + target >= len(words):
            break
        i += step
    return out


def chunk_section(section: Section, meta: DocumentMeta, start_ordinal: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    keep_whole = _looks_like_table(section.text)
    pieces = [section.text] if keep_whole else [
        " ".join(w) for w in _windows(_split_words(section.text), TARGET_TOKENS, OVERLAP_TOKENS)
    ]
    for j, piece in enumerate(pieces):
        ordinal = start_ordinal + j
        loc = section.location if len(pieces) == 1 else f"{section.location} (part {j + 1})"
        chunks.append(
            Chunk(
                chunk_id=chunk_id_for(meta.document_id, ordinal),
                document_id=meta.document_id,
                document_version=meta.document_version,
                ordinal=ordinal,
                heading=section.heading,
                location=loc,
                content=piece.strip(),
                title=meta.title,
                source_id=meta.source_id,
                authority=meta.authority,
                approval_status=meta.approval_status,
                published_at=meta.published_at,
                effective_from=meta.effective_from,
                is_current=meta.is_current,
            )
        )
    return chunks


def chunk_document(parsed: ParsedDocument, meta: DocumentMeta) -> list[Chunk]:
    chunks: list[Chunk] = []
    ordinal = 1
    for section in parsed.sections:
        produced = chunk_section(section, meta, ordinal)
        chunks.extend(produced)
        ordinal += len(produced)
    return chunks
