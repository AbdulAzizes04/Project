"""
Tests for REST API Endpoints
"""
import pytest
import json
from app import create_app
from database.models import db, User

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        # Check if patient exists
        u = User.query.filter_by(email="patient_test@sleepai.org").first()
        if not u:
            u = User(name="Test Patient", email="patient_test@sleepai.org", role="user")
            u.set_password("pass123")
            db.session.add(u)
            db.session.commit()
    return app.test_client()

def test_api_predict_endpoint(client):
    payload = {
        "Age": 38,
        "Gender": "Male",
        "Occupation": "Doctor",
        "Sleep Duration": 6.8,
        "Quality of Sleep": 7,
        "Physical Activity Level": 60,
        "Stress Level": 6,
        "BMI Category": "Normal",
        "Systolic_BP": 122,
        "Diastolic_BP": 82,
        "Heart Rate": 72,
        "Daily Steps": 7000
    }
    response = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "predicted_class" in data
    assert "confidence" in data
    assert "top_shap_factors" in data
    assert "disclaimer" in data

def test_api_model_performance(client):
    response = client.get("/admin/api/model-performance")
    assert response.status_code == 200
    data = response.get_json()
    assert "best_model_name" in data
    assert "models" in data
