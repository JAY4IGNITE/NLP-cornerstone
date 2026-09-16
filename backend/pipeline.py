"""End-to-end Academic NLP and RAG Chatbot Pipeline.
Orchestrates preprocessing -> intent classification -> entity extraction -> hybrid retrieval ->
cross-attention reranking -> grounded answer generation -> attribution confidence scoring.
"""
import time
from typing import List, Dict, Any, Optional

from backend.nlp.intent_classifier import intent_classifier
from backend.nlp.entity_extractor import entity_extractor
from backend.rag.retriever import hybrid_retriever
from backend.rag.reranker import reranker_service
from backend.rag.generator import answer_generator
from backend.rag.attribution import attribution_engine
from backend.guardrails import guardrails
from backend.utils.logger import logger

class StudentChatbotPipeline:
    def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """Execute the full 8-stage academic NLP + RAG pipeline."""
        start_time = time.time()
        logger.info(f"Processing query: '{query}'")

        # 0. Safety & Boundary Guardrail Check
        is_safe, failure_reason, refusal_msg = guardrails.check_input_safety(query)
        if not is_safe:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": query,
                "intent": "out_of_scope" if failure_reason == "non_academic_domain" else "security_guardrail",
                "intent_confidence": 1.0,
                "raw_intent": failure_reason,
                "is_fallback": True,
                "top_intents": [],
                "entities": {},
                "answer": refusal_msg,
                "sources": [],
                "is_grounded": True,
                "overall_confidence": 1.0,
                "confidence_breakdown": {
                    "guardrail_triggered": failure_reason
                },
                "retrieved_chunk_count": 0,
                "reranked_chunk_count": 0,
                "latency_ms": latency_ms
            }

        # 1. Intent Classification
        intent_result = intent_classifier.predict(query)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        # 2. Entity Extraction
        entities = entity_extractor.extract(query)

        # 3. Hybrid Retrieval (Dense Qdrant + Sparse BM25 with entity filtering)
        retrieved_chunks = []
        reranked_chunks = []

        # Conversational intents do not require PDF retrieval
        if intent not in {"greeting", "thanks", "help", "fallback"}:
            retrieved_chunks = hybrid_retriever.retrieve(
                query=query,
                entities=entities,
                intent=intent,
                top_k=top_k * 2
            )

            # 4. Cross-Encoder Reranking
            if retrieved_chunks:
                reranked_chunks = reranker_service.rerank(query=query, chunks=retrieved_chunks, intent=intent)
            else:
                reranked_chunks = []

            # Guardrail: Validate retrieval relevance threshold
            is_retrieval_grounded, grounding_warning = guardrails.validate_retrieval_grounding(intent, reranked_chunks)
            if not is_retrieval_grounded:
                latency_ms = round((time.time() - start_time) * 1000, 2)
                return {
                    "query": query,
                    "intent": intent,
                    "intent_confidence": confidence,
                    "raw_intent": intent_result.get("raw_intent", intent),
                    "is_fallback": True,
                    "top_intents": intent_result.get("top_intents", []),
                    "entities": entities,
                    "answer": grounding_warning,
                    "sources": [],
                    "is_grounded": False,
                    "overall_confidence": 0.25,
                    "confidence_breakdown": {
                        "reason": "retrieval_below_threshold"
                    },
                    "retrieved_chunk_count": len(retrieved_chunks),
                    "reranked_chunk_count": len(reranked_chunks),
                    "latency_ms": latency_ms
                }
        else:
            reranked_chunks = []

        # 5. Grounded Answer Generation
        answer = answer_generator.generate(
            query=query,
            intent_data=intent_result,
            entities=entities,
            chunks=reranked_chunks,
            chat_history=chat_history
        )

        # 6. Source Attribution & Confidence Scoring
        attribution_result = attribution_engine.calculate_confidence(
            query=query,
            answer=answer,
            intent_data=intent_result,
            entities=entities,
            chunks=reranked_chunks
        )

        # 7. Fact & Hallucination Check
        fact_check = guardrails.verify_answer_facts(answer, entities, reranked_chunks)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        pipeline_output = {
            "query": query,
            "intent": intent,
            "intent_confidence": confidence,
            "raw_intent": intent_result.get("raw_intent", intent),
            "is_fallback": intent_result.get("is_fallback", False),
            "top_intents": intent_result.get("top_intents", []),
            "entities": entities,
            "answer": answer,
            "sources": attribution_result["citations"],
            "is_grounded": attribution_result["is_grounded"],
            "overall_confidence": attribution_result["overall_confidence"],
            "confidence_breakdown": attribution_result["breakdown"],
            "fact_check": fact_check,
            "retrieved_chunk_count": len(retrieved_chunks),
            "reranked_chunk_count": len(reranked_chunks),
            "latency_ms": latency_ms
        }

        logger.info(
            f"Completed pipeline: intent='{intent}' ({confidence}), "
            f"grounded={attribution_result['is_grounded']}, latency={latency_ms}ms"
        )
        return pipeline_output

pipeline = StudentChatbotPipeline()
