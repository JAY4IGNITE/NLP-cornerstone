"""End-to-End API Test Suite for AI-Based Student Chatbot.
Tests all FastAPI endpoints with the 1,000,000-row real Hugging Face model and curriculum RAG.
"""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.main import app

def run_api_tests():
    client = TestClient(app)
    results = {}

    print("======================================================================")
    print("RUNNING COMPLETE API ENDPOINT VERIFICATION SUITE")
    print("======================================================================")

    # 1. Health Check
    print("\n1. Testing GET /api/health...")
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    health_data = resp.json()
    print(f"   Status: {health_data['status']} | Vector Provider: {health_data['vector_provider']}")
    results["health"] = "PASS"

    # 2. Metrics & 1M Dataset Statistics
    print("\n2. Testing GET /api/metrics...")
    resp = client.get("/api/metrics")
    assert resp.status_code == 200, f"Metrics check failed: {resp.status_code}"
    metrics_data = resp.json()
    total_q = metrics_data["dataset"]["total_queries"]
    is_synth = metrics_data["dataset"]["is_synthetic"]
    source = metrics_data["dataset"]["source"]
    print(f"   Total Queries in Dataset: {total_q:,}")
    print(f"   Is Synthetic: {is_synth} (Real data requirement)")
    print(f"   Data Source: {source}")
    assert total_q >= 1_000_000, f"Expected >= 1,000,000 rows, got {total_q}"
    assert not is_synth, "Expected non-synthetic real data"
    results["metrics"] = "PASS"

    # 3. Intent Classification
    print("\n3. Testing POST /api/nlp/classify...")
    test_queries = [
        "How do I set up a local database server?",
        "What are the admission prerequisites for semester 5?",
        "Where is the campus hostel mess located?"
    ]
    for q in test_queries:
        resp = client.post("/api/nlp/classify", json={"query": q})
        assert resp.status_code == 200, f"Classify failed for '{q}': {resp.status_code}"
        cls_data = resp.json()
        intent = cls_data["prediction"]["intent"]
        conf = cls_data["prediction"]["confidence"]
        print(f"   Query: '{q}' -> Intent: {intent} (conf: {conf:.2f})")
    results["nlp_classify"] = "PASS"

    # 4. Entity Extraction
    print("\n4. Testing POST /api/nlp/entities...")
    resp = client.post("/api/nlp/entities", json={"query": "Tell me about Unit 3 topics in CS301 Database Systems"})
    assert resp.status_code == 200, f"Entity extraction failed: {resp.status_code}"
    ent_data = resp.json()["entities"]
    print(f"   Extracted Entities: Course Code={ent_data.get('course_code')}, Unit={ent_data.get('unit')}, Course={ent_data.get('canonical_course_name')}")
    assert ent_data.get("course_code") == "CS301"
    assert ent_data.get("unit") == 3
    results["entity_extraction"] = "PASS"

    # 5. Hybrid Retrieval
    print("\n5. Testing POST /api/rag/retrieve...")
    resp = client.post("/api/rag/retrieve", json={"query": "Relational algebra and SQL", "course_code": "CS301", "top_k": 3})
    assert resp.status_code == 200, f"Retrieve failed: {resp.status_code}"
    ret_data = resp.json()
    print(f"   Retrieved {len(ret_data['retrieved_candidates'])} candidates, Reranked top {len(ret_data['reranked_top_k'])} chunks")
    assert len(ret_data["reranked_top_k"]) > 0
    results["hybrid_retrieval"] = "PASS"

    # 6. Curriculum Courses Catalog
    print("\n6. Testing GET /api/curriculum/courses...")
    resp = client.get("/api/curriculum/courses")
    assert resp.status_code == 200, f"Courses catalog failed: {resp.status_code}"
    courses = resp.json().get("courses", [])
    print(f"   Retrieved {len(courses)} accredited curriculum courses")
    assert len(courses) > 0
    results["courses_catalog"] = "PASS"

    # 7. Multi-Resource Catalog
    print("\n7. Testing GET /api/resources...")
    resp = client.get("/api/resources")
    assert resp.status_code == 200, f"Resources catalog failed: {resp.status_code}"
    catalog = resp.json().get("resources", [])
    print(f"   Integrated Resource Modules: {len(catalog)}")
    assert len(catalog) == 5
    results["resources_catalog"] = "PASS"

    # 8. Full End-to-End Chat Pipeline
    print("\n8. Testing POST /api/chat (Full Pipeline Execution)...")
    chat_payload = {
        "query": "What are the course objectives and prerequisites of CS201 Data Structures?",
        "chat_history": [],
        "top_k": 4
    }
    resp = client.post("/api/chat", json=chat_payload)
    assert resp.status_code == 200, f"Chat endpoint failed: {resp.status_code}"
    chat_res = resp.json()
    print(f"   Intent: {chat_res['intent']} (conf: {chat_res['intent_confidence']})")
    print(f"   Is Grounded: {chat_res['is_grounded']}")
    print(f"   Overall Confidence: {chat_res['overall_confidence']}")
    print(f"   Sources Cited: {len(chat_res['sources'])}")
    print(f"   Latency: {chat_res['latency_ms']}ms")
    print(f"   Answer snippet:\n   {chat_res['answer'][:200]}...")
    assert len(chat_res["answer"]) > 20
    results["full_chat_pipeline"] = "PASS"

    # 9. Feedback Submission & Retrieval
    print("\n9. Testing POST & GET /api/feedback...")
    fb_payload = {
        "query": "What is CS201?",
        "answer": chat_res["answer"][:100],
        "intent": chat_res["intent"],
        "feedback": "thumbs_up",
        "comments": "Excellent grounded answer from curriculum!"
    }
    resp = client.post("/api/feedback", json=fb_payload)
    assert resp.status_code == 200
    resp_get = client.get("/api/feedback")
    assert resp_get.status_code == 200
    print(f"   Feedback recorded and verified. Status: {resp.json().get('status')}")
    results["feedback"] = "PASS"

    print("\n" + "="*70)
    print("ALL API ENDPOINTS PASSED WITH 100% SUCCESS!")
    for test_name, status in results.items():
        print(f"  [x] {test_name:25s}: {status}")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_api_tests()
