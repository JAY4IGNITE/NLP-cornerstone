"""Query normalization and input validation.

Conservative, deterministic normalization only (DETAILS.md §4): Unicode (NFKC),
whitespace, punctuation shape. We do NOT lower-case (course codes like "CSE301"
are case-bearing) and we do NOT expand abbreviations, because that could alter
academic meaning.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_WS = re.compile(r"\s+")
# Map typographic punctuation to ASCII equivalents (shape only, not meaning).
_PUNCT_MAP = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "−": "-", "…": "...",
    " ": " ",
}


class QueryValidationError(ValueError):
    """Raised when a query is empty or exceeds the configured length."""


@dataclass(frozen=True)
class NormalizedQuery:
    raw: str
    normalized: str
    char_len: int


def normalize_query(text: str) -> NormalizedQuery:
    if text is None:  # defensive; schema should prevent this
        raise QueryValidationError("query must not be null")
    raw = text
    s = unicodedata.normalize("NFKC", text)
    s = "".join(_PUNCT_MAP.get(ch, ch) for ch in s)
    # Drop control characters (except normal whitespace which we collapse next).
    s = "".join(ch for ch in s if ch == " " or unicodedata.category(ch)[0] != "C")
    s = _WS.sub(" ", s).strip()
    return NormalizedQuery(raw=raw, normalized=s, char_len=len(s))


def validate_query(text: str, *, max_chars: int) -> NormalizedQuery:
    """Normalize and enforce non-empty + length bounds. Raises on violation."""
    nq = normalize_query(text)
    if not nq.normalized:
        raise QueryValidationError("query must not be empty")
    if nq.char_len > max_chars:
        raise QueryValidationError(f"query exceeds {max_chars} characters")
    return nq


def tokenize(text: str) -> list[str]:
    """Lower-cased alphanumeric tokenization used by lexical retrieval / fallback
    intent features. Keeps digits attached to letters (course codes)."""
    return re.findall(r"[a-z0-9]+", text.lower())
