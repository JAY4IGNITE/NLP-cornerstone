"""Source Attribution and Groundedness Evaluation Engine.
Computes multi-factor RAG confidence scores and verifies factual citations.
"""
import re
from typing import List, Dict, Any, Optional

class AttributionEngine:
    def __init__(self, retrieval_threshold: float = 0.40, rerank_threshold: float = 0.40):
        self.retrieval_threshold = retrieval_threshold
        self.rerank_threshold = rerank_threshold

    def calculate_confidence(
        self,
        query: str,
        answer: str,
        intent_data: Dict[str, Any],
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute groundedness and attribution breakdown."""
        intent = intent_data.get("intent", "fallback")
        intent_conf = intent_data.get("confidence", 0.0)

        # Conversational intents do not require PDF retrieval
        if intent in {"greeting", "thanks", "help"}:
            return {
                "overall_confidence": round(intent_conf, 4),
                "is_grounded": True,
                "breakdown": {
                    "intent_confidence": round(intent_conf, 4),
                    "retrieval_score": 1.0,
                    "rerank_score": 1.0,
                    "entity_match": 1.0,
                    "citation_score": 1.0
                },
                "citations": []
            }

        if intent == "fallback" or not chunks:
            return {
                "overall_confidence": 0.20,
                "is_grounded": False,
                "breakdown": {
                    "intent_confidence": round(intent_conf, 4),
                    "retrieval_score": 0.0,
                    "rerank_score": 0.0,
                    "entity_match": 0.0,
                    "citation_score": 0.0
                },
                "citations": []
            }

        # 1. Retrieval & Rerank Scores
        top_retrieval_score = max((c.get("retrieval_score", 0.0) for c in chunks), default=0.0)
        top_rerank_score = max((c.get("rerank_score", 0.0) for c in chunks), default=0.0)

        # 2. Entity Alignment
        entity_score = 0.5
        course = entities.get("course") or entities.get("canonical_course_name")
        course_code = entities.get("course_code")
        unit = entities.get("unit")
        semester = entities.get("semester")

        matched_entities = 0
        total_entities = 0
        if course or course_code:
            total_entities += 1
            if any((course and course.lower() in (c.get("course_name") or "").lower()) or
                   (course_code and course_code.upper() == (c.get("course_code") or "").upper()) for c in chunks):
                matched_entities += 1
        if unit:
            total_entities += 1
            if any(c.get("unit") == unit for c in chunks):
                matched_entities += 1
        if semester:
            total_entities += 1
            if any(c.get("semester") == semester for c in chunks):
                matched_entities += 1

        if total_entities > 0:
            entity_score = matched_entities / total_entities
        else:
            entity_score = 0.8  # General query (e.g. academic regulations)

        # 3. Citation Check in Generated Answer
        citations = []
        for c in chunks:
            c_id = c.get("chunk_id", "")
            source_doc = c.get("source_document") or c.get("document_name") or "Curriculum Handbook"
            page = c.get("page_number") or c.get("page")
            section = c.get("section_heading") or c.get("section") or c.get("course_name")

            # Check if mentioned
            doc_code = c.get("course_code") or ""
            is_cited = False
            if c_id and c_id in answer:
                is_cited = True
            elif doc_code and doc_code in answer:
                is_cited = True
            elif f"Page {page}" in answer or f"page {page}" in answer:
                is_cited = True
            elif source_doc in answer:
                is_cited = True

            citations.append({
                "chunk_id": c_id,
                "source_document": source_doc,
                "page": page,
                "section": section,
                "course_code": doc_code,
                "course_name": c.get("course_name"),
                "relevance_score": c.get("rerank_score") or c.get("retrieval_score", 0.0),
                "is_cited": is_cited
            })

        citation_score = 0.9 if any(cit["is_cited"] for cit in citations) else 0.65

        # Weighted aggregate
        overall = (
            0.20 * intent_conf +
            0.30 * top_retrieval_score +
            0.30 * top_rerank_score +
            0.10 * entity_score +
            0.10 * citation_score
        )
        overall_clamped = round(max(0.0, min(1.0, overall)), 4)

        is_grounded = (
            top_retrieval_score >= self.retrieval_threshold and
            top_rerank_score >= self.rerank_threshold and
            overall_clamped >= 0.50
        )

        return {
            "overall_confidence": overall_clamped,
            "is_grounded": is_grounded,
            "breakdown": {
                "intent_confidence": round(intent_conf, 4),
                "top_retrieval_score": round(top_retrieval_score, 4),
                "top_rerank_score": round(top_rerank_score, 4),
                "entity_alignment": round(entity_score, 4),
                "citation_score": round(citation_score, 4)
            },
            "citations": citations
        }

attribution_engine = AttributionEngine()
