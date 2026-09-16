"""Vector Storage Provider - Cloudflare Vectorize.
Primary vector database backend powered by Cloudflare Vectorize edge vector engine.
Maintains full backward-compatible interfaces for the Academic RAG Pipeline.
"""
from typing import List, Dict, Any, Optional
from backend.rag.cloudflare_vector_store import (
    CloudflareVectorStore,
    cloudflare_vector_store,
)

class VectorStore:
    """Cloudflare Vectorize vector store adapter."""

    def __init__(self, collection_name: Optional[str] = None):
        self.store = CloudflareVectorStore(index_name=collection_name)
        self.collection_name = self.store.index_name

    def insert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        return self.store.insert_chunks(chunks, embeddings)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        course: Optional[str] = None,
        course_code: Optional[str] = None,
        semester: Optional[int] = None,
        unit: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.store.search(
            query_vector=query_vector,
            top_k=top_k,
            course=course,
            course_code=course_code,
            semester=semester,
            unit=unit,
            category=category
        )

    def get_total_chunks(self) -> int:
        return self.store.get_total_chunks()

    def get_index_info(self) -> Dict[str, Any]:
        return self.store.get_index_info()

# Export singleton instance
vector_store = cloudflare_vector_store
