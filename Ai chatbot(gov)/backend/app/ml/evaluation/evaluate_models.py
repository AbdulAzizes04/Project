"""
Model Evaluation and Benchmark Suite.

Evaluates trained classification and priority prediction models, generates
academic-standard performance tables (Confusion Matrix, Precision, Recall,
F1-Score, Latency), and saves evaluation summaries for visualization.

Usage:
    cd backend
    python -m app.ml.evaluation.evaluate_models
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure backend root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)


def evaluate_classifier(model_dir: str, test_data_path: str) -> Dict[str, Any]:
    """Evaluate trained complaint classification model."""
    classifier_path = os.path.join(model_dir, "complaint_classifier.pkl")
    vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    metadata_path = os.path.join(model_dir, "classifier_metadata.json")

    if not os.path.exists(classifier_path) or not os.path.exists(vectorizer_path):
        print(f"(!) Classifier artifacts not found in {model_dir}. Running training first...")
        from app.ml.training.train_classifier import train_and_evaluate, load_or_generate_data, preprocess_data
        from sklearn.model_selection import train_test_split

        data_path = os.path.join(BACKEND_ROOT, "artifacts", "data", "complaints_dataset.csv")
        df = load_or_generate_data(data_path)
        df = preprocess_data(df)

        label_names = sorted(df["category"].unique().tolist())
        X_train, X_test, y_train, y_test = train_test_split(
            df["processed_text"].values,
            df["category"].values,
            test_size=0.2,
            random_state=42,
            stratify=df["category"].values,
        )
        results, best_name, _ = train_and_evaluate(
            X_train, X_test, y_train, y_test, label_names, model_dir
        )

    classifier = joblib.load(classifier_path)
    vectorizer = joblib.load(vectorizer_path)

    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

    # Load dataset for evaluation benchmark
    data_path = test_data_path or os.path.join(BACKEND_ROOT, "artifacts", "data", "complaints_dataset.csv")
    if not os.path.exists(data_path):
        from app.ml.training.generate_dataset import generate_dataset
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        generate_dataset(n_per_category=200, output_path=data_path)

    df = pd.read_csv(data_path).dropna(subset=["text", "category"])
    from app.ml.preprocessing.text_preprocessor import preprocess
    df["processed_text"] = df["text"].apply(preprocess)

    from sklearn.model_selection import train_test_split
    _, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["category"])

    X_test_vec = vectorizer.transform(test_df["processed_text"])
    y_test = test_df["category"].values

    # Benchmark latency
    start = time.perf_counter()
    y_pred = classifier.predict(X_test_vec)
    inference_duration = time.perf_counter() - start
    avg_latency_ms = (inference_duration / len(y_test)) * 1000.0

    labels = sorted(test_df["category"].unique().tolist())
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()
    report = classification_report(y_test, y_pred, labels=labels, target_names=labels, output_dict=True, zero_division=0)

    print("\n" + "=" * 60)
    print("  CLASSIFICATION MODEL EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Algorithm:           {metadata.get('algorithm', 'LinearSVC')}")
    print(f"Test Samples:        {len(y_test)}")
    print(f"Accuracy:            {acc * 100:.2f}%")
    print(f"Weighted Precision:  {prec * 100:.2f}%")
    print(f"Weighted Recall:     {rec * 100:.2f}%")
    print(f"Weighted F1 Score:   {f1 * 100:.2f}%")
    print(f"Avg Latency:         {avg_latency_ms:.3f} ms / prediction")
    print("-" * 60)

    return {
        "model_type": "classifier",
        "algorithm": metadata.get("algorithm", "LinearSVC"),
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "avg_latency_ms": avg_latency_ms,
        "labels": labels,
        "confusion_matrix": cm,
        "classification_report": report,
    }


def evaluate_priority(model_dir: str, data_path: str) -> Dict[str, Any]:
    """Evaluate trained priority prediction model."""
    priority_model_path = os.path.join(model_dir, "priority_model.pkl")
    metadata_path = os.path.join(model_dir, "priority_metadata.json")

    if not os.path.exists(priority_model_path):
        print(f"(!) Priority model artifacts not found in {model_dir}. Running priority training first...")
        from app.ml.training.train_priority import train_priority_model
        train_priority_model(model_dir=model_dir)

    pipeline = joblib.load(priority_model_path)
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

    if not os.path.exists(data_path):
        from app.ml.training.generate_dataset import generate_dataset
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        generate_dataset(n_per_category=200, output_path=data_path)

    df = pd.read_csv(data_path).dropna(subset=["text", "priority"])
    from sklearn.model_selection import train_test_split
    _, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["priority"])

    from app.ml.training.train_priority import extract_priority_features
    feature_dicts = [extract_priority_features(row) for _, row in test_df.iterrows()]
    feat_df = pd.DataFrame(feature_dicts)

    # Reconstruct combined features matrix
    vec = pipeline["vectorizer"]
    clf = pipeline["classifier"]
    X_text = vec.transform(test_df["text"].fillna(""))
    from scipy.sparse import hstack
    X_comb = hstack([X_text, feat_df.values])

    y_test = test_df["priority"].values
    labels = ["Low", "Medium", "High", "Critical"]

    start = time.perf_counter()
    y_pred = clf.predict(X_comb)
    inference_duration = time.perf_counter() - start
    avg_latency_ms = (inference_duration / len(y_test)) * 1000.0

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()
    report = classification_report(y_test, y_pred, labels=labels, target_names=labels, output_dict=True, zero_division=0)

    print("\n" + "=" * 60)
    print("  PRIORITY MODEL EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Algorithm:           {metadata.get('algorithm', 'GradientBoostingClassifier')}")
    print(f"Test Samples:        {len(y_test)}")
    print(f"Accuracy:            {acc * 100:.2f}%")
    print(f"Weighted Precision:  {prec * 100:.2f}%")
    print(f"Weighted Recall:     {rec * 100:.2f}%")
    print(f"Weighted F1 Score:   {f1 * 100:.2f}%")
    print(f"Avg Latency:         {avg_latency_ms:.3f} ms / prediction")
    print("=" * 60 + "\n")

    return {
        "model_type": "priority",
        "algorithm": metadata.get("algorithm", "GradientBoostingClassifier"),
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "avg_latency_ms": avg_latency_ms,
        "labels": labels,
        "confusion_matrix": cm,
        "classification_report": report,
    }


def main():
    model_dir = os.path.join(BACKEND_ROOT, "artifacts", "models")
    data_path = os.path.join(BACKEND_ROOT, "artifacts", "data", "complaints_dataset.csv")
    os.makedirs(model_dir, exist_ok=True)

    print("Starting Comprehensive Model Evaluation...")
    classifier_eval = evaluate_classifier(model_dir, data_path)
    priority_eval = evaluate_priority(model_dir, data_path)

    summary = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "models": {
            "complaint_classifier": classifier_eval,
            "priority_predictor": priority_eval,
        }
    }

    summary_file = os.path.join(model_dir, "evaluation_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Complete evaluation report exported to: {summary_file}")


if __name__ == "__main__":
    main()
