"""Provider selection (ARCHITECTURE.md §LLM).

Chooses the configured grounded provider and *always* returns something usable:
if the requested remote provider is unavailable (no key, SDK missing) it falls
back to the deterministic extractive provider so the pipeline runs offline with
zero configuration. The choice never affects grounding — every provider answers
only from supplied evidence or abstains.
"""

from __future__ import annotations

from backend.app.core.config import Settings
from backend.app.core.logging import get_logger
from backend.app.llm.anthropic import AnthropicProvider
from backend.app.llm.base import LLMProvider
from backend.app.llm.extractive import ExtractiveProvider
from backend.app.llm.gemini import GeminiProvider
from backend.app.llm.openai import OpenAIProvider

_log = get_logger("llm.factory")


def build_provider(settings: Settings) -> LLMProvider:
    choice = (settings.llm_provider or "extractive").strip().lower()

    if choice == "gemini" and settings.has_gemini_key:
        provider = GeminiProvider(
            settings.gemini_api_key,
            settings.gemini_model,
            timeout=settings.request_timeout_seconds,
        )
        if provider.available:
            return provider
        _log.warning("provider_unavailable_fallback", extra={"provider": "gemini"})

    elif choice == "anthropic" and settings.has_anthropic_key:
        provider = AnthropicProvider(
            settings.anthropic_api_key,
            settings.anthropic_model,
            timeout=settings.request_timeout_seconds,
        )
        if provider.available:
            return provider
        _log.warning("provider_unavailable_fallback", extra={"provider": "anthropic"})

    elif choice == "openai" and settings.has_openai_key:
        provider = OpenAIProvider(
            settings.openai_api_key,
            settings.openai_model,
            base_url=settings.openai_base_url or None,
            timeout=settings.request_timeout_seconds,
        )
        if provider.available:
            return provider
        _log.warning("provider_unavailable_fallback", extra={"provider": "openai"})

    elif choice in {"gemini", "anthropic", "openai"}:
        _log.warning("provider_no_key_fallback", extra={"provider": choice})

    # Default and universal fallback: deterministic, offline, cannot fabricate.
    return ExtractiveProvider()
