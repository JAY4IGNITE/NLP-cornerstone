"""Integration tests: the full orchestrator pipeline with fake + real providers."""

from __future__ import annotations

IN_SCOPE = "How many credits is Data Structures?"


def test_fake_provider_answered_path(make_orchestrator, fake_provider):
    orch = make_orchestrator(fake_provider)
    out = orch.answer(IN_SCOPE)
    assert out.status == "answered"
    assert out.reason == "validated"
    assert len(out.citations) == 1
    # the fake cites the first evidence chunk; it must be a retrieved chunk
    assert out.citations[0].chunk_id in out.retrieved_chunk_ids
    assert out.provider == "fake"
    assert out.model == "fake-model-v1"


def test_fake_abstaining_provider(make_orchestrator, abstain_provider):
    orch = make_orchestrator(abstain_provider)
    out = orch.answer(IN_SCOPE)
    assert out.status == "abstained"
    assert out.reason == "provider_abstained"
    assert out.citations == []


def test_fabricated_citation_is_rejected(make_orchestrator, fabricating_provider):
    orch = make_orchestrator(fabricating_provider)
    out = orch.answer(IN_SCOPE)
    # provider claimed to answer but cited a chunk that was never retrieved
    assert out.status == "abstained"
    assert out.reason == "no_valid_citation"
    assert out.citations == []


def test_extractive_pipeline_answers_and_cites_valid_chunks(orchestrator_extractive):
    out = orchestrator_extractive.answer(IN_SCOPE)
    assert out.status == "answered"
    assert len(out.citations) >= 1
    for c in out.citations:
        assert c.chunk_id in out.retrieved_chunk_ids
    # answer should surface the grounded credit figure
    assert "4 credits" in out.answer


def test_pipeline_is_deterministic(orchestrator_extractive):
    a = orchestrator_extractive.answer(IN_SCOPE)
    b = orchestrator_extractive.answer(IN_SCOPE)
    assert a.status == b.status
    assert a.answer == b.answer
    assert a.retrieved_chunk_ids == b.retrieved_chunk_ids
    assert a.retrieval_scores == b.retrieval_scores
    assert [c.chunk_id for c in a.citations] == [c.chunk_id for c in b.citations]


def test_outcome_carries_observability_fields(orchestrator_extractive):
    out = orchestrator_extractive.answer(IN_SCOPE)
    assert out.intent_label
    assert 0.0 <= out.intent_confidence <= 1.0
    assert out.considered >= len(out.retrieved_chunk_ids)
    assert len(out.retrieval_scores) == len(out.retrieved_chunk_ids)
    assert out.provider == "extractive"
    assert out.model  # extractive model tag present
