"""
Unit tests for 8-signal RiskFusionEngine and InterventionEngine.

Tests multi-signal fusion, weight constraints, thresholding, and automated policy intervention.
"""

import pytest
from models.risk_engine import RiskFusionEngine, RiskSignalBreakdown
from models.intervention_engine import InterventionEngine, InterventionPolicy


def test_risk_fusion_weights_sum_to_one():
    """Verify default risk fusion weights sum to 1.0."""
    engine = RiskFusionEngine()
    total_weight = sum(engine.weights.values())
    assert pytest.approx(total_weight, rel=1e-3) == 1.0


def test_risk_fusion_low_risk_scenario():
    """Test risk fusion with all low-risk inputs."""
    engine = RiskFusionEngine()
    result = engine.fuse_risk(
        supervised_prob=0.02,
        behavioral_deviation_score=10.0,
        anomaly_score=15.0,
        beneficiary_risk_score=5.0,
        velocity_risk_score=10.0,
        device_risk_score=5.0,
        location_risk_score=5.0,
        temporal_risk_score=10.0,
    )

    assert result.composite_risk_score < 30.0
    assert result.risk_level in ["LOW", "MEDIUM"]
    assert len(result.signals) == 8


def test_risk_fusion_critical_risk_scenario():
    """Test risk fusion with elevated scam-consistent inputs."""
    engine = RiskFusionEngine()
    result = engine.fuse_risk(
        supervised_prob=0.92,
        behavioral_deviation_score=95.0,
        anomaly_score=90.0,
        beneficiary_risk_score=85.0,
        velocity_risk_score=80.0,
        device_risk_score=75.0,
        location_risk_score=80.0,
        temporal_risk_score=85.0,
    )

    assert result.composite_risk_score >= 80.0
    assert result.risk_level == "CRITICAL"
    assert "Supervised ML" in result.top_contributing_signals[0] or "Behavioral" in result.top_contributing_signals[0]


def test_intervention_engine_low_risk():
    """Test intervention engine returns Approve for low risk."""
    engine = InterventionEngine()
    policy = engine.evaluate_intervention(risk_score=15.0, risk_level="LOW")

    assert policy.action == "APPROVE"
    assert policy.requires_step_up is False
    assert policy.cooling_off_hours == 0


def test_intervention_engine_critical_risk():
    """Test intervention engine returns Cooling-off Hold and SOC Escalation for critical risk."""
    engine = InterventionEngine()
    policy = engine.evaluate_intervention(risk_score=92.0, risk_level="CRITICAL")

    assert policy.action in ["COOLING_OFF_HOLD", "ESCALATE_SOC", "STEP_UP_AND_DELAY"]
    assert policy.cooling_off_hours > 0
    assert policy.requires_step_up is True
    assert policy.customer_warning != ""
