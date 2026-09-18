"""Unit & Integration tests for Authentication endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_register_citizen_success(client: TestClient):
    payload = {
        "email": "newcitizen@example.com",
        "password": "Password@123",
        "full_name": "Priya Patel",
        "phone": "9811223344",
        "role": "citizen",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["full_name"] == payload["full_name"]
    assert "tokens" in data
    assert "access_token" in data["tokens"]


def test_register_duplicate_email(client: TestClient, test_citizen_user):
    payload = {
        "email": test_citizen_user.email,
        "password": "Password@123",
        "full_name": "Duplicate User",
        "phone": "9800000000",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_login_success(client: TestClient, test_citizen_user):
    payload = {
        "email": test_citizen_user.email,
        "password": "Citizen@123",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert data["user"]["email"] == test_citizen_user.email


def test_login_invalid_credentials(client: TestClient, test_citizen_user):
    payload = {
        "email": test_citizen_user.email,
        "password": "WrongPassword!99",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_get_current_user_profile(client: TestClient, citizen_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testcitizen@gmail.com"
    assert data["role"] == "citizen"
