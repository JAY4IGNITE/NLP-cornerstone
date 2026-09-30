"""Structured, secret-safe logging.

Emits single-line JSON logs. A small allow-list of fields is supported for
request audit records (PRD FR-07 / SECURITY_PRIVACY.md §2). Raw user text is
never logged unless STORE_RAW_QUERY is explicitly enabled.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

_SECRET_HINTS = ("api_key", "apikey", "token", "password", "secret", "authorization")

# Fields permitted in an audit log record.
AUDIT_FIELDS = {
    "trace_id",
    "route",
    "latency_ms",
    "intent",
    "intent_confidence",
    "retrieved_chunk_ids",
    "retrieval_scores",
    "provider",
    "model",
    "response_status",
    "error_category",
    "knowledge_base_version",
}


def _redact(record: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for k, v in record.items():
        lk = k.lower()
        if any(h in lk for h in _SECRET_HINTS):
            clean[k] = "<redacted>"
        else:
            clean[k] = v
    return clean


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(_redact(extra))
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, level: int, msg: str, **fields: Any) -> None:
    """Log a structured event. Secret-looking keys are redacted."""
    logger.log(level, msg, extra={"extra_fields": _redact(fields)})


def audit_record(**fields: Any) -> dict[str, Any]:
    """Build an audit record limited to the allow-listed audit fields."""
    return _redact({k: v for k, v in fields.items() if k in AUDIT_FIELDS})
