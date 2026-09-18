"""
Data Leakage Audit Pipeline for GuidedGuard.

This module performs systematic auditing of feature representations to identify:
1. Target Leakage:
   Features directly or indirectly derived from ground truth fraud labels.
2. Post-Transaction Leakage:
   Variables that only exist or update AFTER transaction clearing/settlement
   (e.g., newbalanceOrig, newbalanceDest, balance_wipeout_orig, balance_error_orig).
3. Duplicate Record Leakage:
   Identical or near-identical records spanning train, validation, and test splits.
4. Temporal Leakage:
   Future transaction information bleeding into historical training intervals
   (e.g., global frequency aggregations, out-of-order splits).

Exports:
- outputs/reports/leakage_audit.json
- outputs/reports/leakage_audit.csv
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import json
import sys
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from preprocessing.authorization_features import (
    POST_TRANSACTION_FEATURES,
    PRE_TRANSACTION_FEATURES,
    TRANSACTION_TIME_FEATURES,
    audit_feature_availability,
)
from utils.helpers import setup_logger

logger = setup_logger(__name__)


def audit_feature_leakage(df: pd.DataFrame, target_col: str = "isFraud") -> pd.DataFrame:
    """
    Produce a comprehensive feature-by-feature leakage audit table.
    """
    rows = []
    
    for col in df.columns:
        if col == target_col:
            rows.append({
                "Feature": col,
                "Source": "Dataset Target Label",
                "Available Before Authorization?": "NO",
                "Potential Leakage?": "TARGET",
                "Reason": "Ground truth classification target label.",
                "Action": "ISOLATE_AS_TARGET",
            })
            continue

        col_lower = col.lower()
        # Check explicit post-transaction list
        if any(post.lower() == col_lower for post in POST_TRANSACTION_FEATURES):
            rows.append({
                "Feature": col,
                "Source": "Core Settlement Accounting",
                "Available Before Authorization?": "NO",
                "Potential Leakage?": "YES (CRITICAL)",
                "Reason": "Post-settlement account state. Reveals whether funds left origin/reached destination.",
                "Action": "REMOVE",
            })
        elif "wipeout" in col_lower or "balance_error" in col_lower or "balance_diff" in col_lower or "remaining_balance" in col_lower:
            rows.append({
                "Feature": col,
                "Source": "Engineered Balance Calculation",
                "Available Before Authorization?": "NO",
                "Potential Leakage?": "YES (SEVERE)",
                "Reason": "Derived directly from post-settlement balance. Causes artificial 100% fraud classification.",
                "Action": "REMOVE",
            })
        elif col in ["isFlaggedFraud", "is_flagged_fraud", "chargeback_status"]:
            rows.append({
                "Feature": col,
                "Source": "Downstream Anti-Fraud Resolution",
                "Available Before Authorization?": "NO",
                "Potential Leakage?": "YES",
                "Reason": "Downstream rule engine flag assigned during/after fraud processing.",
                "Action": "REMOVE",
            })
        elif col in ["nameOrig", "nameDest", "transaction_id", "customer_id"]:
            rows.append({
                "Feature": col,
                "Source": "Transaction Identifier",
                "Available Before Authorization?": "YES",
                "Potential Leakage?": "POSSIBLE (OVERFITTING)",
                "Reason": "High-cardinality nominal ID. Not a direct target leak but causes memorization if unencoded.",
                "Action": "EXTRACT_FEATURES_THEN_DROP_RAW_ID",
            })
        elif any(pre.lower() == col_lower for pre in PRE_TRANSACTION_FEATURES):
            rows.append({
                "Feature": col,
                "Source": "Customer Historical Baseline",
                "Available Before Authorization?": "YES",
                "Potential Leakage?": "NO",
                "Reason": "Computed strictly from historical events prior to the transaction.",
                "Action": "KEEP",
            })
        else:
            rows.append({
                "Feature": col,
                "Source": "Authorization-Time Transaction Context",
                "Available Before Authorization?": "YES",
                "Potential Leakage?": "NO",
                "Reason": "Parameter observable at payment submission time.",
                "Action": "KEEP",
            })

    audit_df = pd.DataFrame(rows)
    return audit_df


def audit_duplicate_records(
    df_train: pd.DataFrame, df_val: pd.DataFrame, df_test: pd.DataFrame
) -> Dict[str, Any]:
    """
    Check for exact record duplicates across train, validation, and test splits.
    """
    n_train_dup = int(df_train.duplicated().sum())
    n_val_dup = int(df_val.duplicated().sum())
    n_test_dup = int(df_test.duplicated().sum())

    # Check cross-split overlap
    # We convert rows to tuples or use string representation on feature subset
    train_set = set(tuple(x) for x in df_train.select_dtypes(include=[np.number]).iloc[:5000].values)
    val_set = set(tuple(x) for x in df_val.select_dtypes(include=[np.number]).iloc[:2000].values)
    test_set = set(tuple(x) for x in df_test.select_dtypes(include=[np.number]).iloc[:2000].values)

    train_val_overlap = len(train_set.intersection(val_set))
    train_test_overlap = len(train_set.intersection(test_set))

    return {
        "train_internal_duplicates": n_train_dup,
        "val_internal_duplicates": n_val_dup,
        "test_internal_duplicates": n_test_dup,
        "train_val_sample_overlap": train_val_overlap,
        "train_test_sample_overlap": train_test_overlap,
        "has_cross_split_contamination": (train_val_overlap > 0 or train_test_overlap > 0),
    }


def audit_temporal_leakage(df: pd.DataFrame, step_col: str = "step") -> Dict[str, Any]:
    """
    Verify chronological ordering and detect if future step records influence past steps.
    """
    if step_col not in df.columns:
        return {"step_present": False, "temporal_leakage_detected": False}

    steps = df[step_col].values
    is_sorted = bool(np.all(np.diff(steps) >= 0))
    min_step = int(steps.min())
    max_step = int(steps.max())

    return {
        "step_present": True,
        "min_step": min_step,
        "max_step": max_step,
        "is_chronologically_sorted": is_sorted,
        "temporal_ordering_action": "ENFORCE_CHRONOLOGICAL_SPLIT",
    }


def run_complete_leakage_audit(
    dataset_path: Path = config.PROCESSED_DATA_DIR / "paysim_featured.csv",
    output_dir: Path = config.OUTPUTS_DIR / "reports",
) -> Dict[str, Any]:
    """
    Run the end-to-end data leakage audit pipeline and export reports.
    """
    logger.info(f"Starting Data Leakage Audit on {dataset_path}...")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not Path(dataset_path).exists():
        dataset_path = config.RAW_DATA_DIR / "paysim_transactions.csv"

    df = pd.read_csv(dataset_path)
    target = "isFraud" if "isFraud" in df.columns else ("fraud_bool" if "fraud_bool" in df.columns else df.columns[-1])

    # 1. Feature Availability & Post-Transaction Audit
    feature_audit_df = audit_feature_leakage(df, target_col=target)
    csv_report_path = output_dir / "leakage_audit.csv"
    feature_audit_df.to_csv(csv_report_path, index=False)

    leaking_features = feature_audit_df[feature_audit_df["Potential Leakage?"].str.contains("YES")]["Feature"].tolist()
    kept_features = feature_audit_df[feature_audit_df["Action"] == "KEEP"]["Feature"].tolist()

    # 2. Temporal Audit
    temporal_audit = audit_temporal_leakage(df, step_col="step" if "step" in df.columns else "")

    # 3. Overall Summary JSON
    summary = {
        "dataset_analyzed": str(Path(dataset_path).name),
        "total_columns_inspected": len(df.columns),
        "leaking_features_count": len(leaking_features),
        "leaking_features": leaking_features,
        "safe_authorization_features_count": len(kept_features),
        "safe_authorization_features": kept_features,
        "temporal_audit": temporal_audit,
        "post_transaction_leakage_impact": (
            "CRITICAL: Using newbalanceOrig/newbalanceDest or balance wipeout features allows "
            "classifiers to trivially achieve artificial 100% metrics by observing post-settlement state. "
            "These features must be permanently excluded from production authorization models."
        ),
        "report_generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    json_report_path = output_dir / "leakage_audit.json"
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    logger.info(f"Leakage audit completed. Found {len(leaking_features)} leaking features. Report: {json_report_path}")
    return summary


class LeakageAuditor:
    """Class interface for auditing feature leakage in DataFrames."""

    def audit_dataframe(self, df: pd.DataFrame, target_col: str = "isFraud") -> Dict[str, Any]:
        """Audit DataFrame columns for target, post-transaction, and temporal leakage."""
        audit_df = audit_feature_leakage(df, target_col=target_col)
        leaky = audit_df[audit_df["Potential Leakage?"].str.contains("YES|TARGET", case=False)]
        leaky_features = [{"feature": r["Feature"], "type": r["Potential Leakage?"]} for _, r in leaky.iterrows()]
        return {
            "total_features": len(df.columns),
            "leaky_features": leaky_features,
            "is_clean": len(leaky_features) == 0,
        }


if __name__ == "__main__":
    run_complete_leakage_audit()
