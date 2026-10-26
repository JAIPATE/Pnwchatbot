import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "PNW" in data["system"]

def test_campuses_endpoint():
    response = client.get("/api/campuses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    codes = [c["code"] for c in data]
    assert "HAMMOND" in codes
    assert "WESTVILLE" in codes

def test_schedule_endpoint():
    response = client.get("/api/schedule?term=FALL_2026")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    event_names = [e["event_name"] for e in data]
    assert any("100%" in name or "Refund" in name for name in event_names)

def test_prerequisites_endpoint():
    response = client.get("/api/prerequisites?course_code=CS%2030200")
    assert response.status_code == 200
    data = response.json()
    assert data["target_course"] == "CS 30200"
    assert len(data["prerequisites"]) > 0
    prereq_codes = [p["prerequisite_code"] for p in data["prerequisites"]]
    assert "CS 18000" in prereq_codes

def test_chat_policy_query():
    payload = {"query": "How do I pay a parking ticket at PNW?", "campus_id": 1}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is True
    assert len(data["citations"]) > 0
    assert "parking" in data["response_text"].lower()

def test_chat_failsafe_guardrail():
    payload = {"query": "What is the secret recipe for baking a chocolate cake?", "campus_id": 1}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is False
    assert len(data["citations"]) == 0
    assert "sorry" in data["response_text"].lower()
    assert "deanofstudents@pnw.edu" in data["response_text"].lower()
