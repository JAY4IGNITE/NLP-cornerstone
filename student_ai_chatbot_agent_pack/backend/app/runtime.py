"""Application runtime state (ARCHITECTURE.md §Runtime).

Assembles the whole pipeline once at startup and hands it to the routers:

    settings -> embedder -> knowledge base (load persisted index, else build
    in-memory from approved sources) -> intent classifier -> retrieval service
    -> grounded provider -> orchestrator.

Building in-memory when no persisted index exists keeps the service runnable
out of the box (offline, zero setup); a persisted index is preferred in
production and is produced by scripts/build_index.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.core.config import Settings
from backend.app.core.logging import get_logger
from backend.app.ingestion.pipeline import ingest_sources
from backend.app.llm.base import LLMProvider
from backend.app.llm.factory import build_provider
from backend.app.retrieval.embeddings import EmbeddingModel
from backend.app.retrieval.store import LocalKnowledgeBase
from backend.app.services.citation import CitationValidator
from backend.app.services.intent import IntentClassifier
from backend.app.services.orchestrator import Orchestrator
from backend.app.services.retrieval import RetrievalService

logger = get_logger("runtime")


@dataclass
class AppState:
    settings: Settings
    embedder: EmbeddingModel
    kb: LocalKnowledgeBase
    intent: IntentClassifier
    retrieval: RetrievalService
    provider: LLMProvider
    orchestrator: Orchestrator
    index_source: str  # "persisted" | "in-memory"

    @property
    def index_ready(self) -> bool:
        return self.kb.size > 0


def _load_kb(settings: Settings, embedder: EmbeddingModel) -> tuple[LocalKnowledgeBase, str]:
    index_dir = settings.path(settings.index_dir)
    try:
        kb = LocalKnowledgeBase.load(index_dir)
        logger.info("loaded persisted index from %s (%d chunks)", index_dir, kb.size)
        return kb, "persisted"
    except FileNotFoundError:
        logger.info("no persisted index; building in-memory from approved sources")
    chunks, _manifest = ingest_sources(settings)
    kb = LocalKnowledgeBase.build(
        chunks, embedder, knowledge_base_version=settings.knowledge_base_version
    )
    return kb, "in-memory"


def build_state(settings: Settings) -> AppState:
    embedder = EmbeddingModel(settings.embedding_model, settings.embedding_dim, settings.embedding_mode)
    kb, index_source = _load_kb(settings, embedder)

    model_dir = settings.path(settings.intent_model_dir)
    intent = IntentClassifier(
        str(model_dir) if (model_dir / "model.joblib").exists() else None,
        settings.intent_max_length,
    )
    retrieval = RetrievalService(kb, embedder, settings)
    provider = build_provider(settings)
    orchestrator = Orchestrator(intent, retrieval, provider, CitationValidator())

    logger.info(
        "runtime ready: kb=%d source=%s intent=%s provider=%s",
        kb.size, index_source, intent.backend, provider.name,
    )
    return AppState(
        settings=settings,
        embedder=embedder,
        kb=kb,
        intent=intent,
        retrieval=retrieval,
        provider=provider,
        orchestrator=orchestrator,
        index_source=index_source,
    )
