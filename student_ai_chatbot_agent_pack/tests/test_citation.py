"""Tests for the citation validator — the final anti-hallucination gate."""

from __future__ import annotations

from backend.app.llm.base import ABSTENTION_MESSAGE, GroundedAnswer
from backend.app.services.citation import CitationValidator


def test_valid_citations_pass_and_invalid_are_dropped():
    v = CitationValidator()
    ans = GroundedAnswer("answered", "the answer", ["c1", "c99"], "p", "m")
    d = v.validate(ans, retrieved_chunk_ids=["c1", "c2"])
    assert d.status == "answered"
    assert d.ok is True
    assert d.valid_chunk_ids == ["c1"]
    assert d.dropped_chunk_ids == ["c99"]
    assert d.reason == "validated"
    assert d.answer == "the answer"


def test_answered_with_no_retrieved_citation_abstains():
    v = CitationValidator()
    ans = GroundedAnswer("answered", "the answer", ["c99"], "p", "m")
    d = v.validate(ans, retrieved_chunk_ids=["c1", "c2"])
    assert d.status == "abstained"
    assert d.ok is False
    assert d.reason == "no_valid_citation"
    assert d.valid_chunk_ids == []
    assert d.answer == ABSTENTION_MESSAGE


def test_provider_abstention_is_preserved():
    v = CitationValidator()
    ans = GroundedAnswer("abstained", "whatever", [], "p", "m")
    d = v.validate(ans, retrieved_chunk_ids=["c1"])
    assert d.status == "abstained"
    assert d.reason == "provider_abstained"
    assert d.answer == ABSTENTION_MESSAGE


def test_empty_answer_with_valid_citation_abstains():
    v = CitationValidator()
    ans = GroundedAnswer("answered", "   ", ["c1"], "p", "m")
    d = v.validate(ans, retrieved_chunk_ids=["c1"])
    assert d.status == "abstained"
    assert d.reason == "empty_answer"


def test_duplicate_citations_are_deduplicated():
    v = CitationValidator()
    ans = GroundedAnswer("answered", "the answer", ["c1", "c1"], "p", "m")
    d = v.validate(ans, retrieved_chunk_ids=["c1"])
    assert d.valid_chunk_ids == ["c1"]
    assert d.ok is True


def test_all_valid_citations_must_be_subset_of_retrieved():
    v = CitationValidator()
    ans = GroundedAnswer("answered", "a", ["c1", "c2", "c3"], "p", "m")
    d = v.validate(ans, retrieved_chunk_ids=["c2"])
    assert set(d.valid_chunk_ids).issubset({"c2"})
    assert d.valid_chunk_ids == ["c2"]
    assert set(d.dropped_chunk_ids) == {"c1", "c3"}
