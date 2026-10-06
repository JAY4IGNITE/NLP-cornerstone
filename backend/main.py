from fastapi import FastAPI
from pydantic import BaseModel
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.pipeline import HybridPipeline

app = FastAPI(title="CampusNLP API", description="Intelligent NLP-Based University Student Query Understanding and Knowledge Retrieval System")
nlp_pipeline = HybridPipeline()

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
def query_endpoint(req: QueryRequest):
    """
    Main endpoint matching the API Contract from the MASTER_IMPLEMENTATION_PLAN.md
    """
    result = nlp_pipeline.process_query(req.query)
    
    # Format according to the required schema
    return {
        "query": result["query"],
        "intent": result["intent"],
        "confidence": round(result["confidence"], 2),
        "answer": result["response"],
        "sources": [
            {
                "document": result["source"],
                "page": 1 # Placeholder as demo_knowledge_chunks doesn't have page level precision
            }
        ] if result["source"] else []
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "CampusNLP"}
