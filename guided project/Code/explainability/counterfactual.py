"""
Counterfactual Explainability Engine for GuidedGuard.

In fraud prevention, explaining why a payment was flagged (SHAP/LIME) is only half
the equation. Fraud analysts and users need actionable recourse:
"What minimal, plausible modifications would reduce the estimated risk from Critical/High to Low/Medium?"

CRITICAL POLICY & DISCLAIMER:
Counterfactuals are strictly labeled:
'COUNTERFACTUAL SIMULATION — Actionable Risk Recourse'
Changing a feature in simulation does NOT guarantee real-world payment safety or prove lack of scam intent.
It highlights sensitivity and sensitivity boundaries.
"""

from typing import Dict, Any, List, Optional
import copy


def generate_counterfactual_scenarios(
    current_payload: Dict[str, Any],
    risk_breakdown: Dict[str, Any],
    risk_engine: Any,
    user_baseline_avg: float = 2500.0,
) -> Dict[str, Any]:
    """
    Generate minimal actionable perturbations across sensitive risk drivers:
    1. Amount reduction closer to user baseline
    2. Known/established beneficiary
    3. Normal business hours timing
    4. Trusted/known customer device
    5. Domestic location
    """
    current_risk_score = risk_breakdown.get("final_risk_score", risk_breakdown.get("risk_score", 75))
    current_components = risk_breakdown.get("risk_components", {})

    amt = float(current_payload.get("amount", 50000.0))
    is_new_ben = int(current_payload.get("is_new_beneficiary", 1))
    is_late = int(current_payload.get("is_late_night", 1))
    dev = str(current_payload.get("device_type", "Unknown Proxy"))
    loc = str(current_payload.get("location", "Foreign Proxy"))

    scenarios = []

    # Counterfactual 1: Amount closer to normal baseline
    if amt > user_baseline_avg * 2.0:
        c1_comp = copy.deepcopy(current_components)
        c1_comp["supervised_ml"] = max(5.0, c1_comp.get("supervised_ml", 50.0) * 0.40)
        c1_comp["behavioral_deviation"] = max(5.0, c1_comp.get("behavioral_deviation", 70.0) * 0.30)
        c1_comp["anomaly_detection"] = max(10.0, c1_comp.get("anomaly_detection", 60.0) * 0.45)
        
        sim1 = risk_engine.compute_fused_risk(
            c1_comp["supervised_ml"],
            c1_comp["anomaly_detection"],
            c1_comp["behavioral_deviation"],
            c1_comp.get("beneficiary_risk", 50.0),
            c1_comp.get("velocity_risk", 30.0),
            c1_comp.get("device_risk", 20.0),
            c1_comp.get("location_risk", 20.0),
            c1_comp.get("temporal_risk", 20.0),
        )
        scenarios.append({
            "id": "CF-1",
            "lever": "Transaction Amount",
            "current_state": f"${amt:,.2f}",
            "simulated_state": f"${user_baseline_avg:,.2f} (Within normal historical baseline)",
            "estimated_risk_score": sim1["risk_score"],
            "estimated_risk_level": sim1["risk_level"],
            "risk_reduction_points": max(0, current_risk_score - sim1["risk_score"]),
            "explanation": f"Reducing transaction volume within historical spending range drops estimated risk by {max(0, current_risk_score - sim1['risk_score'])} points.",
        })

    # Counterfactual 2: Previously established beneficiary
    if is_new_ben == 1:
        c2_comp = copy.deepcopy(current_components)
        c2_comp["beneficiary_risk"] = 10.0
        c2_comp["behavioral_deviation"] = max(10.0, c2_comp.get("behavioral_deviation", 50.0) - 25.0)

        sim2 = risk_engine.compute_fused_risk(
            c2_comp.get("supervised_ml", 50.0),
            c2_comp.get("anomaly_detection", 50.0),
            c2_comp["behavioral_deviation"],
            c2_comp["beneficiary_risk"],
            c2_comp.get("velocity_risk", 30.0),
            c2_comp.get("device_risk", 20.0),
            c2_comp.get("location_risk", 20.0),
            c2_comp.get("temporal_risk", 20.0),
        )
        scenarios.append({
            "id": "CF-2",
            "lever": "Recipient Relationship",
            "current_state": "Newly added / unverified beneficiary",
            "simulated_state": "Previously established beneficiary with verified payment history",
            "estimated_risk_score": sim2["risk_score"],
            "estimated_risk_level": sim2["risk_level"],
            "risk_reduction_points": max(0, current_risk_score - sim2["risk_score"]),
            "explanation": "If the destination account were an established recurring payee, novelty risk would be mitigated.",
        })

    # Counterfactual 3: Standard Business Hours
    if is_late == 1 or current_components.get("temporal_risk", 0) > 40:
        c3_comp = copy.deepcopy(current_components)
        c3_comp["temporal_risk"] = 10.0
        c3_comp["behavioral_deviation"] = max(5.0, c3_comp.get("behavioral_deviation", 50.0) - 15.0)

        sim3 = risk_engine.compute_fused_risk(
            c3_comp.get("supervised_ml", 50.0),
            c3_comp.get("anomaly_detection", 50.0),
            c3_comp["behavioral_deviation"],
            c3_comp.get("beneficiary_risk", 40.0),
            c3_comp.get("velocity_risk", 30.0),
            c3_comp.get("device_risk", 20.0),
            c3_comp.get("location_risk", 20.0),
            c3_comp["temporal_risk"],
        )
        scenarios.append({
            "id": "CF-3",
            "lever": "Transaction Timing",
            "current_state": "Late night / off-hours execution",
            "simulated_state": "Routine daytime business hours (09:00 - 18:00)",
            "estimated_risk_score": sim3["risk_score"],
            "estimated_risk_level": sim3["risk_level"],
            "risk_reduction_points": max(0, current_risk_score - sim3["risk_score"]),
            "explanation": "Initiating the transfer during standard business hours reduces urgency/panic indicators.",
        })

    # Counterfactual 4: Known Device & Domestic Location
    if "proxy" in dev.lower() or "proxy" in loc.lower() or "foreign" in loc.lower():
        c4_comp = copy.deepcopy(current_components)
        c4_comp["device_risk"] = 10.0
        c4_comp["location_risk"] = 10.0
        c4_comp["anomaly_detection"] = max(10.0, c4_comp.get("anomaly_detection", 50.0) - 20.0)

        sim4 = risk_engine.compute_fused_risk(
            c4_comp.get("supervised_ml", 40.0),
            c4_comp["anomaly_detection"],
            c4_comp.get("behavioral_deviation", 40.0),
            c4_comp.get("beneficiary_risk", 40.0),
            c4_comp.get("velocity_risk", 20.0),
            c4_comp["device_risk"],
            c4_comp["location_risk"],
            c4_comp.get("temporal_risk", 20.0),
        )
        scenarios.append({
            "id": "CF-4",
            "lever": "Device & Network Access",
            "current_state": f"{dev} from {loc}",
            "simulated_state": "Customer registered Mobile App from verified Domestic Home network",
            "estimated_risk_score": sim4["risk_score"],
            "estimated_risk_level": sim4["risk_level"],
            "risk_reduction_points": max(0, current_risk_score - sim4["risk_score"]),
            "explanation": "Accessing the account from a recognized personal device avoids proxy/VPN anomaly penalties.",
        })

    return {
        "current_risk_score": current_risk_score,
        "scenarios": scenarios,
        "disclaimer": "Counterfactual simulation only. Changing inputs in simulation illustrates sensitivity and does not guarantee safety.",
    }


class CounterfactualEngine:
    """Object-oriented engine for actionable counterfactual recourse."""

    def __init__(self, risk_engine: Optional[Any] = None):
        if risk_engine is None:
            from models.risk_engine import RiskFusionEngine
            self.risk_engine = RiskFusionEngine()
        else:
            self.risk_engine = risk_engine

    def find_counterfactual(self, current_payload: Dict[str, Any], target_risk: float = 30.0) -> Dict[str, Any]:
        risk_breakdown = {
            "risk_score": current_payload.get("risk_score", 75),
            "risk_components": {
                "supervised_ml": 70.0,
                "behavioral_deviation": 65.0,
                "anomaly_detection": 60.0,
                "beneficiary_risk": 50.0,
                "velocity_risk": 40.0,
                "device_risk": 30.0,
                "location_risk": 20.0,
                "temporal_risk": 20.0,
            },
        }
        res = generate_counterfactual_scenarios(current_payload, risk_breakdown, self.risk_engine)
        recourse_paths = []
        for sc in res.get("scenarios", []):
            recourse_paths.append({
                "recommended_changes": sc.get("simulated_state", ""),
                "projected_risk_score": sc.get("estimated_risk_score", 30.0),
                "risk_reduction": sc.get("risk_reduction_points", 0),
            })
        return {
            "current_risk_score": res.get("current_risk_score", 75),
            "recourse_paths": recourse_paths,
            "disclaimer": res.get("disclaimer", ""),
        }
