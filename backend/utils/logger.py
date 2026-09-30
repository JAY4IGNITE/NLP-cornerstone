"""Structured logger without logging credentials."""
import logging
import json
import sys
import time
from typing import Any, Dict, Optional

class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "structured_data") and isinstance(record.structured_data, dict):
            # Sanitize any keys that might contain sensitive tokens
            sanitized = {}
            for k, v in record.structured_data.items():
                if "key" in k.lower() or "token" in k.lower() or "secret" in k.lower() or "auth" in k.lower():
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = v
            log_data.update(sanitized)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logger(name: str = "student_chatbot") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

def log_event(event_type: str, details: Dict[str, Any], level: str = "info"):
    extra = {"structured_data": {"event": event_type, **details}}
    if level == "error":
        logger.error(f"Event: {event_type}", extra=extra)
    elif level == "warning":
        logger.warning(f"Event: {event_type}", extra=extra)
    else:
        logger.info(f"Event: {event_type}", extra=extra)
