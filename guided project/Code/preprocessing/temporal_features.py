"""
Temporal Behavior Features for GuidedGuard.

This module computes time-of-day, day-of-week, and timing interval indicators:
- hour
- day_of_week
- is_weekend
- is_unusual_hour
- time_since_previous_transaction
- time_since_previous_beneficiary_transaction
- temporal_deviation_level (LOW, MEDIUM, HIGH)
- temporal_risk_score (0-100)

Evaluates whether the transaction occurs during the customer's typical activity hours
(e.g., 08:00-21:00) or at unusual times (e.g. 03:15 AM late-night panic transfers).
"""

from typing import Dict, Any, List, Optional
import pandas as pd


def compute_temporal_features(
    step: Optional[int] = None,
    timestamp: Optional[Any] = None,
    user_usual_hours: Optional[List[int]] = None,
    last_txn_time: Optional[pd.Timestamp] = None,
    last_beneficiary_txn_time: Optional[pd.Timestamp] = None,
) -> Dict[str, Any]:
    """
    Extract temporal features and compare against user's personal activity baseline.
    """
    if timestamp is not None:
        dt = pd.to_datetime(timestamp)
        hour = int(dt.hour)
        day_of_week = int(dt.dayofweek)
    elif step is not None:
        # In PaySim, step represents elapsed hours from start
        hour = int(step % 24)
        day_of_week = int((step // 24) % 7)
    else:
        hour = 12
        day_of_week = 0

    is_weekend = 1 if day_of_week in [5, 6] else 0
    is_late_night = 1 if hour in [0, 1, 2, 3, 4, 5, 23] else 0

    # User personal baseline: default normal active window is 08:00 - 21:00
    normal_hours = user_usual_hours if user_usual_hours else list(range(8, 22))
    is_unusual_hour = 1 if hour not in normal_hours else 0

    # Time intervals
    hours_since_last = 24.0
    if timestamp is not None and last_txn_time is not None:
        diff = (pd.to_datetime(timestamp) - pd.to_datetime(last_txn_time)).total_seconds() / 3600.0
        hours_since_last = max(0.01, round(diff, 2))

    hours_since_last_ben = 72.0
    if timestamp is not None and last_beneficiary_txn_time is not None:
        diff = (pd.to_datetime(timestamp) - pd.to_datetime(last_beneficiary_txn_time)).total_seconds() / 3600.0
        hours_since_last_ben = max(0.01, round(diff, 2))

    # Risk scoring
    if is_late_night and is_unusual_hour:
        temporal_deviation = "HIGH"
        temporal_risk_score = 85.0
    elif is_unusual_hour or is_late_night:
        temporal_deviation = "MEDIUM"
        temporal_risk_score = 50.0
    else:
        temporal_deviation = "LOW"
        temporal_risk_score = 10.0

    return {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "is_late_night": is_late_night,
        "is_unusual_hour": is_unusual_hour,
        "time_since_previous_transaction_hours": hours_since_last,
        "time_since_previous_beneficiary_transaction_hours": hours_since_last_ben,
        "temporal_deviation_level": temporal_deviation,
        "temporal_risk_score": float(temporal_risk_score),
    }
