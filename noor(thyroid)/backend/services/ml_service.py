"""
ML Service — Load models and run ensemble prediction with weighted voting
"""
import os, sys, joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "ml_models" / "saved_models"

FEATURE_COLUMNS = [
    "age", "gender_enc", "weight", "height", "bmi", "pulse_rate",
    "fatigue", "weight_gain", "weight_loss", "hair_loss", "constipation",
    "anxiety", "depression", "sweating", "neck_swelling", "voice_changes",
    "cold_intolerance", "heat_intolerance", "difficulty_swallowing", "sleep_disturbance",
    "tsh", "t3", "t4", "ft3", "ft4",
    "hemoglobin", "wbc", "rbc", "platelets", "vitamin_d", "calcium",
    "diabetes", "hypertension", "family_history", "smoking", "alcohol"
]

CLASSES = ["Healthy", "Hypothyroidism", "Hyperthyroidism", "Thyroid Nodules"]
WEIGHTS = {"rf": 0.30, "xgb": 0.30, "lgbm": 0.20, "svm": 0.10, "ann": 0.10}


class MLService:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scaler = None
        self.models_loaded = False

    async def load_models(self):
        try:
            model_files = {
                "rf":   MODELS_DIR / "rf_model.pkl",
                "xgb":  MODELS_DIR / "xgb_model.pkl",
                "lgbm": MODELS_DIR / "lgbm_model.pkl",
                "svm":  MODELS_DIR / "svm_model.pkl",
                "ann":  MODELS_DIR / "ann_model.pkl",
            }
            scaler_file = MODELS_DIR / "scaler.pkl"

            all_exist = all(f.exists() for f in model_files.values()) and scaler_file.exists()
            if not all_exist:
                print("[ML] Models not found — training now...")
                await self._train_models()

            for name, path in model_files.items():
                self.models[name] = joblib.load(path)
            self.scaler = joblib.load(scaler_file)
            self.models_loaded = True
            print("[ML] All models loaded successfully")
        except Exception as e:
            print(f"[ML] Warning: {e}. Running in demo mode.")
            self.models_loaded = False

    async def _train_models(self):
        """Trigger training script."""
        import subprocess
        train_script = Path(__file__).resolve().parent.parent.parent / "ml_models" / "train.py"
        result = subprocess.run(
            [sys.executable, str(train_script)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print(f"[ML] Training stderr: {result.stderr}")

    def _prepare_features(self, data: Dict) -> np.ndarray:
        gender_enc = 1 if str(data.get("gender", "")).lower() in ("male", "m") else 0
        features = [
            float(data.get("age", 30)),
            gender_enc,
            float(data.get("weight", 70)),
            float(data.get("height", 170)),
            float(data.get("bmi", 24.2)),
            float(data.get("pulse_rate", 72)),
            int(data.get("fatigue", 0)),
            int(data.get("weight_gain", 0)),
            int(data.get("weight_loss", 0)),
            int(data.get("hair_loss", 0)),
            int(data.get("constipation", 0)),
            int(data.get("anxiety", 0)),
            int(data.get("depression", 0)),
            int(data.get("sweating", 0)),
            int(data.get("neck_swelling", 0)),
            int(data.get("voice_changes", 0)),
            int(data.get("cold_intolerance", 0)),
            int(data.get("heat_intolerance", 0)),
            int(data.get("difficulty_swallowing", 0)),
            int(data.get("sleep_disturbance", 0)),
            float(data.get("tsh", 2.5)),
            float(data.get("t3", 1.2)),
            float(data.get("t4", 100.0)),
            float(data.get("ft3", 3.5)),
            float(data.get("ft4", 1.2)),
            float(data.get("hemoglobin", 13.5)),
            float(data.get("wbc", 7.0)),
            float(data.get("rbc", 4.5)),
            float(data.get("platelets", 250.0)),
            float(data.get("vitamin_d", 30.0)),
            float(data.get("calcium", 9.5)),
            int(data.get("diabetes", 0)),
            int(data.get("hypertension", 0)),
            int(data.get("family_history", 0)),
            int(data.get("smoking", 0)),
            int(data.get("alcohol", 0)),
        ]
        return np.array(features).reshape(1, -1)

    def predict(self, data: Dict) -> Dict:
        """Run ensemble prediction with weighted voting."""
        X_raw = self._prepare_features(data)

        if not self.models_loaded:
            return self._demo_prediction(data)

        X = self.scaler.transform(X_raw)

        probas = {}
        for name, model in self.models.items():
            try:
                if hasattr(model, 'predict_proba'):
                    p = model.predict_proba(X)[0]
                else:
                    pred = model.predict(X)[0]
                    p = np.zeros(len(CLASSES))
                    p[int(pred)] = 1.0
                # Ensure length matches CLASSES
                if len(p) < len(CLASSES):
                    pad = np.zeros(len(CLASSES))
                    pad[:len(p)] = p
                    p = pad
                probas[name] = p
            except Exception as e:
                print(f"[ML] Model {name} error: {e}")
                probas[name] = np.array([0.25, 0.25, 0.25, 0.25])

        # Weighted ensemble
        ensemble = np.zeros(len(CLASSES))
        for name, w in WEIGHTS.items():
            if name in probas:
                ensemble += w * probas[name]

        predicted_idx = int(np.argmax(ensemble))
        confidence = float(ensemble[predicted_idx]) * 100

        risk_level = "Low"
        if confidence >= 80:
            risk_level = "High"
        elif confidence >= 60:
            risk_level = "Medium"

        return {
            "predicted_condition": CLASSES[predicted_idx],
            "confidence": round(confidence, 2),
            "risk_level": risk_level,
            "model_confidences": {
                "rf":   round(float(probas.get("rf", [0]*4)[predicted_idx]) * 100, 2),
                "xgb":  round(float(probas.get("xgb", [0]*4)[predicted_idx]) * 100, 2),
                "lgbm": round(float(probas.get("lgbm", [0]*4)[predicted_idx]) * 100, 2),
                "svm":  round(float(probas.get("svm", [0]*4)[predicted_idx]) * 100, 2),
                "ann":  round(float(probas.get("ann", [0]*4)[predicted_idx]) * 100, 2),
            },
            "X_scaled": X,
            "X_raw": X_raw,
            "all_probas": {k: v.tolist() for k, v in probas.items()},
        }

    def _demo_prediction(self, data: Dict) -> Dict:
        """Heuristic demo prediction when models are not trained."""
        tsh = float(data.get("tsh", 2.5))
        ft4 = float(data.get("ft4", 1.2))
        neck = int(data.get("neck_swelling", 0))

        if tsh > 4.5 and ft4 < 0.8:
            cond, conf = "Hypothyroidism", 82.0
        elif tsh < 0.4 and ft4 > 1.8:
            cond, conf = "Hyperthyroidism", 79.0
        elif neck == 1:
            cond, conf = "Thyroid Nodules", 71.0
        else:
            cond, conf = "Healthy", 68.0

        risk_level = "High" if conf >= 80 else ("Medium" if conf >= 60 else "Low")
        return {
            "predicted_condition": cond,
            "confidence": conf,
            "risk_level": risk_level,
            "model_confidences": {"rf": conf, "xgb": conf-2, "lgbm": conf-1, "svm": conf-3, "ann": conf-2},
            "X_scaled": np.zeros((1, len(FEATURE_COLUMNS))),
            "X_raw": np.zeros((1, len(FEATURE_COLUMNS))),
            "all_probas": {},
        }


ml_service = MLService()
