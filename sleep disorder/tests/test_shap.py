"""
Tests for SHAP Explainability Engine
"""
import numpy as np
import pytest
from ml.explain import SleepExplainer
from ml.predict import SleepPredictor

def test_shap_explainer_initialization():
    explainer = SleepExplainer()
    assert explainer.model is not None
    assert len(explainer.feature_names) > 0

def test_shap_explanation_generation():
    predictor = SleepPredictor()
    user_input = {
        "Age": 55,
        "Gender": "Male",
        "Occupation": "Doctor",
        "Sleep Duration": 5.0,
        "Quality of Sleep": 3,
        "Physical Activity Level": 20,
        "Stress Level": 9,
        "BMI Category": "Obese",
        "Systolic_BP": 145,
        "Diastolic_BP": 95,
        "Heart Rate": 88,
        "Daily Steps": 3500
    }
    result = predictor.predict(user_input, generate_shap=True)
    assert "explanation" in result
    shap_data = result["explanation"]
    assert "top_features" in shap_data
    assert len(shap_data["top_features"]) == 5
    assert "shap_plot_base64" in shap_data
    assert len(shap_data["shap_plot_base64"]) > 100
    assert "explanation_summary" in shap_data
