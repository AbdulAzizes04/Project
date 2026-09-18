"""
Tests for Clinical Edge Cases and Input Validation
"""
import pytest
from services.prediction_service import PredictionService
from ml.predict import SleepPredictor

def test_extreme_bmi_and_sleep_duration():
    predictor = SleepPredictor()
    extreme_input = {
        "Age": 65,
        "Gender": "Male",
        "Occupation": "Manager",
        "Sleep Duration": 3.2,
        "Quality of Sleep": 2,
        "Physical Activity Level": 10,
        "Stress Level": 10,
        "BMI Category": "Obese",
        "Systolic_BP": 160,
        "Diastolic_BP": 100,
        "Heart Rate": 95,
        "Daily Steps": 1200
    }
    result = predictor.predict(extreme_input, generate_shap=True)
    assert result["predicted_class"] in ["Insomnia", "Sleep Apnea"]
    assert result["confidence"] > 50

def test_input_validation_catches_invalid_ranges():
    service = PredictionService()
    invalid_data = {
        "Age": 150,                 # Invalid age
        "Sleep Duration": 22.0,     # Invalid duration
        "Quality of Sleep": 15,     # Range is 1-10
        "Stress Level": 0,          # Range is 1-10
        "Physical Activity Level": 800,
        "Systolic_BP": 300,
        "Diastolic_BP": 20,
        "Heart Rate": 250,
        "Daily Steps": 999999
    }
    is_valid, errors = service.validate_input(invalid_data)
    assert is_valid is False
    assert "Age" in errors
    assert "Sleep Duration" in errors
    assert "Quality of Sleep" in errors
    assert "Stress Level" in errors
