import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.pipeline import pipeline

def test_complete_successful_query():
    res = pipeline.process_query("What is the minimum attendance?", top_k=2)
    assert res["intent"] == "attendance_rules"
    assert "answer" in res
    assert "sources" in res
    assert res["is_grounded"] == True or res["is_grounded"] == False

def test_low_confidence_query():
    res = pipeline.process_query("Can you predict my GPA based on astrology?")
    assert res["is_fallback"] == True or res["intent"] == "fallback"

def test_source_citation():
    res = pipeline.process_query("attendance", top_k=1)
    if res["is_grounded"] and res["sources"]:
        assert "document_id" in res["sources"][0]
