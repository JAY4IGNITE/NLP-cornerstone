"""Contracts used by the student workspace, without hosted model services."""
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_demo_query_returns_evidence_without_placeholder_page_numbers():
    response = client.post('/api/query', json={'query': 'What is the minimum attendance requirement?'})
    assert response.status_code == 200
    result = response.json()
    assert 'attendance' in result['answer'].lower()
    assert result['intent'] == 'attendance_rules'
    assert 0 <= result['confidence'] <= 1
    assert result['sources']
    assert all(source['document'] for source in result['sources'])
    assert all('page' not in source for source in result['sources'])


def test_demo_rejects_blank_and_oversized_questions():
    for query in ['', '   ', 'a' * 2001]:
        assert client.post('/api/query', json={'query': query}).status_code == 422


def test_health_describes_the_actual_default_pipeline():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    assert response.json()['mode'] == 'deterministic_demo'


def test_advanced_chat_route_preserves_the_incoming_contract(monkeypatch):
    from backend.pipeline import pipeline
    expected = {'answer': 'Curriculum answer', 'sources': [], 'intent_confidence': 0.8}
    received = {}

    def process_query(**kwargs):
        received.update(kwargs)
        return expected

    monkeypatch.setattr(pipeline, 'process_query', process_query)
    response = client.post('/api/chat', json={'query': 'Course credits?', 'chat_history': [], 'top_k': 3})
    assert response.status_code == 200
    assert response.json() == expected
    assert received == {'query': 'Course credits?', 'chat_history': [], 'top_k': 3}
