"""LLM provider abstraction (ARCHITECTURE.md §LLM, MODEL_PLAN.md §6).

Providers never become the source of truth: they receive only approved evidence
and must answer from it or abstain. A provider returns which evidence chunk ids
it used, so the citation validator can verify them against what was actually
retrieved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class EvidenceItem:
    chunk_id: str
    document_id: str
    title: str
    location: str
    text: str


@dataclass
class GroundedRequest:
    question: str
    intent: str
    evidence: list[EvidenceItem]


@dataclass
class GroundedAnswer:
    status: str  # "answered" | "abstained"
    answer: str
    cited_chunk_ids: list[str] = field(default_factory=list)
    provider: str = ""
    model: str = ""


ABSTENTION_MESSAGE = (
    "I don't have enough verified information in the college knowledge base to "
    "answer that accurately. Please share or check the official college source for this detail."
)


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    @property
    def available(self) -> bool: ...

    def generate_grounded(self, request: GroundedRequest) -> GroundedAnswer: ...
