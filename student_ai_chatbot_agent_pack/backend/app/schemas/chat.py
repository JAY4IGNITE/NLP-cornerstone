"""API request/response schemas (API.md, DETAILS.md §8)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["answered", "abstained", "error"]
ErrorCode = Literal["VALIDATION_ERROR", "PROVIDER_ERROR", "INDEX_ERROR", "INTERNAL_ERROR"]


class ChatRequest(BaseModel):
    message: str = Field(..., description="Free-text student question.")


class Citation(BaseModel):
    document_id: str
    title: str
    location: str = Field(default="", description="page/section/chunk reference")
    chunk_id: str | None = None
    content: str | None = Field(default=None, description="Actual extracted text chunk")


class IntentInfo(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    trace_id: str
    status: Status
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    intent: IntentInfo


class ErrorResponse(BaseModel):
    trace_id: str
    status: Literal["error"] = "error"
    code: ErrorCode
    message: str


class FeedbackRequest(BaseModel):
    trace_id: str
    rating: Literal["helpful", "not_helpful"]
    reason: str | None = Field(
        default=None, description="Optional predefined reason code (no free-form PII)."
    )


class FeedbackResponse(BaseModel):
    trace_id: str
    ok: bool = True


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"] = "ok"
    version: str
    knowledge_base_version: str
    index_ready: bool = False
    provider: str = "extractive"


class ReindexRequest(BaseModel):
    source_version: str


class ReindexResponse(BaseModel):
    status: Literal["ok", "error"]
    knowledge_base_version: str
    chunks_indexed: int = 0
    message: str = ""
