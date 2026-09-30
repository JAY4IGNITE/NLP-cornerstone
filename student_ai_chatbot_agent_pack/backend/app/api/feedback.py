"""Feedback endpoint (API.md, SECURITY_PRIVACY.md).

Records a thumbs-up/down against a trace id. No free-form text is stored to
avoid capturing PII; only a predefined reason code is accepted. Feedback is
written to the structured log (a durable sink can be added without changing the
contract).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from backend.app.api.deps import get_state
from backend.app.core.logging import get_logger, log_event
from backend.app.runtime import AppState
from backend.app.schemas.chat import FeedbackRequest, FeedbackResponse

router = APIRouter(tags=["feedback"])
logger = get_logger("api.feedback")


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(
    payload: FeedbackRequest, request: Request, state: AppState = Depends(get_state)
) -> FeedbackResponse:
    log_event(
        logger, logging.INFO, "feedback",
        trace_id=payload.trace_id,
        route="/feedback",
        rating=payload.rating,
        reason=payload.reason or "",
    )
    return FeedbackResponse(trace_id=payload.trace_id, ok=True)
