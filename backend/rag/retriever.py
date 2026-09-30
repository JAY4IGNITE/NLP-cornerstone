"""Hybrid Retrieval Engine (Dense Qdrant Vector Search + Sparse BM25 Keyword Search + Metadata Filtering + RRF Fusion).
Combines dense semantic vector search with BM25 lexical search using Reciprocal Rank Fusion.
"""
import json
import math
import re
from collections import defaultdict
from typing import List, Dict, Any, Optional, Set

from backend.config import DATA_DIR, settings
from backend.rag.embeddings import embedding_service
from backend.rag.vector_store import vector_store
from backend.utils.logger import logger

class BM25Searcher:
    """Lightweight in-memory BM25 retrieval index for exact curriculum codes and keywords."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[Dict[str, Any]] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_lens: List[int] = []
        self.avg_dl: float = 0.0
        self.idf: Dict[str, float] = {}
        self.load_index()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\b", text.lower())

    def load_index(self):
        chunks_file = DATA_DIR / "indexed_chunks.json"
        if not chunks_file.exists():
            return
        try:
            with open(chunks_file, "r", encoding="utf-8") as f:
                self.documents = json.load(f)

            if not self.documents:
                return

            self.doc_tokens = [self._tokenize(doc["text"]) for doc in self.documents]
            self.doc_lens = [len(tokens) for tokens in self.doc_tokens]
            self.avg_dl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 1.0

            # Document frequencies
            df: Dict[str, int] = defaultdict(int)
            for tokens in self.doc_tokens:
                seen: Set[str] = set(tokens)
                for t in seen:
                    df[t] += 1

            n = len(self.documents)
            for term, freq in df.items():
                # Robertson-Spärck Jones IDF
                self.idf[term] = math.log((n - freq + 0.5) / (freq + 0.5) + 1.0)
            logger.info(f"Initialized BM25 index over {len(self.documents)} curriculum chunks")
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        query_tokens = self._tokenize(query)
        scores = [0.0] * len(self.documents)

        for i, tokens in enumerate(self.doc_tokens):
            d_len = self.doc_lens[i]
            # Term frequencies
            tf: Dict[str, int] = defaultdict(int)
            for t in tokens:
                tf[t] += 1

            score = 0.0
            for qt in query_tokens:
                if qt in tf:
                    t_freq = tf[qt]
                    term_idf = self.idf.get(qt, 0.0)
                    numerator = term_idf * t_freq * (self.k1 + 1.0)
                    denominator = t_freq + self.k1 * (1.0 - self.b + self.b * (d_len / self.avg_dl))
                    score += (numerator / denominator)
            scores[i] = score

        ranked_indices = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)
        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] > 0.0:
                doc = dict(self.documents[idx])
                doc["score"] = round(scores[idx], 4)
                results.append(doc)
        return results

class HybridRetriever:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.bm25 = BM25Searcher()

    def retrieve(
        self,
        query: str,
        entities: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """Perform metadata-filtered dense search + BM25 keyword search and fuse via RRF."""
        entities = entities or {}
        course = entities.get("canonical_course_name") or entities.get("course")
        course_code = entities.get("course_code")
        semester = entities.get("semester")
        unit = entities.get("unit")

        # Query Expansion based on detected intent
        expanded_query = query
        if intent == "prerequisites" and "prerequisite" not in expanded_query.lower():
            expanded_query = f"{expanded_query} prerequisites prior knowledge"
        elif intent == "course_outcome" and "outcome" not in expanded_query.lower():
            expanded_query = f"{expanded_query} course outcomes COs"
        elif intent == "course_objectives" and "objective" not in expanded_query.lower():
            expanded_query = f"{expanded_query} objectives instructional goals"
        elif intent == "credits" and "credit" not in expanded_query.lower():
            expanded_query = f"{expanded_query} credits L T P"
        elif intent == "academic_regulations":
            expanded_query = f"{expanded_query} attendance grading regulations credit requirements"
        elif "hostel" in query.lower() or "mess" in query.lower() or "curfew" in query.lower():
            expanded_query = f"{expanded_query} hostel curfew mess timing warden outstation pass rules"
        elif "library" in query.lower() or "books" in query.lower():
            expanded_query = f"{expanded_query} central library timings borrowing cards IEEE digital repositories"
        elif "scholarship" in query.lower() or "fee waiver" in query.lower() or "financial aid" in query.lower():
            expanded_query = f"{expanded_query} merit scholarship financial assistance fee waiver NSP"
        elif "placement" in query.lower() or "internship" in query.lower() or "recruitment" in query.lower():
            expanded_query = f"{expanded_query} training placement cell eligibility dream company CGPA NOC"
        elif "revaluation" in query.lower() or "supplementary" in query.lower() or "arrear" in query.lower():
            expanded_query = f"{expanded_query} revaluation script photocopy supplementary examination arrear rules"
        elif "cheat sheet" in query.lower() or "formula" in query.lower() or "quick revision" in query.lower():
            expanded_query = f"{expanded_query} cheat sheet revision notes formulas complexity algorithms"

        # 1. Dense Semantic Retrieval via Cloudflare Vectorize
        query_vec = embedding_service.get_query_embedding(expanded_query)
        dense_results = vector_store.search(
            query_vector=query_vec,
            top_k=top_k * 2,
            course=course,
            course_code=course_code,
            semester=semester,
            unit=unit
        )

        # 2. Sparse Lexical Retrieval via BM25
        # Augment search query with detected course codes or unit keywords
        search_query = expanded_query
        if course_code and course_code.lower() not in search_query.lower():
            search_query = f"{course_code} {search_query}"
        if unit and f"unit {unit}" not in search_query.lower():
            search_query = f"{search_query} unit {unit}"

        sparse_results = self.bm25.search(search_query, top_k=top_k * 2)

        # Apply entity filters to sparse results if needed
        if course_code or semester or unit:
            filtered_sparse = []
            for item in sparse_results:
                match = True
                if course_code and item.get("course_code") and item["course_code"].upper() != course_code.upper():
                    match = False
                if semester and item.get("semester") and item["semester"] != semester:
                    match = False
                if unit and item.get("unit") and item["unit"] != unit:
                    match = False
                if match:
                    filtered_sparse.append(item)
            if filtered_sparse:
                sparse_results = filtered_sparse

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = defaultdict(float)
        chunk_map: Dict[str, Dict[str, Any]] = {}
        dense_ranks: Dict[str, int] = {}
        sparse_ranks: Dict[str, int] = {}

        # Dense contributions
        for rank, item in enumerate(dense_results, 1):
            c_id = item["chunk_id"]
            chunk_map[c_id] = item
            dense_ranks[c_id] = rank
            rrf_scores[c_id] += 1.0 / (self.rrf_k + rank)

        # Sparse contributions
        for rank, item in enumerate(sparse_results, 1):
            c_id = item["chunk_id"]
            chunk_map[c_id] = item
            sparse_ranks[c_id] = rank
            rrf_scores[c_id] += 1.0 / (self.rrf_k + rank)

        # Sort combined chunks by RRF score
        sorted_chunks = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        final_results = []

        for c_id in sorted_chunks[:top_k]:
            chunk = chunk_map[c_id]
            fused_score = round(rrf_scores[c_id], 5)
            # Normalize RRF score to 0.0 - 1.0 scale approximately
            # Max possible score for rank 1 in both is 2 / (60 + 1) = 0.03278
            normalized_score = min(1.0, round(fused_score / 0.0328, 4))
            chunk_copy = dict(chunk)
            chunk_copy["rrf_score"] = fused_score
            chunk_copy["retrieval_score"] = normalized_score
            chunk_copy["dense_rank"] = dense_ranks.get(c_id)
            chunk_copy["sparse_rank"] = sparse_ranks.get(c_id)
            final_results.append(chunk_copy)

        return final_results

hybrid_retriever = HybridRetriever()
