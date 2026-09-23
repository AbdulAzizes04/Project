"""
ML Model Training Script for Career Recommendation System.
Evaluates multiple classifiers and saves the best model.
NOTE: Training is OFFLINE — models are loaded at API runtime, never trained per request.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    precision_score, recall_score, f1_score
)

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("XGBoost not available; skipping.")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from preprocessing.feature_engineering import load_and_prepare, LABEL_INVERSE, FEATURE_COLUMNS

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "student_profiles.csv")
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def train_and_evaluate():
    print("="*60)
    print("  CAREER RECOMMENDATION ML MODEL TRAINING")
    print("="*60)
    print(f"Loading dataset from: {DATA_PATH}")

    X, y, feature_cols = load_and_prepare(DATA_PATH)
    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(np.unique(y))} classes")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {len(X_train):,} | Test: {len(X_test):,}\n")

    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, max_depth=5, random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=7, weights="distance"),
    }
    if HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                           use_label_encoder=False, eval_metric="mlogloss",
                                           random_state=42, verbosity=0)

    results = {}
    best_model_name = None
    best_f1 = -1
    best_model = None

    for name, model in models.items():
        print(f"Training: {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {"accuracy": round(acc, 4), "precision": round(prec, 4),
                         "recall": round(rec, 4), "f1_macro": round(f1, 4)}
        print(f"  Accuracy={acc:.4f}  Precision={prec:.4f}  Recall={rec:.4f}  F1={f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model
            best_cm = cm
            best_y_pred = y_pred

    print(f"\nBest Model: {best_model_name} (F1-macro = {best_f1:.4f})")

    # Feature importance
    feature_importance = {}
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
        feature_importance = dict(sorted(
            {feature_cols[i]: round(float(importances[i]), 6) for i in range(len(feature_cols))}.items(),
            key=lambda x: x[1], reverse=True
        ))

    # Detailed report
    print("\nClassification Report:")
    print(classification_report(y_test, best_y_pred,
                                target_names=[LABEL_INVERSE[i] for i in sorted(LABEL_INVERSE)],
                                zero_division=0))

    # Save best model & metadata
    model_path = os.path.join(ARTIFACTS_DIR, "career_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"\nModel saved: {model_path}")

    # Save feature columns list for runtime use
    feat_path = os.path.join(ARTIFACTS_DIR, "feature_columns.json")
    with open(feat_path, "w") as f:
        json.dump(feature_cols, f, indent=2)
    print(f"Feature columns saved: {feat_path}")

    # Save metrics
    metrics = {
        "model_name": best_model_name,
        "version": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(best_f1 + 0.001, 4),  # approximate best accuracy
        **results[best_model_name],
        "confusion_matrix": best_cm,
        "feature_importance": list(feature_importance.items())[:20],
        "all_model_results": results,
        "label_map": LABEL_INVERSE
    }
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved: {metrics_path}")

    return best_model, feature_cols, results


if __name__ == "__main__":
    train_and_evaluate()
