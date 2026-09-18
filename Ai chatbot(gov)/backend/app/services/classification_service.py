"""
Complaint Classification Service.
Loads the trained TF-IDF + SVM model and provides prediction with confidence scores.
"""
import os
import json
from typing import Optional
from loguru import logger
import joblib
import numpy as np


class ClassificationService:
    """Loads and invokes the complaint classification model."""

    def __init__(self):
        self._vectorizer = None
        self._model = None
        self._label_names = None
        self._loaded = False
        self._model_version = "1.0.0"

    def _load_models(self):
        """Lazy-load models on first use."""
        if self._loaded:
            return

        vectorizer_path = os.environ.get("VECTORIZER_PATH", "app/ml/models/tfidf_vectorizer.pkl")
        classifier_path = os.environ.get("CLASSIFIER_MODEL_PATH", "app/ml/models/complaint_classifier.pkl")
        metadata_path = "app/ml/models/classifier_metadata.json"

        if not os.path.exists(vectorizer_path) or not os.path.exists(classifier_path):
            logger.warning(
                "Classification model files not found. "
                "Run: python -m app.ml.training.train_classifier"
            )
            self._loaded = False
            return

        try:
            self._vectorizer = joblib.load(vectorizer_path)
            self._model = joblib.load(classifier_path)

            if os.path.exists(metadata_path):
                with open(metadata_path) as f:
                    meta = json.load(f)
                    self._label_names = meta.get("label_names")
                    self._model_version = meta.get("version", "1.0.0")

            self._loaded = True
            logger.info(f"Classification model loaded. Labels: {self._label_names}")
        except Exception as e:
            logger.error(f"Failed to load classification model: {e}")
            self._loaded = False

    def is_ready(self) -> bool:
        self._load_models()
        return self._loaded

    def classify(self, text: str) -> dict:
        """
        Classify a complaint text.

        Returns:
            {
                "category": str,
                "confidence": float,
                "all_scores": dict[str, float],
                "low_confidence": bool
            }
        """
        from app.ml.preprocessing.text_preprocessor import preprocess
        from app.core.config import settings

        if not self.is_ready():
            return self._fallback_classify(text)

        try:
            processed = preprocess(text)
            X = self._vectorizer.transform([processed])
            proba = self._model.predict_proba(X)[0]
            classes = self._model.classes_

            predicted_idx = np.argmax(proba)
            predicted_category = classes[predicted_idx]
            confidence = float(proba[predicted_idx])

            all_scores = {cls: float(prob) for cls, prob in zip(classes, proba)}
            low_confidence = confidence < settings.LOW_CONFIDENCE_THRESHOLD

            return {
                "category": predicted_category,
                "confidence": confidence,
                "all_scores": all_scores,
                "low_confidence": low_confidence,
            }

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return self._fallback_classify(text)

    def _fallback_classify(self, text: str) -> dict:
        """
        Keyword-based fallback when ML model is unavailable.
        Returns low confidence to trigger admin review.
        """
        text_lower = text.lower()
        keywords = {
            "Water Supply": ["water", "tap", "pipeline", "drinking", "supply", "tanker"],
            "Roads": ["road", "pothole", "pavement", "footpath", "bridge", "traffic"],
            "Sanitation": ["garbage", "waste", "sweeper", "dustbin", "toilet", "sanitation", "clean"],
            "Electricity": ["electricity", "power", "light", "current", "voltage", "transformer", "electric"],
            "Street Lighting": ["street light", "lamp", "lighting", "dark", "street lamp"],
            "Drainage": ["drain", "sewer", "sewage", "flood", "waterlog", "overflow", "manhole"],
        }

        scores = {}
        for category, kws in keywords.items():
            scores[category] = sum(1 for kw in kws if kw in text_lower)

        if max(scores.values()) == 0:
            best_category = "Water Supply"
            confidence = 0.2
        else:
            best_category = max(scores, key=scores.get)
            total = sum(scores.values())
            confidence = scores[best_category] / total if total > 0 else 0.2
            confidence = min(confidence * 0.6, 0.6)  # Cap at 0.6 — always "low confidence"

        all_scores = {k: v / max(sum(scores.values()), 1) * 0.6 for k, v in scores.items()}

        return {
            "category": best_category,
            "confidence": confidence,
            "all_scores": all_scores,
            "low_confidence": True,
        }


# Singleton instance
classification_service = ClassificationService()
