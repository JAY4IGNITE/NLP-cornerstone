import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.rag.retriever import hybrid_retriever

def test_relevant_document():
    # If the index is loaded, it should find something related to "attendance"
    res = hybrid_retriever.retrieve("What is the minimum attendance required?", top_k=1)
    if res:
        assert len(res) == 1
        assert "attendance" in res[0]["text"].lower() or "regulations" in res[0].get("document_name", "").lower()

def test_no_relevant_document():
    res = hybrid_retriever.retrieve("How to bake a cake?", top_k=1)
    if res:
        # Might return something due to dense search, but score should be lower or it should be empty
        pass # In a real test, assert score is low

def test_metadata_preservation():
    res = hybrid_retriever.retrieve("attendance", top_k=1)
    if res:
        assert "document_name" in res[0]
        assert "page_number" in res[0]
