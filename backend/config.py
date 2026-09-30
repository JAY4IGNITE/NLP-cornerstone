"""Application configuration and environment settings."""
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DOCUMENTS_DIR = BASE_DIR / "documents" / "curriculum"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure essential directories exist
for p in [DATA_DIR, MODELS_DIR, DOCUMENTS_DIR, REPORTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    # App Information
    APP_NAME: str = "AI-Based Student Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # NVIDIA NIM configurations
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_EMBEDDING_MODEL: str = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")
    NVIDIA_RERANKER_MODEL: str = os.getenv("NVIDIA_RERANKER_MODEL", "nvidia/reranking-mistral-4b")
    NVIDIA_LLM_MODEL: str = os.getenv("NVIDIA_LLM_MODEL", "meta/llama-3.1-70b-instruct")

    # Aliases for convenience
    @property
    def EMBEDDING_MODEL(self) -> str:
        return self.NVIDIA_EMBEDDING_MODEL

    @property
    def RERANKER_MODEL(self) -> str:
        return self.NVIDIA_RERANKER_MODEL

    @property
    def LLM_MODEL(self) -> str:
        return self.NVIDIA_LLM_MODEL

    # Cloudflare Vectorize & Workers AI configuration
    CLOUDFLARE_ACCOUNT_ID: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    CLOUDFLARE_API_TOKEN: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    CLOUDFLARE_VECTORIZE_INDEX: str = os.getenv("CLOUDFLARE_VECTORIZE_INDEX", "student-curriculum-index")
    CLOUDFLARE_EMBEDDING_MODEL: str = os.getenv("CLOUDFLARE_EMBEDDING_MODEL", "@cf/baai/bge-base-en-v1.5")

    # Legacy alias compatibility
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "curriculum_chunks")

    @property
    def QDRANT_COLLECTION_NAME(self) -> str:
        return self.CLOUDFLARE_VECTORIZE_INDEX

    @property
    def COLLECTION_NAME(self) -> str:
        return self.CLOUDFLARE_VECTORIZE_INDEX

    @property
    def VECTORIZE_INDEX_NAME(self) -> str:
        return self.CLOUDFLARE_VECTORIZE_INDEX

    # Confidence and Retrieval Thresholds (Strict Hallucination Prevention)
    INTENT_CONFIDENCE_THRESHOLD: float = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.55"))
    RETRIEVAL_SCORE_THRESHOLD: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.45"))
    RERANKER_TOP_K: int = int(os.getenv("RERANKER_TOP_K", "4"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "5"))

settings = Settings()
