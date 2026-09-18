"""
Unit tests for data preprocessing module.

Tests data validation, type conversion, missing value imputation, and clean data loading.
"""

import pytest
import pandas as pd
import numpy as np
from preprocessing.preprocessing import (
    validate_dataset_schema,
    clean_raw_dataset,
    preprocess_pipeline,
)


@pytest.fixture
def sample_raw_df():
    """Create a mock raw PaySim DataFrame for testing."""
    return pd.DataFrame({
        "step": [1, 1, 2, 3, 5],
        "type": ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"],
        "amount": [100.0, 50000.0, 25000.0, 50.0, 1000.0],
        "nameOrig": ["C1000", "C1001", "C1002", "C1003", "C1004"],
        "oldbalanceOrg": [500.0, 50000.0, 30000.0, 200.0, 500.0],
        "newbalanceOrig": [400.0, 0.0, 5000.0, 150.0, 1500.0],
        "nameDest": ["M2000", "C3000", "C3001", "M2001", "C3002"],
        "oldbalanceDest": [0.0, 0.0, 1000.0, 0.0, 500.0],
        "newbalanceDest": [0.0, 0.0, 26000.0, 0.0, 0.0],
        "isFraud": [0, 1, 0, 0, 0],
    })


def test_validate_dataset_schema_valid(sample_raw_df):
    """Test schema validation on valid DataFrame."""
    is_valid, missing = validate_dataset_schema(sample_raw_df)
    assert is_valid is True
    assert len(missing) == 0


def test_validate_dataset_schema_missing_col(sample_raw_df):
    """Test schema validation when a required column is missing."""
    df_missing = sample_raw_df.drop(columns=["amount"])
    is_valid, missing = validate_dataset_schema(df_missing)
    assert is_valid is False
    assert "amount" in missing


def test_clean_raw_dataset_handles_nulls_and_negatives():
    """Test that dirty records with nulls and negative amounts are handled."""
    dirty_df = pd.DataFrame({
        "step": [1, 2, 3],
        "type": ["PAYMENT", "TRANSFER", "CASH_OUT"],
        "amount": [100.0, -50.0, np.nan],
        "nameOrig": ["C1", "C2", "C3"],
        "oldbalanceOrg": [1000.0, 500.0, 200.0],
        "newbalanceOrig": [900.0, 550.0, 200.0],
        "nameDest": ["M1", "C2", "C3"],
        "oldbalanceDest": [0.0, 0.0, 0.0],
        "newbalanceDest": [0.0, 0.0, 0.0],
        "isFraud": [0, 1, 0],
    })
    cleaned = clean_raw_dataset(dirty_df)
    assert len(cleaned) > 0
    assert (cleaned["amount"] >= 0).all()
    assert cleaned["amount"].isnull().sum() == 0


def test_preprocess_pipeline_end_to_end(sample_raw_df):
    """Test full preprocessing pipeline execution."""
    df_proc = preprocess_pipeline(sample_raw_df)
    assert isinstance(df_proc, pd.DataFrame)
    assert not df_proc.empty
    assert "amount" in df_proc.columns
