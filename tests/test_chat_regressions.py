from backend.pipeline import pipeline
from backend.rag.attribution import attribution_engine
from backend.rag.generator import answer_generator
from backend.rag.retriever import hybrid_retriever, embedding_service, vector_store
from backend.nlp.intent_classifier import intent_classifier
from backend.rag.reranker import reranker_service


def test_tied_ranks_prefer_lexical_evidence_and_keep_source_metadata(monkeypatch):
    monkeypatch.setattr(embedding_service, "get_query_embedding", lambda query: [0.0])
    monkeypatch.setattr(vector_store, "search", lambda **kwargs: [{"chunk_id": "noise", "text": "Graph traversal"}])
    monkeypatch.setattr(hybrid_retriever.bm25, "search", lambda *args, **kwargs: [
        {"chunk_id": "attendance", "text": "75% attendance", "source_document": "Rules.pdf", "page": 2}
    ])
    result = hybrid_retriever.retrieve("attendance", top_k=1)[0]
    assert result["chunk_id"] == "attendance"
    assert result["document_name"] == "Rules.pdf"
    assert result["page_number"] == 2


def test_citations_include_readable_source_excerpts():
    result = attribution_engine.calculate_confidence("attendance", "75% [Rules.pdf, Page 2]", {"intent": "attendance_rules", "confidence": .9}, {}, [
        {"chunk_id": "a", "text": "75% attendance is required.", "source_document": "Rules.pdf", "page": 2, "retrieval_score": .9, "rerank_score": .9}
    ])
    assert result["citations"][0]["document_id"] == "Rules.pdf"
    assert result["citations"][0]["content"] == "75% attendance is required."


def test_exact_lexical_candidate_survives_dense_overlap(monkeypatch):
    noise = [{"chunk_id": f"noise-{i}", "text": "Unrelated policy"} for i in range(8)]
    exact = {"chunk_id": "attendance", "text": "75% attendance is required"}
    monkeypatch.setattr(embedding_service, "get_query_embedding", lambda query: [0.0])
    monkeypatch.setattr(vector_store, "search", lambda **kwargs: noise)
    monkeypatch.setattr(hybrid_retriever.bm25, "search", lambda *args, **kwargs: [exact, *noise])
    assert "attendance" in {item["chunk_id"] for item in hybrid_retriever.retrieve("attendance", top_k=4)}


def test_irrelevant_tail_chunks_do_not_reach_answer_generation(monkeypatch):
    relevant = {"chunk_id": "rules", "text": "75% attendance", "rerank_score": .8, "retrieval_score": .8}
    irrelevant = {"chunk_id": "graphs", "text": "Graph traversal", "rerank_score": .1, "retrieval_score": .4}
    monkeypatch.setattr(intent_classifier, "predict", lambda query: {"intent": "attendance_rules", "confidence": .9})
    monkeypatch.setattr(hybrid_retriever, "retrieve", lambda **kwargs: [relevant, irrelevant])
    monkeypatch.setattr(reranker_service, "rerank", lambda **kwargs: [relevant, irrelevant])
    received = []

    def generate(**kwargs):
        received.extend(kwargs["chunks"])
        return "75% attendance"

    monkeypatch.setattr(answer_generator, "generate", generate)
    pipeline.process_query("minimum attendance")
    assert received == [relevant]


def test_local_answer_finds_the_requested_topic_beyond_document_heading():
    result = answer_generator._fallback_synthesis("How is CGPA calculated?", "academic_regulations", {}, [{
        "text": "OFFICIAL RULES\nAcademic Year 2025\nAttendance\nStudents need 75% attendance.\nExaminations\nPassing marks are 40.\nGrades\nCGPA is the credit-weighted average of grade points.\nCGPA includes all completed semesters.",
        "source_document": "Rules.pdf", "page": 3,
    }])
    assert "CGPA is the credit-weighted average" in result
    assert "[Rules.pdf, Page 3]" in result


def test_feedback_does_not_report_success_when_storage_fails(monkeypatch):
    from fastapi.testclient import TestClient
    import backend.main as main
    monkeypatch.setattr(main, "_append_log", lambda *args: False)
    response = TestClient(main.app).post("/api/feedback", json={
        "query": "Attendance?", "answer": "75%", "intent": "attendance_rules", "feedback": "thumbs_up"
    })
    assert response.status_code == 503


def test_local_reranker_does_not_confuse_minimum_attendance_with_minimum_spanning_trees():
    result = reranker_service._fallback_rerank("What is the minimum attendance requirement?", [
        {"chunk_id": "graphs", "text": "Minimum spanning trees and graph algorithms.", "retrieval_score": .9},
        {"chunk_id": "rules", "text": "Students must have 75% attendance.", "retrieval_score": .8},
    ], "attendance_rules")
    assert result[0]["chunk_id"] == "rules"
    assert result[0]["rerank_score"] >= .45
    assert result[1]["rerank_score"] < .45
