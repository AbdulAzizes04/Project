"""
Configurable Risk Fusion Engine for GuidedGuard.

Combines 8 independent behavioral and probabilistic signals into a normalized composite risk index:
1. Supervised Machine Learning Score (35%)
2. Behavioral Deviation Baseline (20%)
3. Unsupervised Anomaly Detection Score (15%)
4. Beneficiary Novelty / Payee Risk (10%)
5. Transaction Velocity Risk (8%)
6. Client Device Trust / Proxy Indicator (5%)
7. Geographic / Regional Location Anomaly (4%)
8. Temporal / Off-Hours Deviation (3%)

SCIENTIFIC INTEGRITY NOTICE:
Default weights represent an academic prototype policy and are fully configurable.
GuidedGuard does not claim these weights are scientifically optimal across all banking regimes.
All components and final composite outputs are strictly normalized into [0 - 100].

Risk Level Thresholds (Configurable):
    0  -  30: LOW
    31 -  60: MEDIUM
    61 -  80: HIGH
    81 - 100: CRITICAL
"""

from typing import Dict, Any, Tuple, Optional


DEFAULT_WEIGHTS = {
    "supervised_ml": 0.35,
    "behavioral_deviation": 0.20,
    "anomaly_detection": 0.15,
    "beneficiary_risk": 0.10,
    "velocity_risk": 0.08,
    "device_risk": 0.05,
    "location_risk": 0.04,
    "temporal_risk": 0.03,
}

DEFAULT_THRESHOLDS = {
    "LOW": (0, 30),
    "MEDIUM": (31, 60),
    "HIGH": (61, 80),
    "CRITICAL": (81, 100),
}


class RiskFusionEngine:
    """
    Fuses supervised probabilities, unsupervised anomaly scores, and domain rules
    into an explainable 0-100 composite risk index.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, Tuple[int, int]]] = None,
    ):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self.thresholds = thresholds or DEFAULT_THRESHOLDS.copy()

    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update and re-normalize component weights to sum to 1.0."""
        total = sum(new_weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in new_weights.items()}

    def get_risk_level(self, risk_score: float) -> str:
        """Map 0-100 risk score to categorical level."""
        score = max(0.0, min(100.0, float(risk_score)))
        for level, (low, high) in self.thresholds.items():
            if low <= score <= high:
                return level
        if score > 80:
            return "CRITICAL"
        return "LOW"

    def compute_fused_risk(
        self,
        supervised_score: float,       # 0 - 100 (or 0 - 1.0)
        anomaly_score: float,          # 0 - 100
        behavioral_score: float,       # 0 - 100
        beneficiary_score: float,      # 0 - 100
        velocity_score: float,         # 0 - 100
        device_score: float,           # 0 - 100
        location_score: float,         # 0 - 100
        temporal_score: float,         # 0 - 100
    ) -> Dict[str, Any]:
        """
        Execute weighted fusion across all 8 risk components.
        """
        # Ensure supervised score is on 0-100 scale
        if supervised_score <= 1.0:
            supervised_score *= 100.0

        components = {
            "supervised_ml": round(float(np_clip(supervised_score)), 1),
            "behavioral_deviation": round(float(np_clip(behavioral_score)), 1),
            "anomaly_detection": round(float(np_clip(anomaly_score)), 1),
            "beneficiary_risk": round(float(np_clip(beneficiary_score)), 1),
            "velocity_risk": round(float(np_clip(velocity_score)), 1),
            "device_risk": round(float(np_clip(device_score)), 1),
            "location_risk": round(float(np_clip(location_score)), 1),
            "temporal_risk": round(float(np_clip(temporal_score)), 1),
        }

        fused_score = sum(components[k] * self.weights.get(k, 0.0) for k in components)
        final_risk_score = int(round(np_clip(fused_score)))
        risk_level = self.get_risk_level(final_risk_score)

        return {
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "risk_components": components,
            "weights_used": self.weights,
            "thresholds_used": self.thresholds,
        }

    def fuse_risk(
        self,
        supervised_prob: float = 0.0,
        behavioral_deviation_score: float = 0.0,
        anomaly_score: float = 0.0,
        beneficiary_risk_score: float = 0.0,
        velocity_risk_score: float = 0.0,
        device_risk_score: float = 0.0,
        location_risk_score: float = 0.0,
        temporal_risk_score: float = 0.0,
    ) -> 'RiskSignalBreakdown':
        """
        Object-oriented fusion interface returning RiskSignalBreakdown.
        """
        res = self.compute_fused_risk(
            supervised_score=supervised_prob,
            anomaly_score=anomaly_score,
            behavioral_score=behavioral_deviation_score,
            beneficiary_score=beneficiary_risk_score,
            velocity_score=velocity_risk_score,
            device_score=device_risk_score,
            location_score=location_risk_score,
            temporal_score=temporal_risk_score,
        )
        comps = res["risk_components"]
        sorted_factors = sorted(comps.items(), key=lambda x: x[1], reverse=True)
        top_contributing = [f"{k.replace('_', ' ').title()} ({v:.1f})" for k, v in sorted_factors[:3]]
        return RiskSignalBreakdown(
            composite_risk_score=float(res["risk_score"]),
            risk_level=res["risk_level"],
            signals=comps,
            top_contributing_signals=top_contributing,
        )


class RiskSignalBreakdown:
    """Encapsulates multi-signal fusion results."""
    def __init__(
        self,
        composite_risk_score: float,
        risk_level: str,
        signals: Dict[str, float],
        top_contributing_signals: list,
    ):
        self.composite_risk_score = composite_risk_score
        self.risk_level = risk_level
        self.signals = signals
        self.top_contributing_signals = top_contributing_signals

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composite_risk_score": self.composite_risk_score,
            "risk_level": self.risk_level,
            "signals": self.signals,
            "top_contributing_signals": self.top_contributing_signals,
        }


def np_clip(val: float, low: float = 0.0, high: float = 100.0) -> float:
    """Helper to clamp values within bounds."""
    return max(low, min(high, float(val)))
