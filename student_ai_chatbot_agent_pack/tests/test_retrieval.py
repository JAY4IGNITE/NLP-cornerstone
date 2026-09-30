"""Tests for the hybrid retrieval service (fusion + evidence filtering)."""

from __future__ import annotations

from backend.app.retrieval.store import Chunk, LocalKnowledgeBase
from backend.app.services.retrieval import RetrievalService

IN_SCOPE = "What is the minimum attendance requirement?"


def test_in_scope_query_returns_bounded_evidence(retrieval, settings, kb):
    res = retrieval.retrieve(IN_SCOPE)
    assert res.passed_threshold is True
    assert len(res.evidence) >= 1
    assert len(res.evidence) <= settings.final_top_k
    # every returned chunk id is a real chunk in the KB
    for cid in res.chunk_ids:
        assert kb.get_chunk(cid) is not None
    assert res.considered >= len(res.evidence)


def test_scores_are_descending_and_rounded(retrieval):
    res = retrieval.retrieve(IN_SCOPE)
    assert res.scores == sorted(res.scores, reverse=True)
    for s in res.scores:
        assert 0.0 <= s <= 1.0
        assert round(s, 4) == s  # rounded to 4 decimals
    assert 0.0 <= res.top_fused_score <= 1.0


def test_all_evidence_above_fused_threshold(retrieval, settings):
    res = retrieval.retrieve(IN_SCOPE)
    for e in res.evidence:
        assert e.fused_score >= settings.min_fused_score


def test_only_approved_current_chunks_returned(retrieval):
    res = retrieval.retrieve(IN_SCOPE)
    for e in res.evidence:
        assert e.chunk.approval_status.lower() == "approved"
        assert e.chunk.is_current is True


def test_retrieval_is_deterministic(retrieval):
    a = retrieval.retrieve(IN_SCOPE)
    b = retrieval.retrieve(IN_SCOPE)
    assert a.chunk_ids == b.chunk_ids
    assert a.scores == b.scores
    assert a.top_fused_score == b.top_fused_score


def test_empty_kb_retrieval_returns_nothing(empty_kb, embedder, settings):
    svc = RetrievalService(empty_kb, embedder, settings)
    res = svc.retrieve("anything")
    assert res.evidence == []
    assert res.passed_threshold is False
    assert res.considered == 0
    assert res.top_fused_score == 0.0


def test_final_top_k_is_respected(retrieval, settings):
    # a broad query that matches many chunks still caps at final_top_k
    res = retrieval.retrieve("credits course semester exam attendance grading project")
    assert len(res.evidence) <= settings.final_top_k


def test_stale_document_version_is_filtered(embedder, settings):
    content = "attendance minimum requirement is seventy five percent for eligibility"
    old = Chunk(
        chunk_id="D1-C001", document_id="D1", document_version="v1", ordinal=1,
        heading="H", location="L", content=content, title="T",
        source_id="D1", authority="A", is_current=False,
    )
    new = Chunk(
        chunk_id="D1-C002", document_id="D1", document_version="v2", ordinal=1,
        heading="H", location="L", content=content, title="T",
        source_id="D1", authority="A", is_current=True,
    )
    kb2 = LocalKnowledgeBase.build([old, new], embedder, knowledge_base_version="stale-kb")
    res = RetrievalService(kb2, embedder, settings).retrieve("attendance minimum requirement")
    # the current version wins; the stale one is dropped
    assert "D1-C002" in res.chunk_ids
    assert "D1-C001" not in res.chunk_ids


def test_unapproved_chunks_are_filtered(embedder, settings):
    approved = Chunk(
        chunk_id="D2-C001", document_id="D2", document_version="v1", ordinal=1,
        heading="H", location="L", content="library hostel scholarship services available",
        title="T", source_id="D2", authority="A", approval_status="approved",
    )
    pending = Chunk(
        chunk_id="D3-C001", document_id="D3", document_version="v1", ordinal=1,
        heading="H", location="L", content="library hostel scholarship services available",
        title="T", source_id="D3", authority="A", approval_status="pending",
    )
    kb3 = LocalKnowledgeBase.build([approved, pending], embedder, knowledge_base_version="appr-kb")
    res = RetrievalService(kb3, embedder, settings).retrieve("library hostel scholarship services")
    assert "D3-C001" not in res.chunk_ids
