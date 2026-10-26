from backend.services.rag_service import generate_rag_answer, compute_similarity, FAIL_SAFE_REFUSAL

def test_compute_similarity():
    score1 = compute_similarity("parking ticket", "How to pay a parking ticket at PNW bursar office")
    assert score1 > 0.4
    
    score2 = compute_similarity("quantum physics black hole", "Parking rules and regulations for Hammond campus")
    assert score2 < 0.2

def test_rag_grounded_answer():
    res = generate_rag_answer("What are the drop deadlines for Fall 2026 semester?", campus_id=1)
    assert res["is_grounded"] is True
    assert len(res["citations"]) > 0
    assert "Fall 2026" in res["response_text"] or "Refund" in res["response_text"]

def test_rag_failsafe_refusal():
    res = generate_rag_answer("Tell me about alien UFO sightings in area 51", campus_id=1)
    assert res["is_grounded"] is False
    assert len(res["citations"]) == 0
    assert res["response_text"] == FAIL_SAFE_REFUSAL
