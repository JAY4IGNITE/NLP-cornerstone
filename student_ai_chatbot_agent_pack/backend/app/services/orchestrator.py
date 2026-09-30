"""Answer orchestration (ARCHITECTURE.md §Flow, RAG.md §9).

The single place the full request pipeline lives:

    validate -> normalize -> classify intent -> retrieve evidence
        -> ground a provider on that evidence -> validate citations
        -> answer with citations, or abstain.

Grounding and citation validation are non-negotiable gates: the student only
ever sees a claim that came from retrieved, approved evidence, or a safe
abstention. The orchestrator returns plain data; the API layer shapes it into
the response schema and assigns the trace id.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.core.normalization import normalize_query
from backend.app.llm.base import (
    ABSTENTION_MESSAGE,
    EvidenceItem,
    GroundedRequest,
    LLMProvider,
)
from backend.app.services.citation import CitationValidator
from backend.app.services.intent import IntentClassifier
from backend.app.services.retrieval import RetrievalService
from backend.app.services.safety import is_private_record_query


@dataclass
class CitedSource:
    document_id: str
    title: str
    location: str
    chunk_id: str
    content: str = ""


@dataclass
class PipelineOutcome:
    status: str  # "answered" | "abstained"
    answer: str
    citations: list[CitedSource] = field(default_factory=list)
    intent_label: str = ""
    intent_confidence: float = 0.0
    provider: str = ""
    model: str = ""
    # audit / observability
    retrieved_chunk_ids: list[str] = field(default_factory=list)
    retrieval_scores: list[float] = field(default_factory=list)
    considered: int = 0
    top_fused_score: float = 0.0
    reason: str = ""


class Orchestrator:
    def __init__(
        self,
        intent: IntentClassifier,
        retrieval: RetrievalService,
        provider: LLMProvider,
        validator: CitationValidator | None = None,
    ) -> None:
        self.intent = intent
        self.retrieval = retrieval
        self.provider = provider
        self.validator = validator or CitationValidator()

    def answer(self, raw_query: str) -> PipelineOutcome:
        normalized = normalize_query(raw_query).normalized

        prediction = self.intent.predict_intent(normalized)

        # Safety/scope gate: a request for a specific person's private record is
        # refused up front — it is not in the (public) knowledge base and must
        # never be answered from unrelated policy text.
        if is_private_record_query(normalized):
            return PipelineOutcome(
                status="abstained",
                answer=ABSTENTION_MESSAGE,
                intent_label=prediction.label,
                intent_confidence=round(prediction.confidence, 4),
                provider=self.provider.name,
                model=getattr(self.provider, "model", ""),
                reason="private_record",
            )

        result = self.retrieval.retrieve(normalized)

        base = PipelineOutcome(
            status="abstained",
            answer="",
            intent_label=prediction.label,
            intent_confidence=round(prediction.confidence, 4),
            provider=self.provider.name,
            model=getattr(self.provider, "model", ""),
            retrieved_chunk_ids=result.chunk_ids,
            retrieval_scores=result.scores,
            considered=result.considered,
            top_fused_score=result.top_fused_score,
        )

        # No evidence cleared the thresholds -> abstain without calling a provider.
        if not result.evidence:
            base.reason = "no_evidence"
            base.answer = ABSTENTION_MESSAGE
            return base

        grounded_request = GroundedRequest(
            question=normalized,
            intent=prediction.label,
            evidence=[
                EvidenceItem(
                    chunk_id=e.chunk.chunk_id,
                    document_id=e.chunk.document_id,
                    title=e.chunk.title,
                    location=e.chunk.location,
                    text=e.chunk.content,
                )
                for e in result.evidence
            ],
        )

        generated = self.provider.generate_grounded(grounded_request)
        decision = self.validator.validate(generated, result.chunk_ids)

        base.status = decision.status
        base.answer = decision.answer
        base.reason = decision.reason
        base.provider = generated.provider or self.provider.name
        base.model = generated.model or base.model

        if decision.ok:
            by_id = {e.chunk.chunk_id: e.chunk for e in result.evidence}
            citations: list[CitedSource] = []
            for cid in decision.valid_chunk_ids:
                chunk = by_id.get(cid)
                if chunk is None:
                    continue
                citations.append(
                    CitedSource(
                        document_id=chunk.document_id,
                        title=chunk.title,
                        location=chunk.location,
                        chunk_id=chunk.chunk_id,
                        content=chunk.content,
                    )
                )
            base.citations = citations

        return base
