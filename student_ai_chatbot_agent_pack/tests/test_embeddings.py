"""Tests for deterministic hash-mode embeddings.

These never touch the network or optional ML deps: hash mode is explicit.
"""

from __future__ import annotations

import numpy as np

from backend.app.retrieval.embeddings import EmbeddingModel

DIM = 384


def _model() -> EmbeddingModel:
    return EmbeddingModel("sentence-transformers/all-MiniLM-L6-v2", DIM, "hash")


def test_hash_mode_and_dim():
    m = _model()
    assert m.mode == "hash"
    assert m.dim == DIM


def test_embed_shape_and_l2_normalization():
    m = _model()
    mat = m.embed(["data structures course", "attendance grading rules"])
    assert mat.shape == (2, DIM)
    norms = np.linalg.norm(mat, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_embed_empty_returns_zero_by_dim():
    m = _model()
    out = m.embed([])
    assert out.shape == (0, DIM)


def test_embed_one_returns_1d_vector():
    m = _model()
    v = m.embed_one("hello world")
    assert v.shape == (DIM,)


def test_determinism_across_calls_and_instances():
    a = _model().embed(["deterministic text here"])
    b = _model().embed(["deterministic text here"])
    assert np.array_equal(a, b)


def test_distinct_texts_produce_distinct_vectors():
    m = _model()
    v1 = m.embed_one("data structures and algorithms")
    v2 = m.embed_one("hostel scholarship library services")
    assert not np.array_equal(v1, v2)


def test_text_without_tokens_is_zero_vector():
    m = _model()
    v = m.embed_one("!!! ???")
    assert v.shape == (DIM,)
    assert float(np.linalg.norm(v)) == 0.0
