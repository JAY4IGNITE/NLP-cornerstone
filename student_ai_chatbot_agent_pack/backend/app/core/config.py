"""Centralized configuration.

All runtime configuration is loaded here from environment variables / .env.
Invalid configuration fails fast at import/startup. Secret values are never
printed; :meth:`Settings.safe_summary` redacts them.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root = two levels up from backend/app/core/config.py
REPO_ROOT = Path(__file__).resolve().parents[3]

ProviderName = Literal["gemini", "anthropic", "extractive", "openai"]
EmbeddingMode = Literal["hash", "sentence-transformers", "auto"]

_SECRET_FIELDS = {"gemini_api_key", "anthropic_api_key", "openai_api_key", "admin_api_token", "database_url"}


class Settings(BaseSettings):
    """Typed application settings. Field names map to upper-case env vars."""

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database (optional)
    database_url: str = ""

    # Intent model
    intent_model_name: str = "distilbert-base-uncased"
    intent_max_length: int = 128
    intent_seed: int = 42
    intent_model_dir: str = "models/intent/logistic"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    embedding_mode: EmbeddingMode = "auto"

    # Retrieval
    lexical_top_k: int = 10
    dense_top_k: int = 10
    final_top_k: int = 5
    min_fused_score: float = 0.30
    min_dense_score: float = 0.0
    min_lexical_score: float = 0.0

    # LLM
    llm_provider: ProviderName = "extractive"
    gemini_model: str = "gemini-3.8-flash"
    anthropic_model: str = "claude-sonnet-4-6"
    openai_model: str = "meta/llama-3.1-8b-instruct"
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""

    # API controls
    max_query_chars: int = 2000
    request_timeout_seconds: int = 20
    admin_api_token: str = ""

    # Audit
    knowledge_base_version: str = "demo-kb-50k-v1"
    store_raw_query: bool = False

    # Paths
    index_dir: str = "artifacts/index"
    source_registry_path: str = "data/fixtures/source_registry.demo.json"

    # ---- validation (fail fast) ----
    @field_validator("intent_max_length", "embedding_dim", "max_query_chars", "request_timeout_seconds")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("lexical_top_k", "dense_top_k", "final_top_k")
    @classmethod
    def _positive_k(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("top_k values must be positive")
        return v

    @field_validator("min_fused_score", "min_dense_score", "min_lexical_score")
    @classmethod
    def _score_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("score thresholds must be within [0.0, 1.0]")
        return v

    @model_validator(mode="after")
    def _check_consistency(self) -> Settings:
        if self.final_top_k > max(self.lexical_top_k, self.dense_top_k):
            raise ValueError("FINAL_TOP_K cannot exceed the larger channel top-k")
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            # Not fatal at import: the orchestrator degrades to extractive and
            # logs a warning. We only forbid a nonsensical combination here.
            pass
        if self.app_env not in {"development", "test", "staging", "production"}:
            raise ValueError(f"unknown APP_ENV: {self.app_env!r}")
        return self

    # ---- derived helpers ----
    @property
    def use_db(self) -> bool:
        return bool(self.database_url.strip())

    @property
    def has_gemini_key(self) -> bool:
        k = self.gemini_api_key.strip()
        return bool(k) and not k.lower().startswith("your")

    @property
    def has_anthropic_key(self) -> bool:
        k = self.anthropic_api_key.strip()
        return bool(k) and not k.lower().startswith("your")

    @property
    def has_openai_key(self) -> bool:
        k = self.openai_api_key.strip()
        return bool(k) and not k.lower().startswith("your")

    def path(self, rel: str) -> Path:
        """Resolve a repo-relative path to an absolute Path."""
        p = Path(rel)
        return p if p.is_absolute() else (REPO_ROOT / p)

    def safe_summary(self) -> dict[str, object]:
        """Configuration snapshot with all secrets redacted."""
        out: dict[str, object] = {}
        for name in self.model_fields:
            value = getattr(self, name)
            if name in _SECRET_FIELDS:
                out[name] = "<set>" if str(value).strip() else "<empty>"
            else:
                out[name] = value
        out["use_db"] = self.use_db
        out["repo_root"] = str(REPO_ROOT)
        return out


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
