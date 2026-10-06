"""Default offline CampusNLP API.

/api/query uses the deterministic demonstration pipeline. The incoming advanced
pipeline remains available at /api/chat and its complete inspection API is
preserved in backend.legacy_api, without loading it during default startup.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StringConstraints

from src.pipeline import HybridPipeline

BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = BASE_DIR / "data" / "feedback_log.json"
_log_lock = Lock()
logger = logging.getLogger(__name__)

app = FastAPI(title="CampusNLP API", description="University query understanding and evidence retrieval")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
nlp_pipeline = HybridPipeline()


class QueryRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class ChatRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    chat_history: list[dict[str, str]] | None = Field(default_factory=list)
    top_k: int | None = Field(default=4, ge=1, le=10)


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    intent: str
    feedback: str = Field(pattern="^(thumbs_up|thumbs_down)$")
    comments: str | None = None


@app.post("/api/query")
def query_endpoint(req: QueryRequest):
    result = nlp_pipeline.process_query(req.query)
    return {
        "query": result["query"],
        "intent": result["intent"],
        "confidence": round(result["confidence"], 2),
        "answer": result["response"],
        # This index has document attribution, but no reliable page metadata.
        "sources": [{"document": result["source"]}] if result["source"] else [],
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "CampusNLP", "mode": "deterministic_demo"}


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    # Keep optional RAG initialization away from the default UI and startup.
    from backend.pipeline import pipeline
    return pipeline.process_query(query=req.query, chat_history=req.chat_history, top_k=req.top_k or 4)


def _append_log(file_path: Path, entry: dict) -> bool:
    try:
        with _log_lock:
            data = json.loads(file_path.read_text(encoding="utf-8")) if file_path.exists() else []
            if not isinstance(data, list):
                return False
            data.append(entry)
            temporary = file_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(data[-500:], indent=2), encoding="utf-8")
            temporary.replace(file_path)
        return True
    except (OSError, ValueError):
        logger.warning("Could not save feedback")
        return False


@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackRequest):
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), **feedback.model_dump()}
    if not _append_log(FEEDBACK_FILE, entry):
        raise HTTPException(status_code=503, detail="Feedback could not be saved. Please try again.")
    return {"status": "success", "message": "Feedback logged successfully"}
