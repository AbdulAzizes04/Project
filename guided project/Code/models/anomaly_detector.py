"""
Unsupervised Anomaly Detection Module for GuidedGuard.

Supervised classifiers identify known scam patterns present in historical training labels.
However, emerging scam variants, novel social engineering techniques, or zero-day fraud
lack historical labels.

This module trains an Isolation Forest on known legitimate behavioural instances
to quantify general behavioural unusualness without requiring a positive label.

TERMINOLOGY ENFORCEMENT:
The output is an 'Anomaly Score' (0-100), NEVER referred to as a probability.
Higher values denote greater deviation from typical multi-feature distribution manifolds.
"""

from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Wraps Scikit-learn IsolationForest to generate normalized 0-100 anomaly scores.
    """

    def __init__(self, contamination: float = 0.02, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False
        self.min_score_ = -0.5
        self.max_score_ = 0.5

    def fit(self, X_legit: pd.DataFrame) -> "AnomalyDetector":
        """
        Fit Isolation Forest exclusively on legitimate/normal behavioural patterns.
        """
        # Select numeric features
        X_num = X_legit.select_dtypes(include=[np.number])
        self.model.fit(X_num)
        self.is_fitted = True

        raw_scores = self.model.decision_function(X_num)
        self.min_score_ = float(np.min(raw_scores))
        self.max_score_ = float(np.max(raw_scores))
        return self

    def predict_anomaly_score(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate normalized anomaly score (0-100) and percentile rank.
        In scikit-learn IsolationForest, lower decision_function values = more anomalous.
        We invert and scale so 0 = perfectly normal, 100 = highly anomalous outlier.
        """
        if not self.is_fitted:
            # Return neutral baseline if not yet fitted
            return np.array([20.0] * len(X)), np.array([50.0] * len(X))

        X_num = X.select_dtypes(include=[np.number])
        raw_scores = self.model.decision_function(X_num)

        # Invert: low decision function -> high anomaly score
        # Clip within observed training range
        norm = (self.max_score_ - raw_scores) / max(1e-5, (self.max_score_ - self.min_score_))
        anomaly_scores = np.clip(norm * 100.0, 0.0, 100.0)

        # Approximate percentile
        percentiles = np.clip(norm * 99.0, 1.0, 99.0)

        return np.round(anomaly_scores, 2), np.round(percentiles, 1)

    def save(self, filepath: Path) -> Path:
        """Serialize fitted detector artifact."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        return filepath

    @staticmethod
    def load(filepath: Path) -> Optional["AnomalyDetector"]:
        """Load detector artifact."""
        filepath = Path(filepath)
        if not filepath.exists():
            return None
        return joblib.load(filepath)
