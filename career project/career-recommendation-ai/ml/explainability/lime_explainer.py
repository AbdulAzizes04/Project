"""
LIME Explainability Engine for Career Recommendation System.
Provides local, perturbation-based explanations for individual predictions.
IMPORTANT: LIME explanations describe model behavior in local regions around the input,
           and should not be interpreted as universal causal rules.
"""

import numpy as np
import json
import os
import joblib
import logging
from typing import List, Dict, Any

logger = logging.getLogger("career_ai.lime")

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def explain_with_lime(
    feature_vector: np.ndarray,
    feature_names: List[str],
    class_names: List[str],
    class_index: int,
    num_features: int = 10,
    num_samples: int = 1000
) -> Dict[str, Any]:
    """
    Compute LIME tabular explanation for a single prediction.
    Returns feature-level contributions with directionality.
    """
    try:
        from lime.lime_tabular import LimeTabularExplainer
        model_path = os.path.join(ARTIFACTS_DIR, "career_model.joblib")
        model = joblib.load(model_path)

        # LIME needs training data as background; use zeros as reference
        background = np.zeros((100, len(feature_names)))
        # Add slight noise so LIME can perturb
        background += np.random.uniform(-0.05, 0.05, background.shape)

        explainer = LimeTabularExplainer(
            training_data=background,
            feature_names=feature_names,
            class_names=class_names,
            mode="classification",
            discretize_continuous=False,
            random_state=42
        )

        exp = explainer.explain_instance(
            data_row=feature_vector,
            predict_fn=model.predict_proba,
            labels=[class_index],
            num_features=num_features,
            num_samples=num_samples
        )

        lime_contributions = []
        for feature_desc, weight in exp.as_list(label=class_index):
            lime_contributions.append({
                "feature_description": feature_desc,
                "weight": round(float(weight), 6),
                "direction": "POSITIVE" if weight > 0 else "NEGATIVE",
                "abs_weight": round(abs(float(weight)), 6)
            })

        lime_contributions.sort(key=lambda x: x["abs_weight"], reverse=True)

        return {
            "lime_values": lime_contributions,
            "top_positive": [c for c in lime_contributions if c["direction"] == "POSITIVE"][:6],
            "top_negative": [c for c in lime_contributions if c["direction"] == "NEGATIVE"][:6],
            "class_name": class_names[class_index] if class_index < len(class_names) else "Unknown",
            "explanation_quality": "local_perturbation"
        }

    except Exception as exc:
        logger.warning(f"LIME explanation failed: {exc}. Returning heuristic fallback.")
        return _lime_heuristic(feature_vector, feature_names, class_names, class_index, num_features)


def _lime_heuristic(feature_vector, feature_names, class_names, class_index, num_features):
    """Heuristic LIME-style explanation for fallback."""
    contributions = []
    for name, val in zip(feature_names, feature_vector):
        weight = (float(val) - 0.5) * 0.3
        contributions.append({
            "feature_description": f"{name}",
            "weight": round(weight, 6),
            "direction": "POSITIVE" if weight > 0 else "NEGATIVE",
            "abs_weight": round(abs(weight), 6)
        })
    contributions.sort(key=lambda x: x["abs_weight"], reverse=True)
    contributions = contributions[:num_features]
    return {
        "lime_values": contributions,
        "top_positive": [c for c in contributions if c["direction"] == "POSITIVE"][:5],
        "top_negative": [c for c in contributions if c["direction"] == "NEGATIVE"][:5],
        "class_name": class_names[class_index] if class_index < len(class_names) else "Unknown",
        "explanation_quality": "heuristic_fallback"
    }
