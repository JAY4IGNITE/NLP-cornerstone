"""Tests for Settings configuration: defaults, validators, secret redaction."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.core.config import Settings, get_settings


def test_documented_defaults():
    s = Settings()
    assert s.min_fused_score == 0.30
    assert s.final_top_k == 5
    assert s.embedding_dim == 384
    assert s.llm_provider == "extractive"
    assert s.lexical_top_k == 10
    assert s.dense_top_k == 10
    assert s.max_query_chars == 2000


def test_positive_int_validators_reject_non_positive():
    with pytest.raises(ValidationError):
        Settings(embedding_dim=0)
    with pytest.raises(ValidationError):
        Settings(intent_max_length=-1)
    with pytest.raises(ValidationError):
        Settings(max_query_chars=0)
    with pytest.raises(ValidationError):
        Settings(request_timeout_seconds=0)


def test_positive_top_k_validators():
    with pytest.raises(ValidationError):
        Settings(final_top_k=0)
    with pytest.raises(ValidationError):
        Settings(lexical_top_k=-2)


@pytest.mark.parametrize("bad", [-0.01, 1.01, 2.0])
def test_score_thresholds_must_be_in_unit_interval(bad):
    with pytest.raises(ValidationError):
        Settings(min_fused_score=bad)


def test_score_threshold_boundaries_ok():
    assert Settings(min_fused_score=0.0).min_fused_score == 0.0
    assert Settings(min_fused_score=1.0).min_fused_score == 1.0


def test_final_top_k_cannot_exceed_larger_channel():
    with pytest.raises(ValidationError):
        Settings(final_top_k=100, lexical_top_k=10, dense_top_k=10)
    # ok when within the larger channel
    s = Settings(final_top_k=10, lexical_top_k=10, dense_top_k=5)
    assert s.final_top_k == 10


def test_unknown_app_env_raises():
    with pytest.raises(ValidationError):
        Settings(app_env="bogus-env")
    # known values are accepted
    assert Settings(app_env="production").app_env == "production"


def test_safe_summary_redacts_secrets():
    s = Settings(
        admin_api_token="super-secret",
        database_url="postgres://user:pw@host/db",
        gemini_api_key="",
        anthropic_api_key="real-anthropic-key",
    )
    summary = s.safe_summary()
    assert summary["admin_api_token"] == "<set>"
    assert summary["database_url"] == "<set>"
    assert summary["anthropic_api_key"] == "<set>"
    assert summary["gemini_api_key"] == "<empty>"
    # non-secret fields keep their real values
    assert summary["final_top_k"] == s.final_top_k
    assert summary["llm_provider"] == "extractive"
    # never leaks the raw secret value
    assert "super-secret" not in str(summary.values())


def test_has_provider_key_semantics():
    assert Settings(gemini_api_key="").has_gemini_key is False
    assert Settings(gemini_api_key="your-key-here").has_gemini_key is False
    assert Settings(gemini_api_key="AIzaRealLookingKey").has_gemini_key is True
    assert Settings(anthropic_api_key="").has_anthropic_key is False
    assert Settings(anthropic_api_key="YOUR-TOKEN").has_anthropic_key is False
    assert Settings(anthropic_api_key="sk-ant-real").has_anthropic_key is True


def test_get_settings_is_cached_singleton():
    assert get_settings() is get_settings()
