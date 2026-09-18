"""Unit & Integration tests for AI API endpoints and services."""
import pytest
from fastapi.testclient import TestClient


def test_classify_endpoint_fallback_or_model(client: TestClient, citizen_token):
    payload = {
        "text": "The streetlight is not working for the last 2 weeks and road is pitch dark at night"
    }
    response = client.post(
        "/api/ai/classify",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "confidence" in data
    assert data["category"] in [
        "Street Lighting", "Roads", "Water Supply", "Sanitation", "Electricity", "Drainage"
    ]


def test_priority_endpoint(client: TestClient, citizen_token):
    payload = {
        "text": "Urgent emergency! Live high tension electric wire snapped and hanging over school gate, children at risk",
        "category": "Electricity",
    }
    response = client.post(
        "/api/ai/priority",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "priority" in data
    assert data["priority"] in ["Critical", "High", "Medium", "Low"]


def test_full_analyze_pipeline(client: TestClient, citizen_token, test_department):
    payload = {
        "text": "Deep dangerous pothole on 80 feet road near bus stop caused multiple two wheeler accidents",
        "location": "80 feet road",
    }
    response = client.post(
        "/api/ai/analyze",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "priority" in data
    assert "duplicate" in data
    assert data["classification"]["category"] in [
        "Street Lighting", "Roads", "Water Supply", "Sanitation", "Electricity", "Drainage"
    ]
    assert data["priority"]["priority"] in ["Critical", "High", "Medium", "Low"]
