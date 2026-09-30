"""Health check endpoint (API.md)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.api.deps import get_state
from backend.app.runtime import AppState
from backend.app.schemas.chat import HealthResponse

router = APIRouter(tags=["ops"])


@router.get("/health", response_model=HealthResponse)
def health(state: AppState = Depends(get_state)) -> HealthResponse:
    return HealthResponse(
        status="ok" if state.index_ready else "degraded",
        version=state.settings.app_env,
        knowledge_base_version=state.kb.kb_version,
        index_ready=state.index_ready,
        provider=state.provider.name,
    )
