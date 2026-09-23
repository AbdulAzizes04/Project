"""
SHAP Explainability Engine for Career Recommendation System.
Provides local feature attribution explaining WHY a career was recommended.
IMPORTANT: SHAP values explain model behavior, NOT absolute causal factors.
"""

import numpy as np
import json
import os
import joblib
import shap
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("career_ai.shap")

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
HUMAN_READABLE_LABELS = {
    "cgpa": "Academic CGPA",
    "tenth_percentage": "10th Grade Score",
    "twelfth_percentage": "12th Grade Score",
    "aptitude_quant": "Quantitative Aptitude",
    "aptitude_logical": "Logical Reasoning",
    "aptitude_verbal": "Verbal Aptitude",
    "aptitude_technical": "Technical Aptitude",
    "aptitude_total": "Overall Aptitude",
    "num_projects": "Project Experience",
    "project_complexity": "Project Complexity",
    "num_certifications": "Certifications Count",
    "cert_relevance": "Certification Relevance",
    "interest_match": "Career Interest Alignment",
    "domain_match": "Domain Preference Alignment",
}

for skill in ["python", "java", "c", "cpp", "javascript", "typescript", "html", "css",
              "react", "nextjs", "nodejs", "fastapi", "restapi", "sql", "mysql",
              "postgresql", "mongodb", "pandas", "numpy", "statistics", "powerbi",
              "tableau", "sklearn", "tensorflow", "pytorch", "machine_learning",
              "deep_learning", "aws", "gcp", "azure", "docker", "kubernetes",
              "git", "linux", "dsa"]:
    HUMAN_READABLE_LABELS[f"skill_{skill}"] = {
        "skill_python": "Python",
        "skill_java": "Java",
        "skill_c": "C Programming",
        "skill_cpp": "C++",
        "skill_javascript": "JavaScript",
        "skill_typescript": "TypeScript",
        "skill_html": "HTML",
        "skill_css": "CSS",
        "skill_react": "React",
        "skill_nextjs": "Next.js",
        "skill_nodejs": "Node.js",
        "skill_fastapi": "FastAPI",
        "skill_restapi": "REST API",
        "skill_sql": "SQL",
        "skill_mysql": "MySQL",
        "skill_postgresql": "PostgreSQL",
        "skill_mongodb": "MongoDB",
        "skill_pandas": "Pandas",
        "skill_numpy": "NumPy",
        "skill_statistics": "Statistics",
        "skill_powerbi": "Power BI",
        "skill_tableau": "Tableau",
        "skill_sklearn": "Scikit-learn",
        "skill_tensorflow": "TensorFlow",
        "skill_pytorch": "PyTorch",
        "skill_machine_learning": "Machine Learning",
        "skill_deep_learning": "Deep Learning",
        "skill_aws": "AWS",
        "skill_gcp": "Google Cloud",
        "skill_azure": "Microsoft Azure",
        "skill_docker": "Docker",
        "skill_kubernetes": "Kubernetes",
        "skill_git": "Git",
        "skill_linux": "Linux",
        "skill_dsa": "Data Structures & Algorithms",
    }.get(f"skill_{skill}", skill.upper())


def _load_model_and_features():
    model_path = os.path.join(ARTIFACTS_DIR, "career_model.joblib")
    feat_path = os.path.join(ARTIFACTS_DIR, "feature_columns.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError("career_model.joblib not found. Run ml/training/train_model.py first.")

    model = joblib.load(model_path)
    with open(feat_path) as f:
        feature_cols = json.load(f)
    return model, feature_cols


def explain_with_shap(
    feature_vector: np.ndarray,
    feature_names: List[str],
    class_index: int,
    top_n: int = 8
) -> Dict[str, Any]:
    """
    Compute SHAP values for a single prediction.
    Returns positive and negative contributions to the predicted career class.
    """
    try:
        model, feat_cols = _load_model_and_features()
        fv = feature_vector.reshape(1, -1)

        if hasattr(model, "feature_importances_"):
            # Tree-based: use TreeExplainer for efficiency
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(fv)
            # shap_values shape: (n_classes, n_samples, n_features) or (n_samples, n_features, n_classes)
            if isinstance(shap_values, list):
                class_shap = shap_values[class_index][0]  # (n_features,)
            else:
                class_shap = shap_values[0, :, class_index] if shap_values.ndim == 3 else shap_values[0]
        else:
            # Linear/KNN: use KernelExplainer with small background
            background = np.zeros((1, len(feature_names)))
            explainer = shap.KernelExplainer(lambda x: model.predict_proba(x), background)
            shap_values = explainer.shap_values(fv, nsamples=50)
            if isinstance(shap_values, list):
                class_shap = shap_values[class_index][0]
            else:
                class_shap = shap_values[0]

        # Build contribution items
        contributions = []
        for i, (name, val) in enumerate(zip(feature_names, class_shap)):
            label = HUMAN_READABLE_LABELS.get(name, name)
            contributions.append({
                "feature": name,
                "label": label if isinstance(label, str) else name,
                "shap_value": round(float(val), 6),
                "direction": "POSITIVE" if val > 0 else "NEGATIVE",
                "contribution_pct": round(abs(float(val)) * 100, 2)
            })

        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        positive = [c for c in contributions if c["shap_value"] > 0][:top_n]
        negative = [c for c in contributions if c["shap_value"] < 0][:top_n]

        return {
            "all_contributions": contributions[:top_n * 2],
            "top_positive": positive,
            "top_negative": negative,
            "class_index": class_index
        }

    except Exception as exc:
        logger.warning(f"SHAP computation failed: {exc}. Returning heuristic explanation.")
        return _heuristic_explanation(feature_vector, feature_names, class_index, top_n)


def _heuristic_explanation(feature_vector, feature_names, class_index, top_n):
    """Fallback heuristic explanation when SHAP is unavailable."""
    contributions = []
    for i, (name, val) in enumerate(zip(feature_names, feature_vector)):
        label = HUMAN_READABLE_LABELS.get(name, name)
        pseudo_shap = float(val) * 0.1 - 0.05
        contributions.append({
            "feature": name,
            "label": label if isinstance(label, str) else name,
            "shap_value": round(pseudo_shap, 6),
            "direction": "POSITIVE" if pseudo_shap > 0 else "NEGATIVE",
            "contribution_pct": round(abs(pseudo_shap) * 100, 2)
        })
    contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    return {
        "all_contributions": contributions[:top_n * 2],
        "top_positive": [c for c in contributions if c["shap_value"] > 0][:top_n],
        "top_negative": [c for c in contributions if c["shap_value"] < 0][:top_n],
        "class_index": class_index
    }


def generate_human_readable_text(
    career_name: str,
    top_positive: List[Dict],
    top_negative: List[Dict],
    compatibility_score: float
) -> str:
    """
    Generate a transparent, ethical, and readable explanation of the recommendation.
    Uses careful phrasing to distinguish model explanation from causal claims.
    """
    lines = [
        f"Based on your profile, the model assigned a compatibility score of {compatibility_score:.1f}% "
        f"for the {career_name} career path."
    ]

    if top_positive:
        pos_labels = [p["label"] if isinstance(p.get("label"), str) else p["feature"] for p in top_positive[:4]]
        lines.append(
            f"The factors that contributed positively to the model's prediction include: "
            f"{', '.join(pos_labels)}. These areas of your profile aligned well with the "
            f"skill and academic requirements for this career."
        )

    if top_negative:
        neg_labels = [n["label"] if isinstance(n.get("label"), str) else n["feature"] for n in top_negative[:3]]
        lines.append(
            f"Factors that had a relatively lower positive contribution include: "
            f"{', '.join(neg_labels)}. Developing these areas could further improve compatibility."
        )

    lines.append(
        "Note: These factors explain the model's prediction based on patterns in the training data. "
        "They should be interpreted as informational guidance, not as guaranteed outcomes or causal requirements."
    )

    return " ".join(lines)
