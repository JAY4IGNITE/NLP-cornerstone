"""Hybrid retrieval service (RAG.md §5–§7).

query -> dense top-k + lexical top-k -> RRF fusion -> evidence filter
(approval / currency / score thresholds) -> final top-k evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.core.config import Settings
from backend.app.retrieval.embeddings import EmbeddingModel
from backend.app.retrieval.fusion import reciprocal_rank_fusion
from backend.app.retrieval.store import Chunk, LocalKnowledgeBase


@dataclass
class Evidence:
    chunk: Chunk
    fused_score: float
    dense_score: float
    lexical_score: float


@dataclass
class RetrievalResult:
    evidence: list[Evidence]
    considered: int
    top_fused_score: float
    passed_threshold: bool

    @property
    def chunk_ids(self) -> list[str]:
        return [e.chunk.chunk_id for e in self.evidence]

    @property
    def scores(self) -> list[float]:
        return [round(e.fused_score, 4) for e in self.evidence]


class RetrievalService:
    def __init__(
        self, kb: LocalKnowledgeBase, embedder: EmbeddingModel, settings: Settings
    ) -> None:
        self.kb = kb
        self.embedder = embedder
        self.s = settings

    def _filter_evidence(self, hits) -> list[Evidence]:
        # Determine current version per document to drop stale duplicates.
        current_versions: dict[str, str] = {}
        for h in hits:
            c = self.kb.get_chunk(h.idx)
            if c and c.is_current:
                current_versions[c.document_id] = c.document_version

        evidence: list[Evidence] = []
        for h in hits:
            chunk = self.kb.get_chunk(h.idx)
            if chunk is None:
                continue
            if chunk.approval_status.lower() != "approved":
                continue
            cur = current_versions.get(chunk.document_id)
            if cur is not None and chunk.document_version != cur:
                continue  # stale version, a newer one is present
            if h.fused_score < self.s.min_fused_score:
                continue
            if h.dense_score < self.s.min_dense_score:
                continue
            if h.lexical_score < self.s.min_lexical_score:
                continue
            evidence.append(
                Evidence(
                    chunk=chunk,
                    fused_score=h.fused_score,
                    dense_score=h.dense_score,
                    lexical_score=h.lexical_score,
                )
            )
        return evidence

    def retrieve(self, query: str) -> RetrievalResult:
        if self.kb.size == 0:
            return RetrievalResult([], 0, 0.0, False)
        qvec = self.embedder.embed_one(query)
        dense = self.kb.search_dense(qvec, self.s.dense_top_k)
        lexical = self.kb.search_lexical(query, self.s.lexical_top_k)
        fused = reciprocal_rank_fusion(dense, lexical)
        top_fused = fused[0].fused_score if fused else 0.0
        evidence = self._filter_evidence(fused)[: self.s.final_top_k]
        return RetrievalResult(
            evidence=evidence,
            considered=len(fused),
            top_fused_score=round(top_fused, 4),
            passed_threshold=bool(evidence),
        )
