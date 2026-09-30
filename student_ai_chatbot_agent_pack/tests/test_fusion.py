"""Tests for Reciprocal Rank Fusion."""

from __future__ import annotations

import pytest

from backend.app.retrieval.fusion import FusedHit, reciprocal_rank_fusion


def test_item_top_ranked_in_both_channels_scores_one():
    dense = [("a", 0.9), ("b", 0.5)]
    lexical = [("a", 0.8), ("c", 0.4)]
    fused = reciprocal_rank_fusion(dense, lexical)
    top = fused[0]
    assert top.idx == "a"
    assert top.fused_score == pytest.approx(1.0)


def test_sorted_by_fused_score_then_idx():
    dense = [("a", 0.9), ("b", 0.5)]
    lexical = [("a", 0.8), ("c", 0.4)]
    fused = reciprocal_rank_fusion(dense, lexical)
    keys = [(-h.fused_score, h.idx) for h in fused]
    assert keys == sorted(keys)


def test_single_channel_items_present_with_none_rank():
    dense = [("a", 0.9), ("b", 0.5)]
    lexical = [("a", 0.8), ("c", 0.4)]
    fused = {h.idx: h for h in reciprocal_rank_fusion(dense, lexical)}
    # b only in dense, c only in lexical -> both present
    assert set(fused) == {"a", "b", "c"}
    assert fused["b"].lexical_rank is None
    assert fused["b"].dense_rank == 1
    assert fused["c"].dense_rank is None
    assert fused["c"].lexical_rank == 1
    # missing-channel score defaults to 0.0
    assert fused["b"].lexical_score == 0.0
    assert fused["c"].dense_score == 0.0


def test_disjoint_single_channel_ties_ordered_by_idx():
    fused = reciprocal_rank_fusion([("b", 0.9)], [("c", 0.9)])
    assert [h.idx for h in fused] == ["b", "c"]
    assert fused[0].fused_score == pytest.approx(fused[1].fused_score)


def test_scores_and_ranks_captured():
    fused = {h.idx: h for h in reciprocal_rank_fusion([("a", 0.7)], [("a", 0.6)])}
    hit = fused["a"]
    assert isinstance(hit, FusedHit)
    assert hit.dense_score == pytest.approx(0.7)
    assert hit.lexical_score == pytest.approx(0.6)
    assert hit.dense_rank == 0 and hit.lexical_rank == 0


def test_empty_inputs_return_empty():
    assert reciprocal_rank_fusion([], []) == []


def test_fused_scores_within_unit_interval():
    dense = [("a", 0.9), ("b", 0.5), ("d", 0.3)]
    lexical = [("b", 0.8), ("a", 0.4), ("e", 0.2)]
    for h in reciprocal_rank_fusion(dense, lexical):
        assert 0.0 < h.fused_score <= 1.0 + 1e-9


def test_deterministic():
    dense = [("a", 0.9), ("b", 0.5)]
    lexical = [("a", 0.8), ("c", 0.4)]
    r1 = reciprocal_rank_fusion(dense, lexical)
    r2 = reciprocal_rank_fusion(dense, lexical)
    assert [(h.idx, h.fused_score) for h in r1] == [(h.idx, h.fused_score) for h in r2]
