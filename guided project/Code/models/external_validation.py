"""
External Validation Pipeline on Bank Account Fraud (BAF) Benchmark.

Tests whether the developed supervised modeling and feature scaling approach
generalizes to an independent real-world bank fraud benchmark dataset:
BAF (Bank Account Fraud Suite, NeurIPS 2022).

CRITICAL SCIENTIFIC INTEGRITY NOTE:
Performance on BAF does NOT directly measure Authorised Push Payment (APP) scam detection,
because BAF primarily captures synthetic identity and opening account fraud.
Instead, this experiment objectively evaluates how the modeling pipeline transfers to
another high-imbalance financial fraud benchmark.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    accuracy_score,
)

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from preprocessing.dataset_adapter import BAFAdapter
from utils.helpers import setup_logger

logger = setup_logger(__name__)


def run_baf_external_validation(
    baf_path: Optional[Path] = None,
    sample_limit: int = 20000,
) -> Dict[str, Any]:
    """
    Run validation experiment on BAF dataset using adapted features.
    """
    if baf_path is None:
        baf_path = config.RAW_DATA_DIR / "baf_base_dataset.csv"

    baf_path = Path(baf_path)
    if not baf_path.exists():
        logger.warning(f"BAF dataset not found at {baf_path}. Returning unavailable status.")
        return {
            "status": "UNAVAILABLE",
            "message": "External validation dataset (baf_base_dataset.csv) is unavailable locally.",
            "metrics": None,
        }

    logger.info(f"Executing BAF External Validation from {baf_path}...")
    df_raw = pd.read_csv(baf_path, nrows=sample_limit)

    X, y = BAFAdapter.adapt(df_raw)

    # Chronological or split
    n = len(X)
    split_idx = int(n * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Train model
    model = HistGradientBoostingClassifier(random_state=42, max_iter=100)
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    pos_rate = float(y.mean())
    pr_auc = float(average_precision_score(y_test, y_proba))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    acc = float(accuracy_score(y_test, y_pred))

    results = {
        "status": "COMPLETED",
        "dataset_name": "Bank Account Fraud (BAF - NeurIPS 2022)",
        "provenance": "Real-world European bank account opening and identity fraud benchmark.",
        "samples_evaluated": len(df_raw),
        "test_samples": len(X_test),
        "class_ratio_positive_pct": round(pos_rate * 100, 2),
        "model_used": "HistGradientBoostingClassifier",
        "features_used": list(X.columns),
        "metrics": {
            "PR-AUC": round(pr_auc, 4),
            "ROC-AUC": round(roc_auc, 4),
            "F1-Score": round(f1, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "Accuracy": round(acc, 4),
        },
        "scientific_disclaimer": (
            "This experiment measures how the modeling methodology transfers to an independent "
            "financial fraud benchmark. It does NOT claim that BAF performance directly measures APP scam detection."
        ),
    }

    logger.info(f"BAF External Validation Complete: PR-AUC={pr_auc:.4f}, ROC-AUC={roc_auc:.4f}, F1={f1:.4f}")
    return results


if __name__ == "__main__":
    res = run_baf_external_validation()
    print(res)
