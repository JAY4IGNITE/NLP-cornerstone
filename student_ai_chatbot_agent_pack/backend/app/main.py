"""FastAPI application factory (API.md, ARCHITECTURE.md).

Wires logging, the runtime pipeline (built once in the lifespan), a per-request
trace id, permissive CORS for the local frontend, and a catch-all handler that
returns a structured error without leaking internals.
"""

from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api import admin, chat, feedback, health
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging, get_logger, log_event
from backend.app.runtime import build_state
from backend.app.schemas.chat import ErrorResponse

logger = get_logger("api")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.ctx = build_state(settings)
        log_event(logger, logging.INFO, "startup", **settings.safe_summary())
        yield

    app = FastAPI(
        title="Student AI Chatbot",
        version="0.1.0",
        description="Grounded college-information assistant with citations and abstention.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _trace(request: Request, call_next):
        request.state.trace_id = uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Trace-Id"] = request.state.trace_id
        return response

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        trace_id = getattr(request.state, "trace_id", "unknown")
        log_event(
            logger, logging.ERROR, "unhandled_error",
            trace_id=trace_id, route=str(request.url.path), error_category=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                trace_id=trace_id, code="INTERNAL_ERROR", message="internal server error"
            ).model_dump(),
        )

    app.include_router(health.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    
    # Serve compiled frontend if it exists
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    frontend_dist = settings.path("../frontend/dist")
    if frontend_dist.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            # If path requests a specific file (e.g. favicon.ico) that exists
            file_path = frontend_dist / full_path
            if full_path and file_path.is_file():
                return FileResponse(file_path)
            # Otherwise serve index.html (SPA routing)
            return FileResponse(frontend_dist / "index.html")
    else:
        logger.warning("Frontend dist directory not found. API only mode.")
        
    return app


app = create_app()
