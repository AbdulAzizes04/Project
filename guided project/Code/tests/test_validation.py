"""
Unit tests for validation, temporal splitting, and leakage audit.

Tests chronological train/val/test splits, leakage detection rules, and evaluation metrics.
"""

import pytest
import pandas as pd
import numpy as np
from models.temporal_validation import temporal_train_val_test_split
from models.leakage_audit import LeakageAuditor
from models.evaluation import compute_classification_metrics, compute_precision_recall_at_k


def test_temporal_split_chronological_ordering():
    """Verify temporal split strictly maintains time order (train < val < test)."""
    df = pd.DataFrame({
        "step": list(range(1, 101)),
        "amount": [100.0] * 100,
        "isFraud": [0] * 90 + [1] * 10,
    })

    train_df, val_df, test_df, _ = temporal_train_val_test_split(
        df, time_col="step", train_ratio=0.6, val_ratio=0.2, test_ratio=0.2
    )

    assert train_df["step"].max() <= val_df["step"].min()
    assert val_df["step"].max() <= test_df["step"].min()
    assert len(train_df) + len(val_df) + len(test_df) == len(df)


def test_leakage_auditor_detects_post_transaction_features():
    """Verify leakage auditor flags known post-transaction columns."""
    auditor = LeakageAuditor()
    leaky_columns = [
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",      # leakage
        "newbalanceDest",      # leakage
        "balance_wipeout_orig" # leakage
    ]
    df = pd.DataFrame(np.zeros((5, len(leaky_columns))), columns=leaky_columns)
    audit_results = auditor.audit_dataframe(df, target_col="isFraud")

    flagged_names = [item["feature"] for item in audit_results["leaky_features"]]
    assert "newbalanceOrig" in flagged_names
    assert "newbalanceDest" in flagged_names
    assert "balance_wipeout_orig" in flagged_names
    assert "amount" not in flagged_names


def test_evaluation_metrics_computation():
    """Verify comprehensive metrics calculation."""
    y_true = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
    y_prob = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.7, 0.8, 0.85, 0.95])
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = compute_classification_metrics(y_true, y_pred, y_prob)

    assert "roc_auc" in metrics
    assert "pr_auc" in metrics
    assert "f1_score" in metrics
    assert "brier_score" in metrics
    assert metrics["roc_auc"] > 0.9
    assert metrics["pr_auc"] > 0.9


def test_precision_recall_at_k():
    """Verify Precision@K and Recall@K calculation."""
    y_true = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])

    pk, rk = compute_precision_recall_at_k(y_true, y_prob, k=2)
    assert pk == 1.0  # both top 2 are true positives
    assert rk == 1.0  # captured all 2 positives
