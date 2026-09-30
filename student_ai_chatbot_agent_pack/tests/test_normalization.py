"""Tests for query normalization, validation, and tokenization."""

from __future__ import annotations

import pytest

from backend.app.core.normalization import (
    NormalizedQuery,
    QueryValidationError,
    normalize_query,
    tokenize,
    validate_query,
)


def test_normalize_returns_dataclass_with_raw_preserved():
    nq = normalize_query("  Hello  ")
    assert isinstance(nq, NormalizedQuery)
    assert nq.raw == "  Hello  "
    assert nq.normalized == "Hello"
    assert nq.char_len == len(nq.normalized)


def test_typographic_punctuation_mapped_to_ascii():
    nq = normalize_query("“Smart” quotes — dash …")
    # curly quotes -> straight, em-dash -> hyphen, ellipsis -> ...
    assert nq.normalized == '"Smart" quotes - dash ...'


def test_collapses_whitespace_and_strips():
    assert normalize_query("hello   world  ").normalized == "hello world"
    # tabs / newlines are control chars: stripped, not turned into spaces
    assert normalize_query("a\tb\nc").normalized == "abc"


def test_strips_control_characters():
    assert normalize_query("a\x00b\x07c").normalized == "abc"


def test_nfkc_normalization():
    # Fullwidth Latin letters normalize to ASCII under NFKC.
    assert normalize_query("ＡＢ").normalized == "AB"


def test_does_not_lowercase_case_bearing_text():
    # Course codes are case-bearing; normalization must preserve case.
    assert normalize_query("Hello WORLD CSE301").normalized == "Hello WORLD CSE301"


def test_validate_query_rejects_empty_and_whitespace():
    with pytest.raises(QueryValidationError):
        validate_query("", max_chars=100)
    with pytest.raises(QueryValidationError):
        validate_query("     ", max_chars=100)


def test_validate_query_rejects_too_long():
    with pytest.raises(QueryValidationError):
        validate_query("abcdef", max_chars=3)


def test_validate_query_accepts_valid_within_bounds():
    nq = validate_query("How many credits?", max_chars=100)
    assert nq.normalized == "How many credits?"
    assert 0 < nq.char_len <= 100


def test_tokenize_lowercases_and_keeps_digits_in_codes():
    assert tokenize("CS201") == ["cs201"]
    assert tokenize("Hello, World! CS-201") == ["hello", "world", "cs", "201"]


def test_tokenize_empty_on_no_alphanumerics():
    assert tokenize("!!! ??? ---") == []
