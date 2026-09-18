"""
Unit tests for single and batch prediction pipelines.

Tests inference execution, output schema, risk fusion integration, and latency boundaries.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from models.predict import predict_transaction, predict_batch_transactions


def test_predict_single_legitimate_transaction():
    """Test single transaction prediction on low-risk input."""
    input_data = {
        "amount": 150.0,
        "oldbalanceOrg": 5000.0,
        "type": "PAYMENT",
        "step": 12,
        "nameOrig": "C123456",
        "nameDest": "M987654",
        "is_new_device": 0,
        "is_new_location": 0,
    }
    result = predict_transaction(input_data)

    assert "prediction" in result
    assert "risk_score" in result
    assert "risk_level" in result
    assert "probability" in result
    assert "anomaly_score" in result
    assert "fusion" in result
    assert "intervention" in result
    assert "latency_ms" in result
    assert result["latency_ms"] < 5000.0  # reasonable latency ceiling for cold-start test execution
    assert 0.0 <= result["risk_score"] <= 100.0


def test_predict_single_scam_transaction():
    """Test single transaction prediction on elevated scam-consistent input."""
    input_data = {
        "amount": 95000.0,
        "oldbalanceOrg": 95000.0,
        "type": "TRANSFER",
        "step": 2,  # early hour
        "nameOrig": "C999888",
        "nameDest": "C111222",
        "is_new_beneficiary": 1,
        "device_type": "Unknown Proxy",
        "location": "Foreign Proxy",
        "velocity_6h": 8,
        "is_new_device": 1,
        "is_new_location": 1,
    }
    result = predict_transaction(input_data)

    assert result["risk_score"] >= 40.0
    assert result["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]
    assert "intervention" in result


def test_predict_batch_transactions():
    """Test batch inference with a temporary CSV."""
    df_sample = pd.DataFrame([
        {"step": 10, "type": "PAYMENT", "amount": 50.0, "oldbalanceOrg": 2000.0, "nameOrig": "C1", "nameDest": "M1"},
        {"step": 12, "type": "TRANSFER", "amount": 80000.0, "oldbalanceOrg": 85000.0, "nameOrig": "C2", "nameDest": "C3"},
        {"step": 15, "type": "CASH_OUT", "amount": 200.0, "oldbalanceOrg": 1500.0, "nameOrig": "C4", "nameDest": "M2"},
    ])

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df_sample.to_csv(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        batch_res = predict_batch_transactions(tmp_path)
        assert batch_res["total_transactions"] == 3
        assert "avg_risk_score" in batch_res
        assert "flagged_scam_count" in batch_res
        assert Path(batch_res["prediction_csv"]).exists()
    finally:
        Path(tmp_path).unlink(missing_ok=True)
