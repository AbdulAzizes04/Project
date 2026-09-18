"""
Dynamic Banking Risk Score & Rule Engine for GuidedGuard.

This module calculates real composite risk scores (0 to 100) and maps them to discrete
risk categories (LOW, MEDIUM, HIGH, CRITICAL) using a composite weighted formula:
    Composite Risk Score = 0.40 * (ML Probability * 100) +
                           0.15 * Amount Risk +
                           0.15 * Velocity Risk +
                           0.10 * Device Risk +
                           0.10 * Location Risk +
                           0.05 * Beneficiary Risk +
                           0.05 * Historical & Balance Risk
"""

from typing import Tuple, Dict, Any, Optional
import pandas as pd
import config


def get_risk_level(score_val: float) -> str:
    """Map risk score index (0 to 100) or normalized probability to risk category."""
    norm_val = score_val / 100.0 if score_val > 1.0 else score_val
    norm_val = max(0.0, min(1.0, norm_val))

    for level, (low, high) in config.RISK_LEVEL_THRESHOLDS.items():
        if low <= norm_val < high or (level == "CRITICAL" and norm_val >= high):
            return level
    return "CRITICAL"


def get_risk_color(risk_level: str) -> str:
    """Get hex color code associated with risk level category."""
    colors = {
        "LOW": "#28a745",       # Green
        "MEDIUM": "#ffc107",    # Amber
        "HIGH": "#fd7e14",      # Orange
        "CRITICAL": "#dc3545",  # Red
    }
    return colors.get(risk_level.upper(), "#dc3545")


def calculate_behavioral_rule_breakdown(
    df_features: Optional[pd.DataFrame] = None,
    raw_txn_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """
    Calculate 0-100 component risk scores across domain risk categories.
    """
    payload = raw_txn_dict or {}
    amt = float(payload.get("amount", 0.0))
    old_b_orig = float(payload.get("old_balance_orig", payload.get("oldbalanceOrg", 0.0)))
    new_b_orig = float(payload.get("new_balance_orig", payload.get("newbalanceOrig", 0.0)))
    velocity = int(payload.get("velocity_6h", payload.get("transaction_velocity", 1)))
    device = str(payload.get("device_type", "")).lower()
    loc = str(payload.get("location", "")).lower()
    is_new_ben = int(payload.get("is_new_beneficiary", 0))
    is_late_night = int(payload.get("is_late_night", 0))
    has_fraud_history = int(payload.get("beneficiary_fraud_history_flag", 0))
    txn_type = str(payload.get("transaction_type", payload.get("type", "TRANSFER"))).upper()

    # 1. Amount Risk Component (0-100)
    if amt >= 100000.0:
        amount_score = 100.0
    elif amt >= 50000.0:
        amount_score = 80.0
    elif amt >= 10000.0:
        amount_score = 50.0
    elif amt >= 2500.0:
        amount_score = 25.0
    else:
        amount_score = 10.0

    # 2. Velocity Risk Component (0-100)
    if velocity >= 10:
        velocity_score = 100.0
    elif velocity >= 6:
        velocity_score = 75.0
    elif velocity >= 3:
        velocity_score = 40.0
    else:
        velocity_score = 10.0

    # 3. Device Risk Component (0-100)
    if "proxy" in device or "unknown" in device or "vpn" in device:
        device_score = 100.0
    elif "web" in device:
        device_score = 40.0
    else:
        device_score = 10.0

    # 4. Location Risk Component (0-100)
    if "proxy" in loc or "foreign" in loc or "high risk" in loc or "cross border" in loc:
        location_score = 100.0
    else:
        location_score = 10.0

    # 5. Beneficiary Risk Component (0-100)
    if is_new_ben == 1 or has_fraud_history == 1:
        beneficiary_score = 100.0
    else:
        beneficiary_score = 10.0

    # 6. Historical & Balance Risk Component (0-100)
    wipeout = (old_b_orig > 500.0 and new_b_orig == 0.0)
    if wipeout or has_fraud_history == 1:
        history_score = 100.0
    elif is_late_night == 1 or txn_type in ["CASH_OUT", "TRANSFER"]:
        history_score = 50.0
    else:
        history_score = 10.0

    total_behavior_rule_score = (
        0.25 * amount_score +
        0.25 * velocity_score +
        0.20 * device_score +
        0.15 * location_score +
        0.10 * beneficiary_score +
        0.05 * history_score
    )

    return {
        "amount_score": round(amount_score, 2),
        "wipeout_score": 100.0 if wipeout else 0.0,
        "velocity_score": round(velocity_score, 2),
        "device_score": round(device_score, 2),
        "location_score": round(location_score, 2),
        "beneficiary_score": round(beneficiary_score, 2),
        "history_score": round(history_score, 2),
        "time_score": 50.0 if is_late_night == 1 else 10.0,
        "type_score": 50.0 if txn_type in ["CASH_OUT", "TRANSFER"] else 10.0,
        "total_rule_score": round(total_behavior_rule_score, 2),
    }


def get_risk_score_breakdown(
    scam_prob: float,
    df_features: Optional[pd.DataFrame] = None,
    raw_txn_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate detailed Risk Score Breakdown structure using exact required weights:
      - ML Probability: 40%
      - Amount: 15%
      - Velocity: 15%
      - Device: 10%
      - Location: 10%
      - Beneficiary: 5%
      - Historical & Balance Behaviour: 5%
    """
    rule_bd = calculate_behavioral_rule_breakdown(df_features, raw_txn_dict)
    ml_prob_pct = max(0.0, min(1.0, float(scam_prob))) * 100.0

    amt_score = rule_bd["amount_score"]
    vel_score = rule_bd["velocity_score"]
    dev_score = rule_bd["device_score"]
    loc_score = rule_bd["location_score"]
    ben_score = rule_bd["beneficiary_score"]
    hist_score = rule_bd["history_score"]

    composite_score_float = (
        0.40 * ml_prob_pct +
        0.15 * amt_score +
        0.15 * vel_score +
        0.10 * dev_score +
        0.10 * loc_score +
        0.05 * ben_score +
        0.05 * hist_score
    )

    final_score = int(round(max(0.0, min(100.0, composite_score_float))))

    return {
        "model_probability": round(scam_prob * 100, 2),
        "model_probability_score": round(ml_prob_pct, 2),
        "amount_risk": amt_score,
        "velocity_risk": vel_score,
        "device_risk": dev_score,
        "location_risk": loc_score,
        "beneficiary_risk": ben_score,
        "historical_behaviour": hist_score,
        "balance_behaviour": rule_bd["wipeout_score"],
        "time_risk": rule_bd["time_score"],
        "type_risk": rule_bd["type_score"],
        "rule_risk_score": rule_bd["total_rule_score"],
        "final_risk_score": final_score,
    }


def calculate_risk_score(
    scam_prob: float,
    df_features: Optional[pd.DataFrame] = None,
    raw_txn_dict: Optional[Dict[str, Any]] = None,
) -> Tuple[int, str, float]:
    """Calculate composite risk score index (0-100) and risk level category."""
    breakdown = get_risk_score_breakdown(scam_prob, df_features, raw_txn_dict)
    final_score = breakdown["final_risk_score"]
    risk_level = get_risk_level(final_score / 100.0)
    return final_score, risk_level, breakdown["rule_risk_score"]


def get_banking_recommendation(risk_level: str, raw_txn_dict: Optional[Dict[str, Any]] = None, risk_score: int = 0) -> Dict[str, Any]:
    """
    Generate commercial banking recommendation combining Risk Level, Composite Risk Score,
    and Business Rule Overrides.
    """
    payload = raw_txn_dict or {}
    amt = float(payload.get("amount", 0.0))
    velocity = int(payload.get("velocity_6h", payload.get("transaction_velocity", 1)))
    device = str(payload.get("device_type", "")).lower()
    loc = str(payload.get("location", "")).lower()
    is_new_ben = int(payload.get("is_new_beneficiary", 0))

    # Business Rule Critical Trigger Override:
    # High Amount + High Velocity + Unknown Proxy + Foreign Region + New Beneficiary
    is_critical_override = (
        (amt >= 50000.0 and velocity >= 8 and ("proxy" in device or "unknown" in device) and ("proxy" in loc or "foreign" in loc) and is_new_ben == 1) or
        risk_score >= 75 or risk_level == "CRITICAL"
    )

    if is_critical_override:
        return {
            "action": "Freeze Transaction",
            "recommendation": "Freeze Transaction, Notify Customer & Escalate to Fraud Operations",
            "code": "FREEZE_BLOCK",
            "color": "#dc3545",
            "details": "Multiple critical scam indicators triggered (High Amount, High Velocity, Unverified Proxy Access, Foreign Region & New Beneficiary). Payment frozen for SOC escalation.",
            "workflow_step": "Fraud Incident Response",
        }
    elif risk_score >= 50 or risk_level == "HIGH":
        return {
            "action": "Hold Transaction",
            "recommendation": "Hold Transaction for Manual Verification",
            "code": "TEMP_HOLD",
            "color": "#fd7e14",
            "details": "High scam risk pattern identified. Place temporary 15-minute hold and route to fraud analyst queue.",
            "workflow_step": "Analyst Review Queue",
        }
    elif risk_score >= 25 or risk_level == "MEDIUM":
        return {
            "action": "OTP Verification",
            "recommendation": "OTP Verification Required",
            "code": "CHALLENGE_OTP",
            "color": "#ffc107",
            "details": "Moderate risk parameters detected. Challenge customer with SMS OTP or biometric 2FA authentication.",
            "workflow_step": "Step-up Authentication",
        }
    else:
        return {
            "action": "Approve",
            "recommendation": "Approve Transaction",
            "code": "APPROVE",
            "color": "#28a745",
            "details": "Transaction verified within normal customer behavior bounds. Instant settlement allowed.",
            "workflow_step": "Instant Settlement",
        }


def calculate_behavioral_rule_score(
    df_features: Optional[pd.DataFrame] = None,
    raw_txn_dict: Optional[Dict[str, Any]] = None,
) -> float:
    """Calculate total rule risk score (0-100)."""
    breakdown = calculate_behavioral_rule_breakdown(df_features, raw_txn_dict)
    return breakdown["total_rule_score"]


# Backward compatibility alias
calculate_rule_risk_score = calculate_behavioral_rule_score


