"""Shared pytest fixtures for the Student AI Chatbot test suite.

Everything here is engineered to run **fully offline and deterministically**:

* Optional ML/network backends are force-disabled. ``sentence-transformers`` and
  ``torch`` happen to be importable in some environments (and would hit the
  network to download MiniLM), so we pin ``EMBEDDING_MODE=hash`` and set the HF
  offline flags before importing any ``backend`` module.
* ``INDEX_DIR`` is pointed at a fresh empty temp dir so ``build_state`` cannot
  load a persisted (sentence-transformers-built) index and instead rebuilds the
  knowledge base in-memory with deterministic hash embeddings.

These env vars must be set *before* ``backend.app`` is imported, because
``backend.app.main`` builds the FastAPI ``app`` (and reads settings) at import.
"""

from __future__ import annotations

import os
import tempfile

# ---- offline / determinism guards (must precede any backend import) ----
os.environ["EMBEDDING_MODE"] = "hash"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# A brand-new empty directory => LocalKnowledgeBase.load() raises FileNotFoundError
# => runtime falls back to an in-memory build with the hash embedder.
os.environ["INDEX_DIR"] = tempfile.mkdtemp(prefix="sacb_test_index_")
os.environ["LLM_PROVIDER"] = "extractive"
os.environ["SOURCE_REGISTRY_PATH"] = "data/fixtures/source_registry.demo.json"
os.environ["KNOWLEDGE_BASE_VERSION"] = "demo-kb-50k-v1"

import numpy as np
import pytest

from backend.app.core.config import Settings, get_settings
from backend.app.ingestion.pipeline import ingest_sources
from backend.app.llm.base import GroundedAnswer, GroundedRequest
from backend.app.llm.extractive import ExtractiveProvider
from backend.app.retrieval.embeddings import EmbeddingModel
from backend.app.retrieval.store import LocalKnowledgeBase
from backend.app.services.citation import CitationValidator
from backend.app.services.intent import IntentClassifier
from backend.app.services.orchestrator import Orchestrator
from backend.app.services.retrieval import RetrievalService

TEST_KB_VERSION = "test-kb"


# --------------------------------------------------------------------------- #
# Deterministic fake providers (module-level so tests can request the classes) #
# --------------------------------------------------------------------------- #
class FakeProvider:
    """Deterministic 'answered' provider: cites the first evidence chunk."""

    name = "fake"
    model = "fake-model-v1"

    @property
    def available(self) -> bool:
        return True

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer:
        cid = request.evidence[0].chunk_id
        return GroundedAnswer("answered", f"Grounded answer citing {cid}.", [cid], self.name, self.model)


class FakeAbstainProvider:
    """Provider that always abstains."""

    name = "fake"
    model = "fake-model-v1"

    @property
    def available(self) -> bool:
        return True

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer:
        return GroundedAnswer("abstained", "", [], self.name, self.model)


class FabricatingProvider:
    """Malicious provider: claims to answer while citing a fabricated chunk id."""

    name = "fake"
    model = "fake-model-v1"

    @property
    def available(self) -> bool:
        return True

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer:
        return GroundedAnswer("answered", "totally made up", ["FABRICATED-C999"], self.name, self.model)


# --------------------------------------------------------------------------- #
# Core fixtures                                                                #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def embedder(settings: Settings) -> EmbeddingModel:
    # Explicit hash mode: deterministic, offline, no optional deps.
    return EmbeddingModel(settings.embedding_model, settings.embedding_dim, "hash")


@pytest.fixture(scope="session")
def ingested(settings: Settings):
    """(chunks, manifest) from the demo source registry."""
    return ingest_sources(settings)


@pytest.fixture(scope="session")
def chunks(ingested):
    return ingested[0]


@pytest.fixture(scope="session")
def kb(chunks, embedder) -> LocalKnowledgeBase:
    return LocalKnowledgeBase.build(chunks, embedder, knowledge_base_version=TEST_KB_VERSION)


@pytest.fixture(scope="session")
def empty_kb(embedder) -> LocalKnowledgeBase:
    return LocalKnowledgeBase.build([], embedder, knowledge_base_version="empty-kb")


@pytest.fixture(scope="session")
def retrieval(kb, embedder, settings) -> RetrievalService:
    return RetrievalService(kb, embedder, settings)


@pytest.fixture(scope="session")
def intent_classifier() -> IntentClassifier:
    # model_dir=None => deterministic lexical fallback (no torch/transformers).
    return IntentClassifier(None)


@pytest.fixture(scope="session")
def extractive_provider() -> ExtractiveProvider:
    return ExtractiveProvider()


@pytest.fixture
def validator() -> CitationValidator:
    return CitationValidator()


@pytest.fixture(scope="session")
def orchestrator_extractive(retrieval) -> Orchestrator:
    return Orchestrator(IntentClassifier(None), retrieval, ExtractiveProvider(), CitationValidator())


@pytest.fixture
def make_orchestrator(retrieval):
    """Factory: build an Orchestrator wired to a given provider (shared retrieval)."""

    def _make(provider) -> Orchestrator:
        return Orchestrator(IntentClassifier(None), retrieval, provider, CitationValidator())

    return _make


@pytest.fixture
def empty_orchestrator(empty_kb, embedder, settings) -> Orchestrator:
    retr = RetrievalService(empty_kb, embedder, settings)
    return Orchestrator(IntentClassifier(None), retr, ExtractiveProvider(), CitationValidator())


@pytest.fixture
def fake_provider() -> FakeProvider:
    return FakeProvider()


@pytest.fixture
def abstain_provider() -> FakeAbstainProvider:
    return FakeAbstainProvider()


@pytest.fixture
def fabricating_provider() -> FabricatingProvider:
    return FabricatingProvider()


@pytest.fixture(scope="session")
def api_client():
    """FastAPI TestClient with the app lifespan run (builds the pipeline once).

    Imported lazily so the offline env vars set at module top are in force before
    ``backend.app.main`` creates the app / reads settings.
    """
    from fastapi.testclient import TestClient

    from backend.app.main import app

    with TestClient(app) as client:
        yield client


# Expose numpy helper for tests that need array equality without re-importing.
@pytest.fixture(scope="session")
def np_module():
    return np
