"""Shared helpers for remote (API-backed) grounded providers.

A remote model is never trusted as a source of truth. Whatever it returns is
run back through these helpers, which:

- parse the strict JSON contract,
- drop any cited chunk id the model did not actually receive (anti-fabrication),
- fail **closed** to a safe abstention on any error, empty answer, or answer
  that ends up with no valid citation.

The authoritative citation check still runs later in CitationValidator; this is
defense in depth at the provider boundary.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger
from backend.app.llm.base import ABSTENTION_MESSAGE, GroundedAnswer, GroundedRequest
from backend.app.llm.prompt import parse_provider_json

_log = get_logger("llm.remote")


def _abstain(provider: str, model: str) -> GroundedAnswer:
    return GroundedAnswer("abstained", ABSTENTION_MESSAGE, [], provider, model)


def interpret_response(
    request: GroundedRequest, raw_text: str, provider: str, model: str
) -> GroundedAnswer:
    """Turn a raw model response into a validated GroundedAnswer, failing closed."""
    allowed = {e.chunk_id for e in request.evidence}
    try:
        parsed = parse_provider_json(raw_text)
    except (ValueError, TypeError):
        _log.warning("provider_json_parse_failed", extra={"provider": provider})
        return _abstain(provider, model)

    status = str(parsed.get("status", "")).strip().lower()
    answer = str(parsed.get("answer", "")).strip()
    raw_ids = parsed.get("cited_chunk_ids", []) or []
    if not isinstance(raw_ids, list):
        raw_ids = []

    # Keep only citations to evidence that was actually retrieved, in order.
    cited: list[str] = []
    for cid in raw_ids:
        cid = str(cid)
        if cid in allowed and cid not in cited:
            cited.append(cid)

    # Fail closed: abstain unless we have a real answer backed by a real citation.
    if status != "answered" or not answer or not cited:
        return _abstain(provider, model)

    return GroundedAnswer("answered", answer, cited, provider, model)
