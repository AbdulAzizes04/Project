"""
Sleep Disorder AI - Prediction Engine
Loads model & preprocessor, validates and transforms input,
generates class probabilities, and computes SHAP explanations.
"""
import os
import sys
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.preprocess import REVERSE_TARGET_MAPPING, TARGET_MAPPING
from ml.explain import SleepExplainer

class SleepPredictor:
    def __init__(
        self,
        model_path="models/best_model.pkl",
        preprocessor_path="models/preprocessor.pkl",
        feature_names_path="models/feature_names.pkl"
    ):
        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)
        self.feature_names = joblib.load(feature_names_path)
        self.explainer = SleepExplainer(model_path, feature_names_path)
        self.model_name = type(self.model).__name__

    def format_input(self, user_dict):
        """
        Converts user dictionary to a single-row DataFrame compatible with preprocessor.
        Expected keys in user_dict:
        - Age (int/float)
        - Gender ('Male' or 'Female')
        - Occupation (str)
        - Sleep Duration (float)
        - Quality of Sleep (int 1-10)
        - Physical Activity Level (int min/day)
        - Stress Level (int 1-10)
        - BMI Category ('Normal', 'Overweight', 'Obese')
        - Systolic_BP (int/float)
        - Diastolic_BP (int/float)
        - Heart Rate (int/float)
        - Daily Steps (int/float)
        """
        # Parse Blood Pressure if provided as single string '120/80'
        if "Blood Pressure" in user_dict and ("Systolic_BP" not in user_dict or not user_dict["Systolic_BP"]):
            parts = str(user_dict["Blood Pressure"]).split("/")
            systolic = float(parts[0]) if len(parts) > 0 else 120.0
            diastolic = float(parts[1]) if len(parts) > 1 else 80.0
        else:
            systolic = float(user_dict.get("Systolic_BP", 120))
            diastolic = float(user_dict.get("Diastolic_BP", 80))

        # Standardize BMI category
        bmi = str(user_dict.get("BMI Category", "Normal")).strip()
        if bmi == "Normal Weight":
            bmi = "Normal"

        data = {
            "Age": [float(user_dict.get("Age", 35))],
            "Gender": [str(user_dict.get("Gender", "Male")).strip().capitalize()],
            "Occupation": [str(user_dict.get("Occupation", "Engineer")).strip()],
            "Sleep Duration": [float(user_dict.get("Sleep Duration", 7.0))],
            "Quality of Sleep": [int(user_dict.get("Quality of Sleep", 7))],
            "Physical Activity Level": [int(user_dict.get("Physical Activity Level", 60))],
            "Stress Level": [int(user_dict.get("Stress Level", 5))],
            "BMI Category": [bmi],
            "Heart Rate": [int(user_dict.get("Heart Rate", 70))],
            "Daily Steps": [int(user_dict.get("Daily Steps", 6000))],
            "Systolic_BP": [systolic],
            "Diastolic_BP": [diastolic]
        }
        return pd.DataFrame(data)

    def predict(self, user_dict, generate_shap=True):
        """
        Executes prediction and returns detailed results.
        """
        input_df = self.format_input(user_dict)
        
        # Transform using preprocessor
        X_proc = self.preprocessor.transform(input_df)
        
        # Predict class & probabilities
        pred_idx = int(self.model.predict(X_proc)[0])
        pred_class_name = REVERSE_TARGET_MAPPING.get(pred_idx, "Unknown")
        
        probabilities = {}
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_proc)[0]
            for idx, prob in enumerate(probs):
                name = REVERSE_TARGET_MAPPING.get(idx, f"Class {idx}")
                probabilities[name] = round(float(prob) * 100, 2)
            confidence = probabilities.get(pred_class_name, 0.0)
        else:
            confidence = 100.0
            probabilities = {pred_class_name: 100.0}
            
        # Determine clinical risk category
        if pred_class_name == "None":
            risk_level = "Low Risk"
            risk_badge = "success"
        elif pred_class_name == "Insomnia":
            risk_level = "Moderate Risk (Sleep Initiation / Maintenance)"
            risk_badge = "warning"
        else: # Sleep Apnea
            risk_level = "Elevated Risk (Breathing Disturbance)"
            risk_badge = "danger"
            
        result = {
            "predicted_class": pred_class_name,
            "predicted_class_idx": pred_idx,
            "confidence": confidence,
            "probabilities": probabilities,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "model_used": self.model_name,
            "input_summary": input_df.to_dict(orient="records")[0]
        }
        
        # Compute SHAP explainability
        if generate_shap:
            shap_result = self.explainer.explain_instance(X_proc, predicted_class_idx=pred_idx)
            result["explanation"] = shap_result
            
        return result

if __name__ == "__main__":
    predictor = SleepPredictor()
    sample = {
        "Age": 45,
        "Gender": "Male",
        "Occupation": "Doctor",
        "Sleep Duration": 5.5,
        "Quality of Sleep": 4,
        "Physical Activity Level": 30,
        "Stress Level": 8,
        "BMI Category": "Overweight",
        "Blood Pressure": "140/90",
        "Heart Rate": 82,
        "Daily Steps": 4000
    }
    pred = predictor.predict(sample)
    print("Prediction Result:")
    print(f"Predicted Class: {pred['predicted_class']} ({pred['confidence']}%)")
    print(f"Probabilities: {pred['probabilities']}")
    print(f"Top Factor: {pred['explanation']['top_features'][0]}")
