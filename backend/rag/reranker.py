"""NVIDIA NIM Reranker Client with intelligent lexical-semantic fallback.
Reranks initial candidate chunks using cross-attention relevance scoring.
"""
from typing import List, Dict, Any, Optional
import requests
from backend.config import settings
from backend.utils.logger import logger

class RerankerService:
    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_BASE_URL.rstrip("/")
        self.model = settings.RERANKER_MODEL
        self.top_k = settings.RERANKER_TOP_K

    def _fallback_rerank(self, query: str, chunks: List[Dict[str, Any]], intent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Intelligent local cross-scoring using n-gram overlap, exact code matching, section match, and position weighting."""
        query_words = set(query.lower().split())
        scored = []

        # Intent to section keywords
        intent_keywords = {
            "prerequisites": ["prerequisite", "prereq", "prior"],
            "course_outcome": ["outcome", "co", "learning outcome"],
            "course_objectives": ["objective", "aim", "goal"],
            "credits": ["credit", "l: ", "t: ", "p: "],
            "units": ["unit", "module"],
            "unit_topics": ["unit", "module", "topics"],
            "academic_regulations": ["attendance", "grading", "regulation", "cia", "credit requirements"]
        }

        target_kws = intent_keywords.get(intent or "", [])

        for orig_idx, chunk in enumerate(chunks):
            text = (chunk.get("text", "") + " " + (chunk.get("section_heading") or chunk.get("section") or "")).lower()
            text_words = set(text.split())

            # Keyword overlap Jaccard
            overlap = len(query_words.intersection(text_words))
            jaccard = overlap / max(1, len(query_words.union(text_words)))

            # Section intent keyword match bonus
            intent_bonus = 0.0
            for kw in target_kws:
                if kw in text:
                    intent_bonus = 0.45
                    break

            # Exact phrase bonus
            phrase_bonus = 0.35 if any(w in text for w in query_words if len(w) > 4) else 0.0

            # Course code exact match bonus
            code_bonus = 0.25 if chunk.get("course_code") and chunk["course_code"].lower() in query.lower() else 0.0

            # Base retrieval score
            ret_score = chunk.get("retrieval_score", 0.5)

            # Combined pseudo cross-attention score
            score = round(min(1.0, 0.3 * ret_score + 0.25 * jaccard + phrase_bonus + code_bonus + intent_bonus), 4)

            item = dict(chunk)
            item["rerank_score"] = score
            item["original_rank"] = orig_idx + 1
            scored.append(item)

        # Sort by rerank score descending
        scored = sorted(scored, key=lambda x: x["rerank_score"], reverse=True)
        for new_rank, item in enumerate(scored, 1):
            item["new_rank"] = new_rank
        return scored[:self.top_k]

    def rerank(self, query: str, chunks: List[Dict[str, Any]], intent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Rerank candidates using NVIDIA NIM cross-encoder or local fallback."""
        if not chunks:
            return []

        if len(chunks) <= 1:
            chunk = dict(chunks[0])
            chunk["rerank_score"] = 0.95
            chunk["original_rank"] = 1
            chunk["new_rank"] = 1
            return [chunk]

        # If NVIDIA API Key is provided
        if self.api_key and not self.api_key.startswith("nvapi-placeholder") and len(self.api_key) > 20:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                url = f"{self.base_url}/ranking"
                passages = [{"text": c["text"]} for c in chunks]
                payload = {
                    "model": self.model,
                    "query": {"text": query},
                    "passages": passages,
                    "truncate": "END"
                }
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    resp_json = response.json()
                    rankings = resp_json.get("rankings", [])
                    reranked = []
                    for new_rank, item in enumerate(rankings[:self.top_k], 1):
                        orig_idx = item["index"]
                        chunk = dict(chunks[orig_idx])
                        chunk["rerank_score"] = round(float(item.get("logit", 0.9)), 4)
                        chunk["original_rank"] = orig_idx + 1
                        chunk["new_rank"] = new_rank
                        reranked.append(chunk)
                    logger.info(f"Successfully reranked {len(chunks)} chunks via NVIDIA NIM ({self.model})")
                    return reranked
                else:
                    logger.warning(f"NVIDIA NIM reranker returned {response.status_code}: {response.text[:200]}")
            except Exception as e:
                logger.warning(f"Error calling NVIDIA NIM reranker: {e}")

        # Local fallback reranking
        return self._fallback_rerank(query, chunks, intent=intent)

reranker_service = RerankerService()
