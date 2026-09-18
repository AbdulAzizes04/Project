"""
LIME Service — Local Interpretable Model-Agnostic Explanations
"""
import numpy as np
from typing import List, Dict, Any

FEATURE_NAMES = [
    "Age", "Gender", "Weight", "Height", "BMI", "Pulse Rate",
    "Fatigue", "Weight Gain", "Weight Loss", "Hair Loss", "Constipation",
    "Anxiety", "Depression", "Sweating", "Neck Swelling", "Voice Changes",
    "Cold Intolerance", "Heat Intolerance", "Difficulty Swallowing", "Sleep Disturbance",
    "TSH", "T3", "T4", "FT3", "FT4",
    "Hemoglobin", "WBC", "RBC", "Platelets", "Vitamin D", "Calcium",
    "Diabetes", "Hypertension", "Family History", "Smoking", "Alcohol"
]

CATEGORICAL_FEATURES = [1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 31, 32, 33, 34, 35]


def compute_lime_explanation(
    model,
    X_scaled: np.ndarray,
    X_raw: np.ndarray,
    training_data: np.ndarray = None
) -> List[Dict[str, Any]]:
    """Compute LIME explanation for a single prediction."""
    try:
        from lime.lime_tabular import LimeTabularExplainer

        if training_data is None:
            # Generate synthetic background
            np.random.seed(42)
            training_data = np.random.randn(200, len(FEATURE_NAMES))

        explainer = LimeTabularExplainer(
            training_data,
            feature_names=FEATURE_NAMES,
            class_names=["Healthy", "Hypothyroidism", "Hyperthyroidism", "Thyroid Nodules"],
            categorical_features=CATEGORICAL_FEATURES,
            mode="classification",
            random_state=42,
        )

        predict_fn = model.predict_proba if hasattr(model, 'predict_proba') else model.predict
        exp = explainer.explain_instance(
            X_scaled[0],
            predict_fn,
            num_features=15,
            num_samples=300
        )

        result = []
        for feat, weight in exp.as_list():
            result.append({
                "feature": feat,
                "weight": round(float(weight), 5),
                "impact": "positive" if weight > 0 else "negative"
            })
        return result

    except Exception as e:
        print(f"[LIME] Error: {e}")
        return _mock_lime(X_raw)


def _mock_lime(X_raw: np.ndarray) -> List[Dict[str, Any]]:
    """Generate mock LIME explanation."""
    result = []
    values = X_raw[0]
    weights = (values - values.mean()) / (values.std() + 1e-8)
    for name, w in sorted(zip(FEATURE_NAMES, weights), key=lambda x: abs(x[1]), reverse=True)[:12]:
        result.append({
            "feature": name,
            "weight": round(float(w * 0.1), 5),
            "impact": "positive" if w > 0 else "negative"
        })
    return result
