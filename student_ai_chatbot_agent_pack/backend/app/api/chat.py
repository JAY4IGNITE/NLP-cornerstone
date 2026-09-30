"""Chat endpoint — the grounded question-answering entrypoint (API.md)."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from backend.app.api.deps import get_state, get_trace_id
from backend.app.core.logging import audit_record, get_logger, log_event
from backend.app.core.normalization import QueryValidationError, validate_query
from backend.app.runtime import AppState
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    ErrorResponse,
    IntentInfo,
)

router = APIRouter(tags=["chat"])
logger = get_logger("api.chat")


@router.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}})
def chat(payload: ChatRequest, request: Request, state: AppState = Depends(get_state)):
    trace_id = get_trace_id(request)
    started = time.perf_counter()

    try:
        validate_query(payload.message, max_chars=state.settings.max_query_chars)
    except QueryValidationError as exc:
        log_event(
            logger, logging.WARNING, "chat_validation_error",
            **audit_record(trace_id=trace_id, route="/chat", response_status="error",
                           error_category="VALIDATION_ERROR"),
        )
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                trace_id=trace_id, code="VALIDATION_ERROR", message=str(exc)
            ).model_dump(),
        )

    outcome = state.orchestrator.answer(payload.message)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    log_event(
        logger, logging.INFO, "chat",
        **audit_record(
            trace_id=trace_id,
            route="/chat",
            latency_ms=latency_ms,
            intent=outcome.intent_label,
            intent_confidence=outcome.intent_confidence,
            retrieved_chunk_ids=outcome.retrieved_chunk_ids,
            retrieval_scores=outcome.retrieval_scores,
            provider=outcome.provider,
            model=outcome.model,
            response_status=outcome.status,
            knowledge_base_version=state.kb.kb_version,
        ),
    )

    return ChatResponse(
        trace_id=trace_id,
        status=outcome.status,  # "answered" | "abstained"
        answer=outcome.answer,
        citations=[
            Citation(
                document_id=c.document_id,
                title=c.title,
                location=c.location,
                chunk_id=c.chunk_id,
                content=c.content,
            )
            for c in outcome.citations
        ],
        intent=IntentInfo(label=outcome.intent_label, confidence=outcome.intent_confidence),
    )
