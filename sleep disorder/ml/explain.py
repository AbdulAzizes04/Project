"""
Sleep Disorder AI - SHAP Explainable AI Module
Computes Shapley values for individual predictions, ranks top influential features,
determines direction of contribution, and renders publication-quality SHAP plots.
"""
import os
import sys
import io
import base64
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for web threads
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import shap
from ml.preprocess import REVERSE_TARGET_MAPPING

class SleepExplainer:
    def __init__(self, model_path="models/best_model.pkl", feature_names_path="models/feature_names.pkl"):
        self.model = joblib.load(model_path)
        self.feature_names = joblib.load(feature_names_path)
        
        # Initialize TreeExplainer for tree-based models (RandomForest / XGBoost)
        try:
            self.explainer = shap.TreeExplainer(self.model)
        except Exception:
            self.explainer = shap.Explainer(self.model)
            
    def friendly_feature_name(self, name):
        """Converts internal feature column names to human-readable labels."""
        mapping = {
            "Systolic_BP": "Systolic Blood Pressure (mmHg)",
            "Diastolic_BP": "Diastolic Blood Pressure (mmHg)",
            "Sleep Duration": "Sleep Duration (hours)",
            "Quality of Sleep": "Quality of Sleep (1-10)",
            "Physical Activity Level": "Physical Activity Level (min/day)",
            "Stress Level": "Stress Level (1-10)",
            "Heart Rate": "Resting Heart Rate (bpm)",
            "Daily Steps": "Daily Step Count",
            "Age": "Patient Age",
            "Gender_Male": "Gender: Male",
            "Gender_Female": "Gender: Female",
            "BMI Category_Normal": "BMI: Normal Weight",
            "BMI Category_Overweight": "BMI: Overweight",
            "BMI Category_Obese": "BMI: Obese"
        }
        if name in mapping:
            return mapping[name]
        if name.startswith("Occupation_"):
            return f"Occupation: {name.replace('Occupation_', '')}"
        return name

    def explain_instance(self, processed_features_array, predicted_class_idx, top_n=5):
        """
        Calculates SHAP values for a single processed sample.
        Args:
            processed_features_array: 2D numpy array of shape (1, num_features)
            predicted_class_idx: int (0: None, 1: Insomnia, 2: Sleep Apnea)
            top_n: int, number of top features to return
        Returns:
            dict containing:
            - top_features: list of dicts with feature_name, shap_value, direction, impact
            - shap_plot_base64: PNG image encoded in base64
            - explanation_text: natural language summary
        """
        raw_shap = self.explainer.shap_values(processed_features_array)
        
        # Determine SHAP array structure
        # In shap 0.45+, shape for multiclass RF can be (1, n_features, n_classes) or list of (1, n_features)
        if isinstance(raw_shap, list):
            class_shap = raw_shap[predicted_class_idx][0]
        elif hasattr(raw_shap, "ndim") and raw_shap.ndim == 3:
            class_shap = raw_shap[0, :, predicted_class_idx]
        elif hasattr(raw_shap, "ndim") and raw_shap.ndim == 2:
            class_shap = raw_shap[0]
        else:
            class_shap = np.array(raw_shap).flatten()
            
        predicted_class_name = REVERSE_TARGET_MAPPING.get(predicted_class_idx, "Unknown")
        
        # Rank features by absolute magnitude
        abs_shap = np.abs(class_shap)
        sorted_indices = np.argsort(abs_shap)[::-1]
        
        top_features = []
        for idx in sorted_indices[:top_n]:
            feat_val = float(class_shap[idx])
            raw_name = self.feature_names[idx]
            friendly_name = self.friendly_feature_name(raw_name)
            
            # Direction: positive pushes toward this class; negative pushes against
            if feat_val > 0.001:
                direction = "Positive"
                impact_desc = f"Elevates probability of {predicted_class_name}"
            elif feat_val < -0.001:
                direction = "Negative"
                impact_desc = f"Decreases probability of {predicted_class_name} (Protective)"
            else:
                direction = "Neutral"
                impact_desc = "Minimal impact on this outcome"
                
            top_features.append({
                "feature_name": friendly_name,
                "raw_feature_name": raw_name,
                "shap_value": round(feat_val, 4),
                "abs_value": round(abs(feat_val), 4),
                "direction": direction,
                "impact_description": impact_desc
            })
            
        # Generate publication-grade horizontal bar plot
        plot_base64 = self._generate_shap_plot(top_features, predicted_class_name)
        
        # Natural language summary
        summary_items = []
        for f in top_features[:3]:
            action = "increased" if f["direction"] == "Positive" else "reduced"
            summary_items.append(f"{f['feature_name']} ({action} risk by {abs(f['shap_value']):.3f})")
            
        explanation_summary = (
            f"The prediction of '{predicted_class_name}' was primarily influenced by: "
            + "; ".join(summary_items) + "."
        )
        
        return {
            "predicted_class": predicted_class_name,
            "predicted_class_idx": predicted_class_idx,
            "top_features": top_features,
            "shap_plot_base64": plot_base64,
            "explanation_summary": explanation_summary
        }
        
    def _generate_shap_plot(self, top_features, predicted_class_name):
        """Creates a modern, stylized Matplotlib SHAP impact chart."""
        names = [f["feature_name"] for f in reversed(top_features)]
        values = [f["shap_value"] for f in reversed(top_features)]
        colors = ["#e63946" if v > 0 else "#2a9d8f" for v in values]
        
        fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8f9fa")
        
        bars = ax.barh(names, values, color=colors, height=0.55, edgecolor="none")
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            offset = 0.005 if width >= 0 else -0.005
            ha = "left" if width >= 0 else "right"
            ax.annotate(
                f"{width:+.3f}",
                xy=(width + offset, bar.get_y() + bar.get_height() / 2),
                xytext=(0, 0),
                textcoords="offset points",
                ha=ha, va="center",
                fontsize=9, fontweight="bold",
                color="#1d3557"
            )
            
        ax.axvline(0, color="#495057", linestyle="--", linewidth=1.2, alpha=0.7)
        ax.grid(axis="x", linestyle=":", alpha=0.6, color="#ced4da")
        ax.set_title(
            f"SHAP Feature Influence for: {predicted_class_name}\n"
            f"(Red = Increases Risk | Teal = Protective/Decreases Risk)",
            fontsize=11, fontweight="bold", color="#1d3557", pad=12
        )
        ax.set_xlabel("SHAP Value (Log-odds Impact)", fontsize=9, fontweight="semibold", color="#343a40")
        ax.tick_params(axis="both", which="major", labelsize=9)
        
        # Clean spines
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#ced4da")
        ax.spines["bottom"].set_color("#ced4da")
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

if __name__ == "__main__":
    explainer = SleepExplainer()
    dummy_input = np.zeros((1, len(explainer.feature_names)))
    res = explainer.explain_instance(dummy_input, predicted_class_idx=1)
    print("SHAP test successful! Top feature:", res["top_features"][0])
