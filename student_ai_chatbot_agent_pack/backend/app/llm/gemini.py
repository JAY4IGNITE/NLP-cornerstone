"""Gemini grounded provider (optional, MODEL_PLAN.md §6).

Uses the ``google-genai`` SDK when installed and an API key is configured.
The model receives only the grounded prompt (evidence wrapped in <EVIDENCE>
delimiters) and must answer from it or abstain. Any SDK/network/parse failure
degrades to a safe abstention — the provider never fabricates on error.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger
from backend.app.llm._remote import _abstain, interpret_response
from backend.app.llm.base import GroundedAnswer, GroundedRequest
from backend.app.llm.prompt import build_prompt

_log = get_logger("llm.gemini")


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str, *, timeout: int = 20) -> None:
        self._api_key = api_key or ""
        self.model = model
        self._timeout = timeout
        self._client = None

    @property
    def available(self) -> bool:
        if not self._api_key:
            return False
        try:
            import google.genai  # noqa: F401
        except ImportError:
            return False
        return True

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer:
        if not self.available:
            return _abstain(self.name, self.model)
        prompt = build_prompt(request)
        try:
            from google.genai import types

            client = self._get_client()
            resp = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    http_options=types.HttpOptions(timeout=self._timeout * 1000),
                ),
            )
            raw = getattr(resp, "text", None) or ""
        except Exception as exc:  # noqa: BLE001 — degrade to abstention on any failure
            _log.warning("gemini_call_failed", extra={"error_category": type(exc).__name__})
            return _abstain(self.name, self.model)

        return interpret_response(request, raw, self.name, self.model)
