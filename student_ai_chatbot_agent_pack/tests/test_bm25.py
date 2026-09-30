"""Tests for the self-contained BM25 lexical retriever."""

from __future__ import annotations

import numpy as np

from backend.app.retrieval.bm25 import BM25

CORPUS = [
    ["data", "structures", "credits"],
    ["attendance", "rules", "exam"],
    ["data", "credits", "credits"],
]


def test_get_scores_shape_and_type():
    bm = BM25(CORPUS)
    scores = bm.get_scores(["data", "credits"])
    assert isinstance(scores, np.ndarray)
    assert scores.shape == (3,)


def test_relevant_docs_score_higher_than_irrelevant():
    bm = BM25(CORPUS)
    scores = bm.get_scores(["data", "credits"])
    # doc 1 has neither "data" nor "credits"
    assert scores[0] > 0
    assert scores[2] > 0
    assert scores[1] == 0.0


def test_top_n_sorted_by_score_then_index():
    bm = BM25(CORPUS)
    top = bm.top_n(["data", "credits"], 3)
    assert [idx for idx, _ in top] == sorted(
        [idx for idx, _ in top], key=lambda i: (-dict(top)[i], i)
    )
    # scores are non-increasing
    vals = [s for _, s in top]
    assert vals == sorted(vals, reverse=True)


def test_top_n_caps_at_corpus_size():
    bm = BM25(CORPUS)
    assert len(bm.top_n(["data"], 99)) == 3


def test_idf_is_always_positive():
    bm = BM25(CORPUS)
    assert bm.idf  # non-empty
    assert all(v > 0 for v in bm.idf.values())


def test_unknown_query_term_contributes_zero():
    bm = BM25(CORPUS)
    scores = bm.get_scores(["nonexistentterm"])
    assert np.all(scores == 0.0)


def test_empty_corpus_returns_empty():
    bm = BM25([])
    assert bm.get_scores(["x"]).shape == (0,)
    assert bm.top_n(["x"], 5) == []


def test_deterministic():
    bm = BM25(CORPUS)
    a = bm.get_scores(["data", "credits"])
    b = bm.get_scores(["data", "credits"])
    assert np.array_equal(a, b)


def test_ties_broken_by_ascending_index():
    # two identical docs => equal scores => lower index first
    bm = BM25([["x", "y"], ["x", "y"]])
    top = bm.top_n(["x"], 2)
    assert top[0][1] == top[1][1]
    assert top[0][0] < top[1][0]
