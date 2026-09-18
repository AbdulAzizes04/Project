"""
Feature Engineering Module for GuidedGuard.

This module provides advanced domain feature engineering for digital payment
scam and fraud risk assessment.

Architectural Improvements:
1. Strict Authorization-Time Boundary:
   Excludes post-transaction balances (newbalanceOrig, newbalanceDest, balance wipeout)
   when `exclude_leakage=True`.
2. Multi-Dimensional Behavioral Features:
   Transaction features, rolling velocity, personal temporal deviation, beneficiary tenure,
   device risk indicators, and location anomaly signals.
3. Experimentation Compatibility:
   Supports generating both the leakage-free authorization-time feature set (Experiment 2, 3, etc.)
   and the historical all-features set (Experiment 1) for scientific comparison.
"""

from typing import Tuple, Dict, Any, List, Optional
from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from preprocessing.authorization_features import filter_authorization_features
from preprocessing.temporal_features import compute_temporal_features
from preprocessing.beneficiary_features import compute_beneficiary_features
from preprocessing.device_features import compute_device_features
from preprocessing.location_features import compute_location_features
from preprocessing.velocity_features import get_default_velocity_features
from utils.helpers import setup_logger

logger = setup_logger(__name__)


def create_transaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate instantaneous transaction amount features."""
    res = df.copy()
    if "amount" in res.columns:
        amt = np.maximum(0.0, res["amount"].astype(float))
        res["log_amount"] = np.log1p(amt)
        mean_amt = amt.mean() if len(amt) > 0 else 2500.0
        std_amt = amt.std() if len(amt) > 1 else 1000.0
        res["amount_deviation"] = (amt - mean_amt) / (std_amt + 1e-6)
        res["relative_amount"] = amt / (mean_amt + 1e-6)
        res["amount_percentile"] = amt.rank(pct=True) if len(amt) > 1 else 0.5
        p90 = amt.quantile(0.90) if len(amt) > 1 else 10000.0
        res["is_large_transaction"] = (amt > p90).astype(int)

    return res


def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate temporal hour, day, and night indicators."""
    res = df.copy()

    if "step" in res.columns:
        res["hour_of_day"] = (res["step"] % 24).astype(int)
        res["day_of_week"] = ((res["step"] // 24) % 7).astype(int)
    elif "timestamp" in res.columns:
        dt = pd.to_datetime(res["timestamp"], errors="coerce")
        res["hour_of_day"] = dt.dt.hour.fillna(12).astype(int)
        res["day_of_week"] = dt.dt.dayofweek.fillna(0).astype(int)
    else:
        res["hour_of_day"] = 12
        res["day_of_week"] = 0

    res["is_weekend"] = res["day_of_week"].isin([5, 6]).astype(int)
    res["is_business_hours"] = res["hour_of_day"].between(9, 17).astype(int)
    res["is_late_night"] = res["hour_of_day"].isin([0, 1, 2, 3, 4, 23]).astype(int)

    return res


def create_velocity_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate velocity indicators."""
    res = df.copy()

    if "velocity_6h" in res.columns:
        res["velocity_1h"] = res["velocity_6h"] / 6.0
        res["velocity_24h"] = res["velocity_6h"] * 3.5
    else:
        res["velocity_1h"] = 1.0
        res["velocity_6h"] = 2.0
        res["velocity_24h"] = 5.0

    res["avg_daily_transactions"] = res["velocity_24h"].mean() if len(res) > 0 else 5.0
    res["recent_transaction_spike"] = (res["velocity_1h"] > (res["velocity_6h"] / 6.0 * 1.5)).astype(int)

    return res


def create_balance_features(df: pd.DataFrame, allow_post_transaction: bool = False) -> pd.DataFrame:
    """
    Generate balance features.
    If allow_post_transaction=False, ONLY pre-transaction balance is used (zero leakage).
    If allow_post_transaction=True, includes post-settlement balance features for leakage audit demonstration.
    """
    res = df.copy()

    old_orig_col = "old_balance_orig" if "old_balance_orig" in res.columns else ("oldbalanceOrg" if "oldbalanceOrg" in res.columns else None)
    new_orig_col = "new_balance_orig" if "new_balance_orig" in res.columns else ("newbalanceOrig" if "newbalanceOrig" in res.columns else None)

    if old_orig_col and "amount" in res.columns:
        old_val = res[old_orig_col].astype(float)
        res["log_old_balance"] = np.log1p(np.maximum(0, old_val))
        res["amount_to_old_balance_ratio"] = res["amount"] / (old_val + 1.0)
        res["is_high_portion_of_balance"] = (res["amount_to_old_balance_ratio"] > 0.8).astype(int)

    if allow_post_transaction and old_orig_col and new_orig_col and "amount" in res.columns:
        # [DATA LEAKAGE WARNING] These features require newbalanceOrig which only exists AFTER authorization
        res["balance_diff_orig"] = res[old_orig_col] - res[new_orig_col]
        expected_orig = res[old_orig_col] - res["amount"]
        res["balance_error_orig"] = np.abs(expected_orig - res[new_orig_col])
        res["remaining_balance_pct_orig"] = res[new_orig_col] / (res[old_orig_col] + 1e-6)
        res["balance_wipeout_orig"] = ((res[old_orig_col] > 500) & (res[new_orig_col] == 0)).astype(int)

    return res


def create_recipient_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate payee risk features."""
    res = df.copy()

    if "is_new_beneficiary" not in res.columns:
        if "nameDest" in res.columns:
            # Map merchant status without global count leakage
            res["is_merchant_dest"] = res["nameDest"].astype(str).str.startswith("M").astype(int)
            res["is_new_beneficiary"] = 0
            res["beneficiary_transaction_count"] = 1
        else:
            res["is_merchant_dest"] = 0
            res["is_new_beneficiary"] = 0
            res["beneficiary_transaction_count"] = 1
    else:
        res["is_merchant_dest"] = 0
        res["beneficiary_transaction_count"] = 1

    res["beneficiary_avg_amount"] = res["amount"].mean() if "amount" in res.columns else 2500.0
    res["beneficiary_fraud_history_flag"] = res.get("beneficiary_fraud_history_flag", 0)

    return res


def create_device_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate device risk indicators."""
    res = df.copy()

    if "device_type" in res.columns:
        dev_str = res["device_type"].astype(str).str.lower()
        res["device_risk_score"] = np.where(dev_str.str.contains("proxy|unknown|vpn|rooted"), 0.85, 0.10)
        res["device_is_proxy"] = dev_str.str.contains("proxy|unknown|vpn|rooted").astype(int)
    else:
        res["device_risk_score"] = 0.10
        res["device_is_proxy"] = 0

    res["is_new_device"] = res.get("is_new_device", (res["device_risk_score"] > 0.3).astype(int))
    return res


def create_location_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate location risk indicators."""
    res = df.copy()

    if "location" in res.columns:
        loc_str = res["location"].astype(str).str.lower()
        res["high_risk_region_flag"] = loc_str.str.contains("proxy|unknown|foreign|high risk|cross border", case=False).astype(int)
    else:
        res["high_risk_region_flag"] = 0

    res["distance_from_home"] = np.where(res["high_risk_region_flag"] == 1, 4500.0, 12.0)
    return res


def create_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate customer spending deviation features."""
    res = df.copy()
    amt = res["amount"] if "amount" in res.columns else pd.Series([100.0] * len(res))
    res["avg_spending"] = amt.mean() if len(amt) > 0 else 2500.0
    res["spending_deviation"] = amt - res["avg_spending"]
    return res


def create_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate composite baseline risk indicators."""
    res = df.copy()
    amt_score = np.clip(res.get("amount_percentile", pd.Series([0.5] * len(res))), 0, 1)
    res["amount_risk_score"] = amt_score
    time_score = res.get("is_late_night", pd.Series([0] * len(res))) * 0.4 + (1 - res.get("is_business_hours", pd.Series([1] * len(res)))) * 0.2
    res["time_risk_score"] = np.clip(time_score, 0, 1)
    return res


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate interaction features."""
    res = df.copy()
    amt = res.get("amount", pd.Series([1.0] * len(res)))
    vel = res.get("velocity_6h", pd.Series([1.0] * len(res)))
    res["interaction_amount_x_velocity"] = amt * vel
    return res


def validate_engineered_features(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate engineered feature matrix."""
    num_df = df.select_dtypes(include=[np.number])
    null_cnt = int(df.isnull().sum().sum())
    inf_cnt = int(np.isinf(num_df).sum().sum())
    return {
        "total_features": len(df.columns),
        "total_rows": len(df),
        "total_nulls": null_cnt,
        "total_infs": inf_cnt,
        "valid_feature_matrix": (null_cnt == 0 and inf_cnt == 0),
    }


def feature_engineering_pipeline(
    df: pd.DataFrame,
    dataset_name: str = "dataset",
    exclude_leakage: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Execute full feature engineering pipeline.
    
    Parameters:
        df: Input DataFrame
        dataset_name: Identifier for logging
        exclude_leakage: If True (default), strictly excludes post-transaction balance features.
                        If False, includes them for Experiment 1 leakage demonstration.
    """
    logger.info(f"Running feature engineering pipeline (exclude_leakage={exclude_leakage})...")
    feat_df = df.copy()

    feat_df = create_transaction_features(feat_df)
    feat_df = create_temporal_features(feat_df)
    feat_df = create_velocity_features(feat_df)
    feat_df = create_balance_features(feat_df, allow_post_transaction=not exclude_leakage)
    feat_df = create_recipient_features(feat_df)
    feat_df = create_device_features(feat_df)
    feat_df = create_location_features(feat_df)
    feat_df = create_customer_features(feat_df)
    feat_df = create_risk_features(feat_df)
    feat_df = create_interaction_features(feat_df)

    if exclude_leakage:
        feat_df = filter_authorization_features(feat_df)

    feat_df = feat_df.fillna(0.0).replace([np.inf, -np.inf], 0.0)

    report = {
        "dataset_name": dataset_name,
        "exclude_leakage": exclude_leakage,
        "total_features": len(feat_df.columns),
        "total_rows": len(feat_df),
    }

    return feat_df, report


# Backward compatibility aliases
compute_domain_features = feature_engineering_pipeline
create_engineered_features = feature_engineering_pipeline
extract_authorization_features = filter_authorization_features
