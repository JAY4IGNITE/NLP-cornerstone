"""Shared FastAPI dependencies: runtime state, trace ids, admin auth."""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, Request

from backend.app.runtime import AppState


def get_state(request: Request) -> AppState:
    state: AppState | None = getattr(request.app.state, "ctx", None)
    if state is None:  # pragma: no cover - lifespan always sets this
        raise HTTPException(status_code=503, detail="service not ready")
    return state


def get_trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "unknown")


def require_admin(
    request: Request,
    x_admin_token: str = Header(default="", alias="X-Admin-Token"),
) -> None:
    """Fail closed: admin routes are disabled unless a token is configured and matches."""
    configured = get_state(request).settings.admin_api_token.strip()
    if not configured:
        raise HTTPException(status_code=403, detail="admin API disabled (no token configured)")
    if not hmac.compare_digest(x_admin_token, configured):
        raise HTTPException(status_code=401, detail="invalid admin token")
