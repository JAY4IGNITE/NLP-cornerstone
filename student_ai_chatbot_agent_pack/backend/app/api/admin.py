"""Admin endpoints (API.md). Token-protected; fail closed.

/admin/reindex rebuilds the index from currently-approved sources, persists it,
and atomically swaps it into the running service. Only approved sources are
ingested (the ingestion pipeline enforces this), so reindexing can never
introduce unapproved content.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from backend.app.api.deps import get_state, get_trace_id, require_admin
from backend.app.core.logging import get_logger, log_event
from backend.app.ingestion.pipeline import ingest_sources
from backend.app.retrieval.store import LocalKnowledgeBase
from backend.app.runtime import AppState
from backend.app.schemas.chat import ReindexRequest, ReindexResponse
from backend.app.services.orchestrator import Orchestrator
from backend.app.services.retrieval import RetrievalService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
logger = get_logger("api.admin")


@router.post("/reindex", response_model=ReindexResponse)
def reindex(
    payload: ReindexRequest, request: Request, state: AppState = Depends(get_state)
) -> ReindexResponse:
    trace_id = get_trace_id(request)
    kb_version = payload.source_version.strip() or state.settings.knowledge_base_version
    try:
        chunks, _manifest = ingest_sources(state.settings)
        kb = LocalKnowledgeBase.build(
            chunks,
            state.embedder,
            knowledge_base_version=kb_version,
            index_dir=state.settings.path(state.settings.index_dir),
        )
    except Exception as exc:  # noqa: BLE001 - report failure, keep serving the old index
        log_event(
            logger, logging.ERROR, "reindex_failed",
            trace_id=trace_id, route="/admin/reindex", error_category=type(exc).__name__,
        )
        return ReindexResponse(
            status="error", knowledge_base_version=state.kb.kb_version, message="reindex failed"
        )

    # Atomically swap the new index into the running service.
    state.kb = kb
    state.retrieval = RetrievalService(kb, state.embedder, state.settings)
    state.orchestrator = Orchestrator(
        state.intent, state.retrieval, state.provider, state.orchestrator.validator
    )
    log_event(
        logger, logging.INFO, "reindex_ok",
        trace_id=trace_id, route="/admin/reindex",
        knowledge_base_version=kb_version, chunks_indexed=kb.size,
    )
    return ReindexResponse(
        status="ok",
        knowledge_base_version=kb_version,
        chunks_indexed=kb.size,
        message=f"indexed {kb.size} chunks",
    )
