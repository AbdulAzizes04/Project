"""
Feature Engineering for Career Recommendation Model.
Converts raw student profile data into normalized ML feature vectors.
"""

import numpy as np
import pandas as pd
import os

FEATURE_COLUMNS = [
    # Academic
    "cgpa", "tenth_percentage", "twelfth_percentage",
    # Aptitude
    "aptitude_quant", "aptitude_logical", "aptitude_verbal",
    "aptitude_technical", "aptitude_total",
    # Portfolio
    "num_projects", "project_complexity", "num_certifications", "cert_relevance",
    # Alignment
    "interest_match", "domain_match",
    # Skills (all 33 skill slots)
    "skill_python", "skill_java", "skill_c", "skill_cpp",
    "skill_javascript", "skill_typescript",
    "skill_html", "skill_css", "skill_react", "skill_nextjs",
    "skill_nodejs", "skill_fastapi", "skill_restapi",
    "skill_sql", "skill_mysql", "skill_postgresql", "skill_mongodb",
    "skill_pandas", "skill_numpy", "skill_statistics",
    "skill_powerbi", "skill_tableau",
    "skill_sklearn", "skill_tensorflow", "skill_pytorch",
    "skill_machine_learning", "skill_deep_learning",
    "skill_aws", "skill_gcp", "skill_azure",
    "skill_docker", "skill_kubernetes", "skill_git", "skill_linux", "skill_dsa",
]

LABEL_MAP = {
    "Software Developer": 0,
    "Data Analyst": 1,
    "Data Scientist": 2,
    "AI/ML Engineer": 3,
    "Frontend Developer": 4,
    "Backend Developer": 5,
    "Cloud Engineer": 6
}
LABEL_INVERSE = {v: k for k, v in LABEL_MAP.items()}


def load_and_prepare(csv_path: str):
    """Load dataset and return X, y with preprocessing."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["career_label"])

    # Encode labels
    df["label"] = df["career_label"].map(LABEL_MAP)
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    # Build feature matrix - only use columns that exist
    available = [c for c in FEATURE_COLUMNS if c in df.columns]
    X = df[available].fillna(0).values.astype(np.float32)
    y = df["label"].values

    # Normalize academic/aptitude columns (0-100 or 0-10 scales)
    # indices of columns that need normalization
    scale_map = {}
    for i, col in enumerate(available):
        if col in ("cgpa",):
            scale_map[i] = 10.0
        elif col in ("tenth_percentage", "twelfth_percentage", "aptitude_quant",
                     "aptitude_logical", "aptitude_verbal", "aptitude_technical", "aptitude_total"):
            scale_map[i] = 100.0

    for i, scale in scale_map.items():
        X[:, i] = X[:, i] / scale

    return X, y, available


def student_profile_to_features(profile_dict: dict, feature_cols: list) -> np.ndarray:
    """Convert a raw student profile dict to a normalized feature vector."""
    vec = []
    for col in feature_cols:
        val = profile_dict.get(col, 0) or 0
        # normalize
        if col == "cgpa":
            val = float(val) / 10.0
        elif col in ("tenth_percentage", "twelfth_percentage", "aptitude_quant",
                     "aptitude_logical", "aptitude_verbal", "aptitude_technical", "aptitude_total"):
            val = float(val) / 100.0
        else:
            val = float(val)
        vec.append(val)
    return np.array(vec, dtype=np.float32)
