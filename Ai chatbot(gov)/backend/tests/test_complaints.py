"""Unit & Integration tests for Complaint endpoints and lifecycle."""
import pytest
from fastapi.testclient import TestClient


def test_create_and_track_complaint(client: TestClient, citizen_token, test_department):
    payload = {
        "title": "Continuous sewage pipeline overflow on 5th cross road",
        "description": "The main sewer line has burst and dirty foul smelling water is flooding the street for 3 days.",
        "category": "Water Supply",
        "location": "Sector 4, Main Market Road",
        "landmark": "Opposite SBI Bank",
        "pincode": "560001",
    }
    response = client.post(
        "/api/complaints/",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "ticket_number" in data
    assert data["status"] in ["submitted", "ai_analyzed"]
    assert data["category"] == "Water Supply"
    ticket_no = data["ticket_number"]

    # Track complaint by ticket number (public tracking)
    track_resp = client.get(f"/api/complaints/track/{ticket_no}")
    assert track_resp.status_code == 200
    track_data = track_resp.json()
    assert track_data["ticket_number"] == ticket_no
    assert track_data["status"] in ["submitted", "ai_analyzed"]


def test_list_citizen_complaints(client: TestClient, citizen_token):
    response = client.get(
        "/api/complaints/my",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_update_status(client: TestClient, citizen_token, admin_token, test_department):
    # 1. Citizen creates complaint
    create_resp = client.post(
        "/api/complaints/",
        json={
            "title": "Dangerous dangling electric wires after storm",
            "description": "High voltage wire snapped and is hanging at pedestrian height near community park.",
            "category": "Water Supply",
            "location": "Park Road, Cross 2",
        },
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert create_resp.status_code == 201
    complaint_id = create_resp.json()["id"]

    # 2. Admin updates status to in_progress
    update_resp = client.patch(
        f"/api/complaints/{complaint_id}/status",
        json={"status": "in_progress", "remarks": "Field technician dispatched to site"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "in_progress"
