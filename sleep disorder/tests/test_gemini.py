"""
Tests for Gemini Service and Offline Fallback Mechanism
"""
import pytest
from services.gemini_service import GeminiService

def test_gemini_service_initialization():
    service = GeminiService()
    assert hasattr(service, "generate_recommendations")
    assert hasattr(service, "chat")

def test_gemini_fallback_recommendations():
    service = GeminiService()
    dummy_pred = {
        "predicted_class": "Insomnia",
        "confidence": 85.5,
        "probabilities": {"None": 5.0, "Insomnia": 85.5, "Sleep Apnea": 9.5},
        "explanation": {
            "top_features": [
                {"feature_name": "Stress Level", "shap_value": 0.08, "direction": "Positive", "impact_description": "Elevates risk"},
                {"feature_name": "Sleep Duration", "shap_value": 0.07, "direction": "Positive", "impact_description": "Elevates risk"}
            ]
        },
        "input_summary": {
            "Age": 45, "Gender": "Female", "Occupation": "Teacher",
            "Sleep Duration": 5.0, "Quality of Sleep": 4, "Stress Level": 8,
            "Physical Activity Level": 30, "Daily Steps": 4000,
            "BMI Category": "Normal", "Systolic_BP": 125, "Diastolic_BP": 80,
            "Heart Rate": 75
        }
    }
    recs = service.generate_recommendations(dummy_pred)
    assert recs is not None
    assert len(recs) > 200
    assert "Insomnia" in recs
    assert "Sleep Hygiene" in recs or "Routine" in recs

def test_gemini_status_report():
    service = GeminiService()
    status = service.get_status()
    assert "is_connected" in status
    assert "mode" in status
    assert "sdk_version" in status
    assert "models_supported" in status
    assert "gemini-2.5-flash" in status["models_supported"]
