"""OpenAI-compatible grounded provider (optional, MODEL_PLAN.md §6).

Uses the ``openai`` SDK when installed and an API key is configured. The
model receives the grounded prompt as the user turn and the grounding rules as
the system prompt; it must answer only from the evidence or abstain. Any
SDK/network/parse failure degrades to a safe abstention — never a fabrication.
"""

from __future__ import annotations

from backend.app.core.logging import get_logger
from backend.app.llm._remote import _abstain, interpret_response
from backend.app.llm.base import GroundedAnswer, GroundedRequest
from backend.app.llm.prompt import SYSTEM_RULES, build_prompt

_log = get_logger("llm.openai")

_MAX_TOKENS = 1024


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str, *, base_url: str | None = None, timeout: int = 20) -> None:
        self._api_key = api_key or ""
        self.model = model
        self._base_url = base_url
        self._timeout = timeout
        self._client = None

    @property
    def available(self) -> bool:
        if not self._api_key:
            return False
        try:
            import openai  # noqa: F401
        except ImportError:
            return False
        return True

    def _get_client(self):
        if self._client is None:
            import openai
            from httpx import Timeout

            self._client = openai.OpenAI(
                api_key=self._api_key, 
                base_url=self._base_url,
                timeout=Timeout(self._timeout)
            )
        return self._client

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer:
        if not self.available:
            return _abstain(self.name, self.model)
        prompt = build_prompt(request)
        try:
            client = self._get_client()
            msg = client.chat.completions.create(
                model=self.model,
                max_tokens=_MAX_TOKENS,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": SYSTEM_RULES},
                    {"role": "user", "content": prompt}
                ],
            )
            raw = msg.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001 — degrade to abstention on any failure
            _log.warning("openai_call_failed", extra={"error_category": type(exc).__name__})
            return _abstain(self.name, self.model)

        return interpret_response(request, raw, self.name, self.model)
