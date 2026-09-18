"""
Unit tests for feature engineering module.

Tests authorization feature extraction, leakage exclusion, and schema compliance.
"""

import pytest
import pandas as pd
import numpy as np
from preprocessing.feature_engineering import (
    feature_engineering_pipeline,
    extract_authorization_features,
)
from preprocessing.authorization_features import (
    filter_authorization_features,
    POST_TRANSACTION_LEAKAGE,
)


@pytest.fixture
def sample_transaction_df():
    """Create sample transaction DataFrame."""
    return pd.DataFrame({
        "step": [1, 2, 10, 24, 48],
        "type": ["TRANSFER", "CASH_OUT", "PAYMENT", "TRANSFER", "CASH_OUT"],
        "amount": [10000.0, 5000.0, 50.0, 200000.0, 500.0],
        "nameOrig": ["C101", "C102", "C103", "C101", "C104"],
        "oldbalanceOrg": [10000.0, 6000.0, 200.0, 200000.0, 1000.0],
        "newbalanceOrig": [0.0, 1000.0, 150.0, 0.0, 500.0],
        "nameDest": ["C901", "C902", "M903", "C904", "C905"],
        "oldbalanceDest": [0.0, 0.0, 0.0, 500.0, 100.0],
        "newbalanceDest": [0.0, 5000.0, 0.0, 200500.0, 600.0],
        "isFraud": [1, 0, 0, 1, 0],
    })


def test_feature_engineering_excludes_leakage(sample_transaction_df):
    """Verify that feature_engineering_pipeline with exclude_leakage=True removes leakage."""
    featured_df, _ = feature_engineering_pipeline(sample_transaction_df, exclude_leakage=True)

    # Assert no post-transaction leakage columns exist
    for col in POST_TRANSACTION_LEAKAGE:
        assert col not in featured_df.columns, f"Leakage column {col} was found in featured_df!"


def test_authorization_features_presence(sample_transaction_df):
    """Verify that authorization-time features are generated."""
    featured_df, _ = feature_engineering_pipeline(sample_transaction_df, exclude_leakage=True)

    expected_features = [
        "amount",
        "oldbalanceOrg",
        "hour_of_day",
        "amount_to_old_balance_ratio",
        "log_amount",
    ]
    for feat in expected_features:
        assert feat in featured_df.columns, f"Expected feature {feat} not in featured_df"


def test_filter_authorization_features():
    """Verify filter_authorization_features strictly strips post-transaction columns."""
    test_cols = [
        "amount", "oldbalanceOrg", "step", "type_TRANSFER",
        "newbalanceOrig", "newbalanceDest", "balance_wipeout_orig", "balance_error_orig",
        "velocity_1h", "customer_amount_mean"
    ]
    df = pd.DataFrame(np.zeros((3, len(test_cols))), columns=test_cols)
    clean_df = filter_authorization_features(df)

    assert "newbalanceOrig" not in clean_df.columns
    assert "newbalanceDest" not in clean_df.columns
    assert "balance_wipeout_orig" not in clean_df.columns
    assert "balance_error_orig" not in clean_df.columns
    assert "amount" in clean_df.columns
    assert "oldbalanceOrg" in clean_df.columns
