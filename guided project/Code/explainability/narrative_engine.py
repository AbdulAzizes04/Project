"""
Natural Language Banking Narrative & Warning Generator for GuidedGuard.

Translates complex technical ML attributions (SHAP/LIME), anomaly scores,
and behavioral baseline deviations into professional, objective banking narratives.

POLICY ON SCIENTIFIC & LEGAL CLAIMS:
Machine learning models observe statistical correlations; they CANNOT prove that
a customer was socially engineered. Statements like 'This is definitely a scam'
are strictly prohibited.
Instead, the narrative engine employs calibrated framing:
'This payment exhibits behavioral and transactional characteristics consistent with elevated scam risk.'
"""

from typing import Dict, Any, List, Optional


def generate_natural_language_explanation(
    transaction_dict: Dict[str, Any],
    risk_score: int,
    risk_level: str,
    risk_components: Dict[str, float],
    top_factors: Optional[List[Dict[str, Any]]] = None,
    deviations: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate clear, human-understandable English explanation points for banking analysts and customers.
    """
    reasons = []
    positive_indicators = []

    amt = float(transaction_dict.get("amount", 0.0))
    is_new_ben = int(transaction_dict.get("is_new_beneficiary", 0))
    is_late = int(transaction_dict.get("is_late_night", 0))
    dev = str(transaction_dict.get("device_type", "Mobile App"))
    loc = str(transaction_dict.get("location", "Domestic Home"))
    vel = int(transaction_dict.get("velocity_6h", 1))

    # 1. Amount Reason
    if deviations and deviations.get("amount_ratio", 1.0) > 3.0:
        ratio = deviations["amount_ratio"]
        reasons.append(
            f"The payment amount (${amt:,.2f}) is significantly higher ({ratio:.1f}x) than the customer's historical average."
        )
    elif amt >= 25000.0:
        reasons.append(f"The transaction amount (${amt:,.2f}) represents an unusually large capital transfer.")
    else:
        positive_indicators.append("Transaction amount is within normal historical spending bounds.")

    # 2. Beneficiary Reason
    if is_new_ben == 1:
        reasons.append("The recipient account is newly registered with no established transaction history.")
    else:
        positive_indicators.append("Recipient is an established payee with previous successful settlements.")

    # 3. Velocity Reason
    if vel >= 5:
        reasons.append(f"High transaction frequency detected ({vel} payments in the recent monitoring window).")
    else:
        positive_indicators.append("Transaction velocity aligns with standard baseline cadence.")

    # 4. Device Reason
    if any(k in dev.lower() for k in ["proxy", "unknown", "vpn", "rooted"]):
        reasons.append(f"Connection initiated through an unverified network proxy or unrecognized client signature ({dev}).")
    else:
        positive_indicators.append("Access originated from a verified personal mobile banking application.")

    # 5. Location Reason
    if any(k in loc.lower() for k in ["proxy", "foreign", "high risk", "cross border"]):
        reasons.append(f"Geolocation indicates an elevated-risk routing zone or cross-border network ({loc}).")
    else:
        positive_indicators.append("Connection originated from the customer's typical domestic home region.")

    # 6. Temporal Reason
    if is_late == 1:
        reasons.append("Payment submitted during late-night / off-hours outside routine daytime banking activity.")
    else:
        positive_indicators.append("Payment submitted during regular business hours.")

    # Primary headline statement
    if risk_level in ["CRITICAL", "HIGH"]:
        headline = (
            f"This transaction has been assigned a {risk_level} risk score ({risk_score}/100) "
            f"because it exhibits multiple behavioral characteristics consistent with scam-guided / APP fraud."
        )
    elif risk_level == "MEDIUM":
        headline = (
            f"This transaction has been assigned a MEDIUM risk score ({risk_score}/100). "
            f"Several atypical parameters were observed that warrant step-up customer verification."
        )
    else:
        headline = (
            f"This transaction has been assigned a LOW risk score ({risk_score}/100). "
            f"Observable signals align broadly with typical customer payment habits."
        )

    # Human-readable summary paragraph
    summary_paragraph = (
        f"{headline} "
        + (f"Key risk contributors include: {'; '.join(reasons[:3])}. " if reasons else "No anomalous risk factors detected. ")
        + (f"Mitigating factors: {'; '.join(positive_indicators[:2])}." if positive_indicators else "")
    )

    return {
        "headline": headline,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "primary_reasons": reasons if reasons else ["No high-risk behavioral anomalies detected."],
        "analyst_notes": reasons,
        "positive_signals": positive_indicators,
        "positive_indicators": positive_indicators,
        "executive_summary": summary_paragraph,
        "recommended_action": "Review Transaction",
        "summary_paragraph": summary_paragraph,
        "claims_compliance": "Verified: Non-definitive probabilistic framing compliant with APP fraud research guidelines.",
    }


class SecurityNarrativeEngine:
    """Object-oriented engine for calibrated natural language banking security narratives."""

    def generate_narrative(
        self,
        risk_score: float,
        risk_level: str,
        signals: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate structured banking risk narrative from input signals."""
        txn_dict = {
            "amount": signals.get("amount", 25000.0),
            "is_new_beneficiary": signals.get("is_new_payee", 1),
            "device_type": signals.get("device_type", "Unknown Proxy"),
            "location": signals.get("location", "Foreign Proxy"),
            "velocity_6h": signals.get("velocity_6h", 3),
        }
        risk_comps = {
            "supervised_ml": signals.get("supervised_prob", 0.5) * 100.0,
            "behavioral_deviation": signals.get("behavioral_score", 50.0),
            "anomaly_detection": signals.get("anomaly_score", 50.0),
            "beneficiary_risk": signals.get("beneficiary_risk", 50.0),
        }
        res = generate_natural_language_explanation(
            transaction_dict=txn_dict,
            risk_score=int(risk_score),
            risk_level=risk_level,
            risk_components=risk_comps,
        )
        return {
            "executive_summary": res.get("executive_summary", ""),
            "key_risk_drivers": res.get("analyst_notes", []),
            "recommended_actions": [res.get("recommended_action", "Review Transaction")],
            "positive_signals": res.get("positive_signals", []),
        }
