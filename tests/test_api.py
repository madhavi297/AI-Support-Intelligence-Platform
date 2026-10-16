"""
Integration tests for FastAPI REST API endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["classifier_ready"] is True
    assert data["knowledge_base_chunks"] > 0


def test_create_and_get_ticket():
    # 1. Create ticket
    payload = {
        "title": "Cannot login to dashboard",
        "description": "Password reset token expired and user is locked out"
    }
    create_resp = client.post("/tickets", json=payload)
    assert create_resp.status_code == 201
    ticket = create_resp.json()
    assert "ticket_code" in ticket
    assert ticket["status"] == "open"
    ticket_id = ticket["id"]

    # 2. Get ticket by ID
    get_resp = client.get(f"/tickets/{ticket_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["ticket_code"] == ticket["ticket_code"]


def test_ticket_not_found():
    response = client.get("/tickets/999999")
    assert response.status_code == 404


def test_ticket_validation_error():
    # Title too short (< 3 chars)
    response = client.post("/tickets", json={"title": "hi", "description": "short"})
    assert response.status_code == 422


def test_analyze_and_draft_ticket_flow():
    # 1. Create ticket
    create_resp = client.post("/tickets", json={
        "title": "Double charge on Visa credit card",
        "description": "I see two $49.99 charges for this month. Please refund one."
    })
    ticket_id = create_resp.json()["id"]

    # 2. Analyze
    analyze_resp = client.post(f"/tickets/{ticket_id}/analyze")
    assert analyze_resp.status_code == 200
    analysis = analyze_resp.json()
    assert analysis["predicted_category"] == "Billing"
    assert len(analysis["relevant_knowledge"]) > 0

    # 3. Draft response
    draft_resp = client.post(f"/tickets/{ticket_id}/draft-response", json={})
    assert draft_resp.status_code == 200
    draft_data = draft_resp.json()
    assert "draft_response" in draft_data
    assert len(draft_data["citations"]) > 0

    # 4. Verify ticket state updated in DB
    ticket_check = client.get(f"/tickets/{ticket_id}").json()
    assert ticket_check["status"] == "analyzed"
    assert ticket_check["category"] == "Billing"


def test_human_override_patch():
    create_resp = client.post("/tickets", json={
        "title": "General product inquiry",
        "description": "Just wondering about standard features"
    })
    ticket_id = create_resp.json()["id"]

    patch_resp = client.patch(f"/tickets/{ticket_id}", json={
        "category": "General Inquiry",
        "priority": "Low",
        "status": "resolved"
    })
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["category"] == "General Inquiry"
    assert data["priority"] == "Low"
    assert data["status"] == "resolved"


def test_knowledge_search_endpoint():
    resp = client.get("/knowledge/search", params={"query": "refund duplicate charge", "top_k": 2})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    assert "source" in results[0]


def test_ml_metrics_endpoint():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "accuracy" in data
    assert data["accuracy"] > 0.5
