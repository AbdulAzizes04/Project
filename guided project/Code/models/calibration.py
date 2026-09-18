"""
Model Probability Calibration Module for GuidedGuard.

Gradient Boosting and tree ensembles produce uncalibrated margin outputs or distorted
probabilities under severe class imbalance. Calling an uncalibrated score a "probability"
is scientifically invalid.

This module implements post-hoc calibration:
1. Platt Scaling (Sigmoid / Logistic regression calibration)
2. Isotonic Regression (Non-parametric piecewise monotonic calibration)
3. Brier Score evaluation and calibration curve diagnostics.

TERMINOLOGY ENFORCEMENT:
Only post-calibrated outputs are referred to as 'Calibrated Fraud Probability'.
Raw ensemble scores are labeled 'Model Risk Score'.
"""

from typing import Tuple, Dict, Any
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss


def train_calibrator(
    base_model: Any,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    method: str = "sigmoid",
) -> Tuple[CalibratedClassifierCV, Dict[str, Any]]:
    """
    Fit Platt Scaling ('sigmoid') or Isotonic Regression ('isotonic') on held-out validation set.
    """
    calibrated = CalibratedClassifierCV(estimator=base_model, method=method, cv="prefit")
    calibrated.fit(X_val, y_val)

    # Compute uncalibrated vs calibrated Brier scores
    if hasattr(base_model, "predict_proba"):
        raw_probs = base_model.predict_proba(X_val)[:, 1]
    else:
        raw_probs = base_model.predict(X_val)

    cal_probs = calibrated.predict_proba(X_val)[:, 1]

    raw_brier = float(brier_score_loss(y_val, raw_probs))
    cal_brier = float(brier_score_loss(y_val, cal_probs))

    diagnostics = {
        "calibration_method": method,
        "raw_brier_score": round(raw_brier, 4),
        "calibrated_brier_score": round(cal_brier, 4),
        "brier_improvement_pct": round(((raw_brier - cal_brier) / max(1e-5, raw_brier)) * 100, 2),
        "is_justified_as_probability": (cal_brier < 0.10),
    }

    return calibrated, diagnostics


def compare_calibration_methods(
    base_model: Any,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> Dict[str, Any]:
    """
    Compare Uncalibrated vs Platt Scaling vs Isotonic Regression on validation data.
    """
    if hasattr(base_model, "predict_proba"):
        raw_probs = base_model.predict_proba(X_val)[:, 1]
    else:
        raw_probs = base_model.predict(X_val)

    cal_sigmoid, diag_sigmoid = train_calibrator(base_model, X_val, y_val, method="sigmoid")
    cal_isotonic, diag_isotonic = train_calibrator(base_model, X_val, y_val, method="isotonic")

    prob_true_raw, prob_pred_raw = calibration_curve(y_val, raw_probs, n_bins=5)
    prob_true_sig, prob_pred_sig = calibration_curve(y_val, diag_sigmoid["calibrated_brier_score"], n_bins=5)

    return {
        "uncalibrated_brier": round(float(brier_score_loss(y_val, raw_probs)), 4),
        "platt_sigmoid_brier": diag_sigmoid["calibrated_brier_score"],
        "isotonic_brier": diag_isotonic["calibrated_brier_score"],
        "best_method": "sigmoid" if diag_sigmoid["calibrated_brier_score"] <= diag_isotonic["calibrated_brier_score"] else "isotonic",
        "sigmoid_model": cal_sigmoid,
        "isotonic_model": cal_isotonic,
    }
