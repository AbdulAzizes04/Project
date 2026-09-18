"""
Unit tests for Explainable AI (XAI) modules.

Tests SHAP, LIME, counterfactual recourse generation, and natural security narratives.
"""

import pytest
import numpy as np
from explainability.shap_explainer import explain_transaction_shap, generate_human_readable_summary
from explainability.counterfactual import CounterfactualEngine
from explainability.narrative_engine import SecurityNarrativeEngine


def test_shap_explanation_structure():
    """Test SHAP explanation output structure."""
    sample_features = {
        "amount": 25000.0,
        "oldbalanceOrg": 30000.0,
        "hour_of_day": 14,
        "amount_to_oldbalance_ratio": 0.83,
        "type_TRANSFER": 1.0,
    }
    shap_res = explain_transaction_shap(sample_features)

    assert "shap_values" in shap_res or "feature_contributions" in shap_res or "top_features" in shap_res


def test_human_readable_summary():
    """Test human readable summary from feature contributions."""
    contributions = {
        "amount_to_avg_ratio": 0.45,
        "customer_zscore_amount": 0.38,
        "is_new_payee": 0.25,
    }
    summaries = generate_human_readable_summary(contributions)
    assert len(summaries) > 0
    assert any("amount" in s.lower() or "payee" in s.lower() or "risk" in s.lower() for s in summaries)


def test_counterfactual_engine():
    """Test minimal actionable recourse generation."""
    cf_engine = CounterfactualEngine()
    current_state = {
        "amount": 75000.0,
        "is_new_payee": 1,
        "is_off_hours": 1,
        "is_new_device": 1,
        "risk_score": 88.0,
    }
    recourse = cf_engine.find_counterfactual(current_state, target_risk=30.0)

    assert "recourse_paths" in recourse
    assert len(recourse["recourse_paths"]) > 0
    first_path = recourse["recourse_paths"][0]
    assert "recommended_changes" in first_path
    assert "projected_risk_score" in first_path
    assert first_path["projected_risk_score"] < current_state["risk_score"]


def test_security_narrative_engine():
    """Test natural security narrative generation."""
    narrative_engine = SecurityNarrativeEngine()
    signals = {
        "supervised_prob": 0.89,
        "behavioral_score": 85.0,
        "anomaly_score": 78.0,
        "beneficiary_risk": 90.0,
        "top_features": [("amount_to_avg_ratio", 0.42), ("is_new_payee", 0.31)],
    }
    narrative = narrative_engine.generate_narrative(
        risk_score=85.0,
        risk_level="CRITICAL",
        signals=signals,
    )

    assert "executive_summary" in narrative
    assert "key_risk_drivers" in narrative
    assert "recommended_actions" in narrative
    # Academic/calibrated wording check: should avoid claiming absolute proof
    assert "proves" not in narrative["executive_summary"].lower()
