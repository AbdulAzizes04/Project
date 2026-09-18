"""
Simulated Payment Intervention Engine for GuidedGuard.

In APP/scam-guided fraud, conventional hard-blocks often cause friction or prompt
the scammer to coach the victim to bypass the block. Tailored contextual interventions
(e.g., cooling-off delays, multi-party callback verification, confirmation dialogs)
disrupt the scammer's urgency.

DISCLAIMER & SAFETY POLICY:
This application is an academic research prototype.
Interventions are strictly SIMULATED for demonstration purposes.
It does NOT connect to real banking, payment rails, or UPI infrastructure.
"""

from typing import Dict, Any, Optional


INTERVENTION_POLICIES = {
    "LOW": {
        "action": "Approve Transaction",
        "badge_color": "#10B981",  # Green
        "dialog_title": "Payment Authorized",
        "user_message": (
            "Transaction parameters and recipient relationship appear broadly consistent "
            "with your historical payment profile. Proceeding with instant authorization."
        ),
        "cooling_off_period_mins": 0,
        "requires_2fa_challenge": False,
        "analyst_queue_escalation": False,
    },
    "MEDIUM": {
        "action": "Contextual Warning & 2FA Challenge",
        "badge_color": "#F59E0B",  # Amber
        "dialog_title": "Additional Verification Recommended",
        "user_message": (
            "Some unusual characteristics were detected (elevated transfer amount or novel transfer window). "
            "Please review the recipient name, account number, and amount before submitting your biometric verification."
        ),
        "cooling_off_period_mins": 0,
        "requires_2fa_challenge": True,
        "analyst_queue_escalation": False,
    },
    "HIGH": {
        "action": "Dynamic Friction & Recipient Callback Prompt",
        "badge_color": "#F97316",  # Orange
        "dialog_title": "Elevated Risk Warning — Verify Recipient Independently",
        "user_message": (
            "Several unusual behavioural characteristics were detected: This payment is significantly higher "
            "than your usual spending or involves a newly added beneficiary. "
            "Scammers frequently impersonate bank officials, police, or merchants creating false urgency. "
            "Please verify the payee via an independent phone call before proceeding."
        ),
        "cooling_off_period_mins": 15,
        "requires_2fa_challenge": True,
        "analyst_queue_escalation": True,
    },
    "CRITICAL": {
        "action": "Temporary Protective Hold & Fraud Operations Escalation",
        "badge_color": "#EF4444",  # Red
        "dialog_title": "Critical Risk Alert — High Scam Consistency Pattern",
        "user_message": (
            "Multiple high-risk behavioral indicators detected: Unusual high-value payment to a new payee "
            "initiated under rapid velocity or novel device access. "
            "Payment has been placed on a temporary 30-minute cooling-off hold. "
            "A fraud prevention specialist will contact you to verify authorization."
        ),
        "cooling_off_period_mins": 30,
        "requires_2fa_challenge": True,
        "analyst_queue_escalation": True,
    },
}


def evaluate_intervention(
    risk_level: str,
    risk_score: int,
    top_factors: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Generate tailored simulated intervention advice for user warnings and SOC operations.
    """
    level = risk_level.upper() if risk_level in INTERVENTION_POLICIES else "LOW"
    policy = INTERVENTION_POLICIES[level].copy()
    policy["risk_level"] = level
    policy["risk_score"] = risk_score
    policy["top_risk_factors"] = top_factors or []
    policy["is_simulated"] = True
    return policy


class InterventionPolicy:
    """Encapsulates simulated intervention policy decision."""

    def __init__(
        self,
        action: str,
        requires_step_up: bool,
        cooling_off_hours: float,
        customer_warning: str,
    ):
        self.action = action
        self.requires_step_up = requires_step_up
        self.cooling_off_hours = cooling_off_hours
        self.customer_warning = customer_warning


class InterventionEngine:
    """Contextual simulated intervention decision engine."""

    def evaluate_intervention(self, risk_score: float, risk_level: str) -> InterventionPolicy:
        """Evaluate intervention and return typed InterventionPolicy object."""
        res = evaluate_intervention(risk_level=risk_level, risk_score=int(risk_score))
        action = "APPROVE" if risk_level.upper() == "LOW" else "COOLING_OFF_HOLD"
        requires_step_up = res.get("requires_2fa_challenge", False)
        cooling_hours = res.get("cooling_off_period_mins", 0) / 60.0
        warning = res.get("user_message", "")
        return InterventionPolicy(
            action=action,
            requires_step_up=requires_step_up,
            cooling_off_hours=cooling_hours,
            customer_warning=warning,
        )
