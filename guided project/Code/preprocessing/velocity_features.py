"""
Transaction Velocity Features for GuidedGuard.

This module computes short-term and rolling window transaction velocity signals:
- transactions_last_5min
- transactions_last_15min
- transactions_last_30min
- transactions_last_1hour
- transactions_last_24hours
- amount_last_30min
- amount_last_1hour
- amount_last_24hours
- beneficiaries_added_last_24hours
- rapid_transaction_indicator

In scam scenarios (e.g. romance, impersonation, investment scams), victims are often
coached to execute rapid successive transfers before bank anti-fraud checks freeze the account.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def compute_velocity_features_from_history(
    user_txns: pd.DataFrame,
    current_timestamp: pd.Timestamp,
    current_amount: float,
    current_beneficiary: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Given a user's transaction history dataframe containing ['timestamp', 'amount', 'beneficiary'],
    calculate true rolling-window velocity metrics prior to authorization.
    """
    if user_txns.empty or "timestamp" not in user_txns.columns:
        return get_default_velocity_features(current_amount)

    history = user_txns[user_txns["timestamp"] < current_timestamp].copy()
    if history.empty:
        return get_default_velocity_features(current_amount)

    now = current_timestamp
    t_5m = now - pd.Timedelta(minutes=5)
    t_15m = now - pd.Timedelta(minutes=15)
    t_30m = now - pd.Timedelta(minutes=30)
    t_1h = now - pd.Timedelta(hours=1)
    t_24h = now - pd.Timedelta(hours=24)

    tx_5m = len(history[history["timestamp"] >= t_5m])
    tx_15m = len(history[history["timestamp"] >= t_15m])
    tx_30m = len(history[history["timestamp"] >= t_30m])
    tx_1h = len(history[history["timestamp"] >= t_1h])
    tx_24h = len(history[history["timestamp"] >= t_24h])

    amt_30m = float(history[history["timestamp"] >= t_30m]["amount"].sum())
    amt_1h = float(history[history["timestamp"] >= t_1h]["amount"].sum())
    amt_24h = float(history[history["timestamp"] >= t_24h]["amount"].sum())

    bens_24h = 0
    if "beneficiary" in history.columns:
        bens_24h = int(history[history["timestamp"] >= t_24h]["beneficiary"].nunique())

    rapid_flag = 1 if (tx_15m >= 2 or tx_1h >= 4) else 0

    # Velocity risk score (0-100)
    if tx_15m >= 3 or tx_1h >= 5 or amt_1h >= 50000:
        vel_score = 95.0
    elif tx_1h >= 3 or tx_24h >= 8 or amt_1h >= 20000:
        vel_score = 70.0
    elif tx_1h >= 2 or tx_24h >= 4:
        vel_score = 40.0
    else:
        vel_score = 10.0

    return {
        "transactions_last_5min": tx_5m,
        "transactions_last_15min": tx_15m,
        "transactions_last_30min": tx_30m,
        "transactions_last_1hour": tx_1h,
        "transactions_last_24hours": tx_24h,
        "amount_last_30min": amt_30m,
        "amount_last_1hour": amt_1h,
        "amount_last_24hours": amt_24h,
        "beneficiaries_added_last_24hours": bens_24h,
        "rapid_transaction_indicator": rapid_flag,
        "velocity_risk_score": vel_score,
        "velocity_source": "HISTORICAL_TIMESTAMP_ANALYSIS",
    }


def get_default_velocity_features(amount: float = 0.0, velocity_input: Optional[int] = None) -> Dict[str, Any]:
    """
    Return baseline/prototype velocity features when continuous transaction streaming
    timestamps are simulated for inference or standalone testing.
    """
    v = velocity_input if velocity_input is not None else 1
    
    if v >= 10:
        vel_score = 95.0
        rapid = 1
    elif v >= 5:
        vel_score = 75.0
        rapid = 1
    elif v >= 3:
        vel_score = 45.0
        rapid = 0
    else:
        vel_score = 10.0
        rapid = 0

    return {
        "transactions_last_5min": max(0, v - 2),
        "transactions_last_15min": max(0, v - 1),
        "transactions_last_30min": v,
        "transactions_last_1hour": v,
        "transactions_last_24hours": v * 3,
        "amount_last_30min": amount * max(1, v - 1),
        "amount_last_1hour": amount * v,
        "amount_last_24hours": amount * v * 2,
        "beneficiaries_added_last_24hours": 1 if v > 3 else 0,
        "rapid_transaction_indicator": rapid,
        "velocity_risk_score": vel_score,
        "velocity_source": "SIMULATED_PROTOTYPE_INPUT" if velocity_input is not None else "DEFAULT_BASELINE",
    }
