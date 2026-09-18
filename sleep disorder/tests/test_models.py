"""
Tests for Model Loading, Inference, and Metrics
"""
import os
import joblib
import numpy as np
import pytest
from ml.predict import SleepPredictor

def test_model_files_exist():
    assert os.path.exists("models/best_model.pkl"), "best_model.pkl missing"
    assert os.path.exists("models/preprocessor.pkl"), "preprocessor.pkl missing"
    assert os.path.exists("models/feature_names.pkl"), "feature_names.pkl missing"
    assert os.path.exists("models/model_metrics.json"), "model_metrics.json missing"

def test_sleep_predictor_inference():
    predictor = SleepPredictor()
    user_input = {
        "Age": 30,
        "Gender": "Male",
        "Occupation": "Engineer",
        "Sleep Duration": 7.5,
        "Quality of Sleep": 8,
        "Physical Activity Level": 60,
        "Stress Level": 4,
        "BMI Category": "Normal",
        "Systolic_BP": 120,
        "Diastolic_BP": 80,
        "Heart Rate": 70,
        "Daily Steps": 8000
    }
    result = predictor.predict(user_input, generate_shap=False)
    assert "predicted_class" in result
    assert result["predicted_class"] in ["None", "Insomnia", "Sleep Apnea"]
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 100
    assert "probabilities" in result
    assert len(result["probabilities"]) == 3
