"""
Unit tests for user behavioral profiling module.

Tests baseline calculation, deviation scoring, cold-start handling, and recipient novelty.
"""

import pytest
import pandas as pd
import numpy as np
from preprocessing.behavioral_profile import UserBehavioralProfiler


@pytest.fixture
def historical_transactions():
    """Create historical transactions for a user."""
    return pd.DataFrame({
        "nameOrig": ["C1001"] * 10 + ["C1002"] * 5,
        "amount": [100.0, 150.0, 120.0, 110.0, 130.0, 140.0, 90.0, 115.0, 125.0, 105.0] + [500.0, 600.0, 550.0, 520.0, 580.0],
        "step": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 3, 5, 7, 9],
        "nameDest": ["M2001", "M2002", "M2001", "M2003", "M2001", "M2002", "M2001", "M2002", "M2003", "M2001"] + ["M3001"] * 5,
        "device_id": ["DEV_A"] * 10 + ["DEV_B"] * 5,
        "location_region": ["REG_NORTH"] * 10 + ["REG_SOUTH"] * 5,
    })


def test_profiler_fit(historical_transactions):
    """Test profiler fitting on historical transactions."""
    profiler = UserBehavioralProfiler()
    profiler.fit(historical_transactions)

    assert "C1001" in profiler.customer_profiles
    profile = profiler.customer_profiles["C1001"]
    assert profile["tx_count"] == 10
    assert 110.0 < profile["mean_amount"] < 130.0
    assert "M2001" in profile["known_recipients"]
    assert "DEV_A" in profile["known_devices"]


def test_profiler_deviation_scoring_normal(historical_transactions):
    """Test deviation computation for a normal transaction."""
    profiler = UserBehavioralProfiler()
    profiler.fit(historical_transactions)

    normal_tx = {
        "nameOrig": "C1001",
        "amount": 120.0,
        "step": 12,
        "nameDest": "M2001",
        "device_id": "DEV_A",
        "location_region": "REG_NORTH",
    }
    dev = profiler.compute_deviations(normal_tx)

    assert dev["amount_to_avg_ratio"] < 2.0
    assert abs(dev["customer_zscore_amount"]) < 2.0
    assert dev["is_new_payee"] == 0
    assert dev["is_new_device"] == 0
    assert dev["is_new_location"] == 0


def test_profiler_deviation_scoring_anomaly(historical_transactions):
    """Test deviation computation for a highly anomalous transaction (scam indicator)."""
    profiler = UserBehavioralProfiler()
    profiler.fit(historical_transactions)

    scam_tx = {
        "nameOrig": "C1001",
        "amount": 50000.0,  # massive spike
        "step": 14,
        "nameDest": "M9999_NEW",  # new payee
        "device_id": "DEV_UNKNOWN",  # new device
        "location_region": "REG_FOREIGN",  # new location
    }
    dev = profiler.compute_deviations(scam_tx)

    assert dev["amount_to_avg_ratio"] > 10.0
    assert dev["customer_zscore_amount"] > 3.0
    assert dev["is_new_payee"] == 1
    assert dev["is_new_device"] == 1
    assert dev["is_new_location"] == 1


def test_profiler_cold_start():
    """Test profiler behavior with an unknown customer (cold-start)."""
    profiler = UserBehavioralProfiler()
    # Don't fit or fit with different customer
    unknown_tx = {
        "nameOrig": "C_BRAND_NEW",
        "amount": 5000.0,
        "step": 1,
        "nameDest": "M9999",
        "device_id": "DEV_X",
        "location_region": "REG_Y",
    }
    dev = profiler.compute_deviations(unknown_tx)

    assert dev["is_cold_start"] == 1
    assert dev["is_new_payee"] == 1
    assert dev["is_new_device"] == 1
