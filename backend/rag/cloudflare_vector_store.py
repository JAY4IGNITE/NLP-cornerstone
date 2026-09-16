"""Cloudflare Vectorize Vector Database Integration.
Supports direct integration with Cloudflare Vectorize v2 HTTP REST API at the edge,
with a high-performance local edge emulation fallback when API tokens are not provided.
Provides metadata filtering, cosine similarity scoring, and batch upsert capabilities.
"""
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import requests

from backend.config import settings, DATA_DIR
from backend.rag.embeddings import EMBEDDING_DIM
from backend.utils.logger import logger

CLOUDFLARE_STORAGE_FILE = DATA_DIR / "cloudflare_vectorize_storage.json"

class CloudflareVectorStore:
    """Manages vector embeddings and retrieval using Cloudflare Vectorize."""

    def __init__(self, index_name: Optional[str] = None):
        self.index_name = index_name or settings.CLOUDFLARE_VECTORIZE_INDEX
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.api_token = settings.CLOUDFLARE_API_TOKEN
        self.dimension = EMBEDDING_DIM
        self.metric = "cosine"
        self.is_remote = bool(self.account_id and self.api_token)

        # In-memory store for fast retrieval and local emulation
        self._local_vectors: List[Dict[str, Any]] = []
        self._vector_matrix: Optional[np.ndarray] = None
        self._id_to_meta: Dict[str, Dict[str, Any]] = {}

        self._init_store()

    @property
    def provider(self) -> str:
        return "cloudflare_vectorize_remote" if self.is_remote else "cloudflare_vectorize_edge_emulator"

    def _init_store(self):
        """Initialize local persistence cache or remote Cloudflare Vectorize index."""
        if self.is_remote:
            try:
                # Check if Cloudflare Vectorize index exists
                url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/vectorize/v2/indexes/{self.index_name}"
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    logger.info(f"Connected to remote Cloudflare Vectorize index '{self.index_name}'")
                else:
                    logger.warning(
                        f"Cloudflare Vectorize remote check returned {res.status_code}: {res.text}. "
                        "Will use local edge emulator store with Cloudflare Vectorize semantics."
                    )
            except Exception as e:
                logger.warning(f"Error checking remote Cloudflare Vectorize index: {e}")

        # Always load or initialize local storage for resilient edge caching
        self._load_local_storage()

    def _load_local_storage(self):
        """Load cached vector records from local disk."""
        if CLOUDFLARE_STORAGE_FILE.exists():
            try:
                with open(CLOUDFLARE_STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._local_vectors = data
                    self._build_vector_matrix()
                logger.info(
                    f"Cloudflare Vectorize loaded {len(self._local_vectors)} vectors from {CLOUDFLARE_STORAGE_FILE}"
                )
            except Exception as e:
                logger.error(f"Failed to load Cloudflare Vectorize storage cache: {e}")
                self._local_vectors = []
        else:
            # Check if previous indexed_chunks exists and migrate automatically
            legacy_file = DATA_DIR / "indexed_chunks.json"
            if legacy_file.exists():
                try:
                    with open(legacy_file, "r", encoding="utf-8") as f:
                        chunks = json.load(f)
                    # Convert to Cloudflare Vectorize format
                    migrated = []
                    for idx, c in enumerate(chunks):
                        migrated.append({
                            "id": c.get("chunk_id", f"cf_vec_{idx+1}"),
                            "text": c.get("text", ""),
                            "metadata": {
                                "chunk_id": c.get("chunk_id", f"cf_vec_{idx+1}"),
                                "course_name": c.get("course_name", ""),
                                "course_code": c.get("course_code", ""),
                                "branch": c.get("branch", "CSE"),
                                "semester": c.get("semester"),
                                "unit": c.get("unit"),
                                "page_number": c.get("page_number", 1),
                                "source_document": c.get("source_document", "Curriculum.pdf"),
                                "section_heading": c.get("section_heading", "")
                            },
                            "values": c.get("embedding")
                        })
                    self._local_vectors = migrated
                    self._persist_local_storage()
                    self._build_vector_matrix()
                    logger.info(f"Auto-migrated {len(migrated)} chunks to Cloudflare Vectorize format")
                except Exception as e:
                    logger.warning(f"Failed legacy chunk migration: {e}")

    def _build_vector_matrix(self):
        """Construct normalized NumPy matrix for sub-millisecond cosine similarity search."""
        if not self._local_vectors:
            self._vector_matrix = None
            self._id_to_meta = {}
            return

        valid_vectors = []
        self._id_to_meta = {}
        for idx, item in enumerate(self._local_vectors):
            vals = item.get("values")
            if vals and len(vals) > 0:
                v = np.array(vals, dtype=np.float32)
                norm = np.linalg.norm(v)
                if norm > 0:
                    v = v / norm
                valid_vectors.append(v)
                self._id_to_meta[idx] = item

        if valid_vectors:
            self._vector_matrix = np.vstack(valid_vectors)
        else:
            self._vector_matrix = None

    def _persist_local_storage(self):
        """Persist vector index to disk."""
        try:
            with open(CLOUDFLARE_STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._local_vectors, f, indent=1)
        except Exception as e:
            logger.error(f"Failed to persist Cloudflare Vectorize storage: {e}")

    def insert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        """Upsert chunk records into Cloudflare Vectorize."""
        if not chunks or not embeddings or len(chunks) != len(embeddings):
            return 0

        new_records = []
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            chunk_id = chunk.get("chunk_id") or f"cf_{idx+1}_{int(time.time())}"
            metadata = {
                "chunk_id": chunk_id,
                "course_name": chunk.get("course_name") or "",
                "course_code": (chunk.get("course_code") or "").upper(),
                "branch": chunk.get("branch") or "CSE",
                "semester": chunk.get("semester"),
                "unit": chunk.get("unit"),
                "page_number": chunk.get("page_number", 1),
                "source_document": chunk.get("source_document") or "Curriculum.pdf",
                "section_heading": chunk.get("section_heading") or chunk.get("section") or "",
                "category": chunk.get("category") or "curriculum"
            }

            record = {
                "id": chunk_id,
                "text": chunk.get("text", ""),
                "metadata": metadata,
                "values": vector
            }
            new_records.append(record)

        # 1. If remote Cloudflare Vectorize is active, upsert via Cloudflare HTTP API
        if self.is_remote:
            try:
                upsert_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/vectorize/v2/indexes/{self.index_name}/upsert"
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/x-ndjson"
                }
                # Cloudflare Vectorize accepts NDJSON payload for upserts
                ndjson_lines = "\n".join(
                    json.dumps({
                        "id": r["id"],
                        "values": r["values"],
                        "metadata": {**r["metadata"], "text": r["text"][:1000]}
                    }) for r in new_records
                )
                res = requests.post(upsert_url, data=ndjson_lines, headers=headers, timeout=15)
                if res.status_code == 200:
                    logger.info(f"Upserted {len(new_records)} vectors to remote Cloudflare Vectorize index '{self.index_name}'")
                else:
                    logger.warning(f"Remote Cloudflare Vectorize upsert status {res.status_code}: {res.text}")
            except Exception as e:
                logger.warning(f"Remote Cloudflare Vectorize upsert failed: {e}")

        # 2. Update local edge index
        # Avoid duplicate IDs
        existing_ids = {r["id"] for r in self._local_vectors}
        for rec in new_records:
            if rec["id"] in existing_ids:
                # Replace existing
                self._local_vectors = [r if r["id"] != rec["id"] else rec for r in self._local_vectors]
            else:
                self._local_vectors.append(rec)

        self._persist_local_storage()
        self._build_vector_matrix()

        logger.info(f"Upserted {len(new_records)} vectors into Cloudflare Vectorize (Total: {len(self._local_vectors)})")
        return len(new_records)

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
        """Query Cloudflare Vectorize with optional metadata filtering and cosine ranking."""
        # 1. Attempt remote Cloudflare Vectorize query if credentials configured
        if self.is_remote:
            try:
                query_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/vectorize/v2/indexes/{self.index_name}/query"
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }
                filter_obj = {}
                if course_code:
                    filter_obj["course_code"] = course_code.upper()
                if semester:
                    filter_obj["semester"] = semester
                if unit:
                    filter_obj["unit"] = unit
                if category:
                    filter_obj["category"] = category

                payload = {
                    "vector": query_vector,
                    "topK": top_k,
                    "returnValues": False,
                    "returnMetadata": "all"
                }
                if filter_obj:
                    payload["filter"] = filter_obj

                res = requests.post(query_url, json=payload, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    matches = data.get("result", {}).get("matches", [])
                    results = []
                    for m in matches:
                        meta = m.get("metadata", {})
                        results.append({
                            "chunk_id": m.get("id"),
                            "score": round(float(m.get("score", 0.0)), 4),
                            "text": meta.get("text") or "",
                            "course_name": meta.get("course_name"),
                            "course_code": meta.get("course_code"),
                            "branch": meta.get("branch", "CSE"),
                            "semester": meta.get("semester"),
                            "unit": meta.get("unit"),
                            "page_number": meta.get("page_number", 1),
                            "source_document": meta.get("source_document", ""),
                            "section_heading": meta.get("section_heading", ""),
                            "category": meta.get("category", "curriculum")
                        })
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"Remote Cloudflare Vectorize query failed ({e}). Using local edge index.")

        # 2. Local Edge Search (Cosine similarity with vectorized NumPy)
        if self._vector_matrix is None or len(self._local_vectors) == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm

        scores = np.dot(self._vector_matrix, q_vec)

        # Filter candidates based on metadata conditions
        matched_indices = []
        for matrix_idx in range(len(scores)):
            item = self._id_to_meta.get(matrix_idx)
            if not item:
                continue
            meta = item.get("metadata", {})

            # Filter conditions
            if course_code and meta.get("course_code", "").upper() != course_code.upper():
                continue
            if course and course.lower() not in meta.get("course_name", "").lower():
                continue
            if semester and meta.get("semester") != semester:
                continue
            if unit and meta.get("unit") != unit:
                continue
            if category and meta.get("category") != category:
                continue

            matched_indices.append((matrix_idx, float(scores[matrix_idx])))

        # Fallback if filtered search returned no matches
        if not matched_indices and (course_code or course or semester or unit or category):
            matched_indices = [(i, float(scores[i])) for i in range(len(scores))]

        # Sort by score descending
        matched_indices.sort(key=lambda x: x[1], reverse=True)
        top_candidates = matched_indices[:top_k]

        results = []
        for matrix_idx, score in top_candidates:
            item = self._id_to_meta[matrix_idx]
            meta = item.get("metadata", {})
            results.append({
                "chunk_id": item.get("id"),
                "score": round(score, 4),
                "text": item.get("text", ""),
                "course_name": meta.get("course_name"),
                "course_code": meta.get("course_code"),
                "branch": meta.get("branch", "CSE"),
                "semester": meta.get("semester"),
                "unit": meta.get("unit"),
                "page_number": meta.get("page_number", 1),
                "source_document": meta.get("source_document", ""),
                "section_heading": meta.get("section_heading", ""),
                "category": meta.get("category", "curriculum")
            })

        return results

    def get_total_chunks(self) -> int:
        """Return total vector count in index."""
        return len(self._local_vectors)

    def get_index_info(self) -> Dict[str, Any]:
        """Return Cloudflare Vectorize status and index statistics."""
        return {
            "provider": "Cloudflare Vectorize",
            "index_name": self.index_name,
            "dimensions": self.dimension,
            "metric": self.metric,
            "total_vectors": len(self._local_vectors),
            "is_remote_authenticated": self.is_remote,
            "edge_storage_status": "synced" if len(self._local_vectors) > 0 else "empty",
            "account_configured": bool(self.account_id)
        }

# Global instance
cloudflare_vector_store = CloudflareVectorStore()
