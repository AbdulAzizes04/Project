"""
Beneficiary Risk Features for GuidedGuard.

This module evaluates destination account / payee characteristics:
- is_new_beneficiary
- beneficiary_age (days known by user)
- beneficiary_transaction_count (prior payments to this recipient)
- time_since_first_payment
- beneficiary_frequency
- beneficiary_risk_score

In scam-guided payments, victims are routinely persuaded to transfer funds to
a newly added beneficiary account (money mule). A new beneficiary paired with
an unusually elevated payment amount forms a classic behavioral risk signature.
"""

from typing import Dict, Any, Optional
import pandas as pd


def compute_beneficiary_features(
    beneficiary_id: str,
    user_beneficiary_history: Optional[Dict[str, Any]] = None,
    is_new_override: Optional[int] = None,
    current_amount: float = 0.0,
) -> Dict[str, Any]:
    """
    Compute recipient risk signals given customer-beneficiary relationship history.
    """
    if is_new_override is not None:
        is_new = int(is_new_override)
        prev_txns = 0 if is_new == 1 else 5
        age_days = 0 if is_new == 1 else 180
    elif user_beneficiary_history and beneficiary_id in user_beneficiary_history:
        record = user_beneficiary_history[beneficiary_id]
        prev_txns = record.get("prev_txns", 1)
        age_days = record.get("age_days", 30)
        is_new = 1 if prev_txns == 0 else 0
    else:
        # Default assumption when no history is found: treat as newly added
        is_new = 1
        prev_txns = 0
        age_days = 0

    # Calculate Beneficiary Risk Score (0-100)
    # A new beneficiary alone is not fraud, but combined with high amount it escalates risk
    base_score = 65.0 if is_new == 1 else 10.0
    if is_new == 1 and current_amount >= 50000.0:
        base_score = 95.0
    elif is_new == 1 and current_amount >= 15000.0:
        base_score = 80.0
    elif is_new == 0 and prev_txns >= 10:
        base_score = 5.0

    return {
        "beneficiary_id": beneficiary_id,
        "is_new_beneficiary": is_new,
        "beneficiary_age_days": age_days,
        "beneficiary_transaction_count": prev_txns,
        "time_since_first_payment_days": age_days,
        "beneficiary_frequency_monthly": round(prev_txns / max(1.0, age_days / 30.0), 2),
        "beneficiary_risk_score": float(base_score),
        "beneficiary_data_source": "CUSTOMER_PAYEE_RELATIONSHIP" if user_beneficiary_history else "USER_INPUT_EVALUATION",
    }
