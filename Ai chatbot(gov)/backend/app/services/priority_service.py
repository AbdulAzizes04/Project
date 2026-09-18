"""
Priority Prediction Service.
Loads trained Gradient Boosting model and predicts complaint priority with confidence.
Falls back to rule-based logic when model is unavailable.
"""
import os
import re
import json
from typing import Optional
from loguru import logger
import joblib
import numpy as np
import scipy.sparse as sp


PRIORITY_KEYWORDS = {
    "Critical": ["fire", "flood", "collapse", "electrocution", "death", "accident happened",
                 "emergency", "disease outbreak", "life risk", "toxic", "hazardous", "crisis",
                 "unconscious", "hospital emergency"],
    "High": ["no water", "no electricity", "no supply", "not working", "dangerous", "unsafe",
             "people suffering", "elderly", "children", "hospital", "urgent", "severe",
             "broken", "damaged", "entire area", "whole colony", "completely", "days"],
    "Medium": ["inconvenient", "problem", "issue", "affecting", "blocking", "irregular",
               "potholes", "dirty", "smell", "not collected"],
    "Low": ["minor", "small", "slight", "billing", "meter", "timer", "noise", "dim"],
}


class PriorityService:
    def __init__(self):
        self._vectorizer = None
        self._model = None
        self._loaded = False
        self._label_names = None

    def _load_models(self):
        if self._loaded:
            return

        vectorizer_path = "app/ml/models/priority_vectorizer.pkl"
        model_path = "app/ml/models/priority_predictor.pkl"
        metadata_path = "app/ml/models/priority_metadata.json"

        if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
            logger.warning(
                "Priority model files not found. "
                "Run: python -m app.ml.training.train_priority"
            )
            return

        try:
            self._vectorizer = joblib.load(vectorizer_path)
            self._model = joblib.load(model_path)

            if os.path.exists(metadata_path):
                with open(metadata_path) as f:
                    meta = json.load(f)
                    self._label_names = meta.get("label_names")

            self._loaded = True
            logger.info("Priority model loaded.")
        except Exception as e:
            logger.error(f"Failed to load priority model: {e}")

    def is_ready(self) -> bool:
        self._load_models()
        return self._loaded

    def _build_engineered_features(self, text: str, category: str = "") -> np.ndarray:
        """Build the same engineered features used during training."""
        text_lower = text.lower()
        features = [
            int(any(kw in text_lower for kw in ["fire", "flood", "collapse", "death", "emergency"])),
            int(any(kw in text_lower for kw in ["no water", "no electricity", "dangerous", "unsafe", "broken"])),
            int(any(kw in text_lower for kw in ["inconvenient", "problem", "issue"])),
            int(any(kw in text_lower for kw in ["minor", "billing", "meter", "noise"])),
            min(len(text) / 200.0, 1.0),
            int(bool(re.search(r"\d+", text))),
            int("urgent" in text_lower or "immediately" in text_lower or "emergency" in text_lower),
            int("people" in text_lower or "residents" in text_lower or "children" in text_lower
                or "elderly" in text_lower or "women" in text_lower),
            int("danger" in text_lower or "unsafe" in text_lower or "accident" in text_lower
                or "risk" in text_lower or "hazard" in text_lower),
            int(any(kw in text_lower for kw in ["month", "weeks", "10 days", "15 days"])),
        ]

        cats = ["Water Supply", "Roads", "Sanitation", "Electricity", "Street Lighting", "Drainage"]
        for c in cats:
            features.append(int(category == c))

        return np.array(features, dtype=float)

    def predict_priority(
        self, text: str, category: str = "", severity: str = "", duration: str = ""
    ) -> dict:
        """
        Predict priority for a complaint.

        Returns:
            {
                "priority": str,
                "confidence": float,
                "all_scores": dict,
                "rule_based_fallback": bool
            }
        """
        from app.ml.preprocessing.text_preprocessor import preprocess
        from app.core.config import settings

        combined_text = f"{text} {category} {severity} {duration}".strip()

        if not self.is_ready():
            return self._rule_based_priority(combined_text)

        try:
            processed = preprocess(combined_text)
            X_tfidf = self._vectorizer.transform([processed])
            eng = self._build_engineered_features(combined_text, category)
            X_eng = sp.csr_matrix(eng.reshape(1, -1))
            X_combined = sp.hstack([X_tfidf, X_eng]).toarray()

            proba = self._model.predict_proba(X_combined)[0]
            classes = self._model.classes_
            predicted_idx = np.argmax(proba)
            priority = classes[predicted_idx]
            confidence = float(proba[predicted_idx])

            all_scores = {cls: float(prob) for cls, prob in zip(classes, proba)}
            low_confidence = confidence < settings.LOW_CONFIDENCE_THRESHOLD

            return {
                "priority": priority,
                "confidence": confidence,
                "all_scores": all_scores,
                "rule_based_fallback": False,
            }
        except Exception as e:
            logger.error(f"Priority prediction error: {e}")
            return self._rule_based_priority(combined_text)

    def _rule_based_priority(self, text: str) -> dict:
        """
        Rule-based priority fallback (used when model unavailable or low confidence).
        NOT the primary prediction — labeled clearly in the response.
        """
        text_lower = text.lower()

        for level in ["Critical", "High", "Medium", "Low"]:
            for kw in PRIORITY_KEYWORDS[level]:
                if kw in text_lower:
                    confidence = {"Critical": 0.82, "High": 0.75, "Medium": 0.65, "Low": 0.70}
                    return {
                        "priority": level,
                        "confidence": confidence[level],
                        "all_scores": {},
                        "rule_based_fallback": True,
                    }

        return {
            "priority": "Medium",
            "confidence": 0.55,
            "all_scores": {},
            "rule_based_fallback": True,
        }


# Singleton
priority_service = PriorityService()
