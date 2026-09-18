"""
Authorization-Time Feature Definitions & Schema Validation for GuidedGuard.

This module enforces a strict architectural distinction between data available
BEFORE payment authorization and information generated POST-settlement.

Feature Availability Categories:
1. PRE_TRANSACTION:
   Historical customer baselines, established beneficiaries, past device trust,
   and prior transaction cadence known before the payment request is submitted.
2. TRANSACTION_TIME:
   Instantaneous transaction parameters observed at the moment of payment authorization:
   amount, payment type, destination account identifier, client device signature,
   IP/location proxy, and current timestamp.
3. POST_TRANSACTION:
   Information resulting from transaction execution and settlement:
   final account balance, destination final balance, clearing status, chargeback
   flags, and fraud investigation outcomes.

CRITICAL POLICY:
Only PRE_TRANSACTION and TRANSACTION_TIME features may be ingested by the
primary risk scoring and machine learning models. POST_TRANSACTION features
are strictly flagged as data leakage and removed.
"""

from typing import List, Dict, Any
import pandas as pd

# Feature Category Definitions
PRE_TRANSACTION_FEATURES = [
    # Customer baseline stats
    "user_avg_amount",
    "user_median_amount",
    "user_std_amount",
    "user_max_amount",
    "user_txn_frequency_daily",
    "user_account_age_days",
    # Beneficiary historical relationship
    "is_new_beneficiary",
    "beneficiary_age_days",
    "beneficiary_prev_txns",
    "beneficiary_risk_score",
    # Historical device/location trust
    "is_new_device",
    "device_trust_score",
    "device_prev_txns",
    "is_new_location",
    "location_risk_score",
    # Prior cadence
    "hours_since_last_txn",
    "amount_last_24h",
    "txns_last_24h",
]

TRANSACTION_TIME_FEATURES = [
    # Transaction core parameters
    "amount",
    "log_amount",
    "transaction_type",
    # Temporal context
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_unusual_hour",
    # Instantaneous deviations from baseline
    "amount_deviation_ratio",
    "amount_z_score",
    # Sliding velocity indicators
    "velocity_5m",
    "velocity_15m",
    "velocity_1h",
    "velocity_24h",
    "amount_velocity_1h",
    "rapid_txn_flag",
    # Device / location at txn time
    "device_type",
    "device_is_proxy",
    "location_region",
    "distance_from_home_km",
]

POST_TRANSACTION_FEATURES = [
    "newbalanceOrig",
    "new_balance_orig",
    "newbalanceDest",
    "new_balance_dest",
    "balance_diff_orig",
    "balance_error_orig",
    "balance_error_dest",
    "balance_wipeout_orig",
    "remaining_balance_pct_orig",
    "is_flagged_fraud",
    "chargeback_status",
    "settlement_status",
]

# Combined authorization-time features
AUTHORIZATION_TIME_FEATURES = PRE_TRANSACTION_FEATURES + TRANSACTION_TIME_FEATURES
POST_TRANSACTION_LEAKAGE = POST_TRANSACTION_FEATURES


def audit_feature_availability(columns: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Inspect a list of column names and classify each by authorization availability.
    
    Returns:
        Dict mapping column name to categorization and leakage status.
    """
    audit = {}
    for col in columns:
        col_lower = col.lower()
        if any(post.lower() == col_lower for post in POST_TRANSACTION_FEATURES):
            audit[col] = {
                "category": "POST_TRANSACTION",
                "available_before_auth": False,
                "is_leakage": True,
                "reason": "Feature reflects post-settlement account state or downstream outcome.",
                "action": "REMOVE_FROM_MODEL",
            }
        elif any(pre.lower() == col_lower for pre in PRE_TRANSACTION_FEATURES):
            audit[col] = {
                "category": "PRE_TRANSACTION",
                "available_before_auth": True,
                "is_leakage": False,
                "reason": "Feature derived purely from customer historical profile prior to payment.",
                "action": "KEEP",
            }
        elif any(tx.lower() == col_lower for tx in TRANSACTION_TIME_FEATURES):
            audit[col] = {
                "category": "TRANSACTION_TIME",
                "available_before_auth": True,
                "is_leakage": False,
                "reason": "Feature observable at moment of payment submission.",
                "action": "KEEP",
            }
        else:
            # Check heuristic indicators
            if "newbalance" in col_lower or "new_balance" in col_lower or "wipeout" in col_lower or "post" in col_lower:
                audit[col] = {
                    "category": "POST_TRANSACTION",
                    "available_before_auth": False,
                    "is_leakage": True,
                    "reason": "Identified as post-settlement feature via heuristic pattern matching.",
                    "action": "REMOVE_FROM_MODEL",
                }
            else:
                audit[col] = {
                    "category": "TRANSACTION_TIME",
                    "available_before_auth": True,
                    "is_leakage": False,
                    "reason": "Defaulted to transaction-time observable parameter.",
                    "action": "KEEP",
                }
    return audit


def filter_authorization_features(df: pd.DataFrame, target_col: str = "isFraud") -> pd.DataFrame:
    """
    Drop all POST_TRANSACTION leakage features from a DataFrame, keeping only
    authorization-time features plus the target column if present.
    """
    audit = audit_feature_availability(list(df.columns))
    cols_to_drop = [col for col, meta in audit.items() if meta["is_leakage"] and col != target_col]
    
    clean_df = df.drop(columns=cols_to_drop, errors="ignore")
    return clean_df
