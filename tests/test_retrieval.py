import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.retrieval.retriever import SemanticRetriever

def test_retriever():
    retriever = SemanticRetriever()
    assert retriever is not None
