"""
Complaint Classification Training Script.

Trains and evaluates two models:
  Model A: TF-IDF + Logistic Regression (baseline)
  Model B: TF-IDF + LinearSVC (final model)

Saves the best model + vectorizer to disk.
Stores evaluation metrics in the database.

Usage:
    cd backend
    python -m app.ml.training.train_classifier
"""
import os
import sys
import json
import pickle
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Ensure backend root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.calibration import CalibratedClassifierCV
import joblib


def load_or_generate_data(data_path: str) -> pd.DataFrame:
    """Load dataset, generating it if not found."""
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Generating...")
        from app.ml.training.generate_dataset import generate_dataset
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        records = generate_dataset(n_per_category=200, output_path=data_path)
        return pd.DataFrame(records)
    else:
        return pd.read_csv(data_path)


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply text preprocessing to the dataset."""
    from app.ml.preprocessing.text_preprocessor import preprocess
    print("Preprocessing text...")
    df = df.dropna(subset=["text", "category"])
    df["processed_text"] = df["text"].apply(preprocess)
    return df


def train_and_evaluate(
    X_train, X_test, y_train, y_test, label_names: list, model_dir: str
):
    """
    Train Model A (LR) and Model B (SVM), evaluate both, save the best.
    Returns metrics dict for both models.
    """
    results = {}

    # ─── Model A: TF-IDF + Logistic Regression ──────────────────────────────
    print("\n[Model A] TF-IDF + Logistic Regression")
    vectorizer_a = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    X_train_a = vectorizer_a.fit_transform(X_train)
    X_test_a = vectorizer_a.transform(X_test)

    lr_model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    lr_model.fit(X_train_a, y_train)
    y_pred_a = lr_model.predict(X_test_a)

    acc_a = accuracy_score(y_test, y_pred_a)
    f1_a = f1_score(y_test, y_pred_a, average="weighted")
    prec_a = precision_score(y_test, y_pred_a, average="weighted", zero_division=0)
    rec_a = recall_score(y_test, y_pred_a, average="weighted", zero_division=0)
    cm_a = confusion_matrix(y_test, y_pred_a, labels=label_names).tolist()
    report_a = classification_report(y_test, y_pred_a, labels=label_names,
                                      target_names=label_names, output_dict=True, zero_division=0)

    print(f"  Accuracy:  {acc_a:.4f}")
    print(f"  F1 Score:  {f1_a:.4f}")
    print(f"  Precision: {prec_a:.4f}")
    print(f"  Recall:    {rec_a:.4f}")

    results["logistic_regression"] = {
        "accuracy": acc_a,
        "f1": f1_a,
        "precision": prec_a,
        "recall": rec_a,
        "confusion_matrix": cm_a,
        "classification_report": report_a,
        "vectorizer": vectorizer_a,
        "model": lr_model,
    }

    # ─── Model B: TF-IDF + LinearSVC (calibrated for probability estimates) ─
    print("\n[Model B] TF-IDF + LinearSVC (calibrated)")
    vectorizer_b = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    X_train_b = vectorizer_b.fit_transform(X_train)
    X_test_b = vectorizer_b.transform(X_test)

    # CalibratedClassifierCV wraps LinearSVC to provide predict_proba
    svm_base = LinearSVC(C=1.0, max_iter=2000, random_state=42)
    svm_model = CalibratedClassifierCV(svm_base, cv=3)
    svm_model.fit(X_train_b, y_train)
    y_pred_b = svm_model.predict(X_test_b)

    # Train accuracy
    y_train_pred_b = svm_model.predict(X_train_b)
    train_acc_b = accuracy_score(y_train, y_train_pred_b)

    acc_b = accuracy_score(y_test, y_pred_b)
    f1_b = f1_score(y_test, y_pred_b, average="weighted")
    prec_b = precision_score(y_test, y_pred_b, average="weighted", zero_division=0)
    rec_b = recall_score(y_test, y_pred_b, average="weighted", zero_division=0)
    cm_b = confusion_matrix(y_test, y_pred_b, labels=label_names).tolist()
    report_b = classification_report(y_test, y_pred_b, labels=label_names,
                                      target_names=label_names, output_dict=True, zero_division=0)

    print(f"  Accuracy:       {acc_b:.4f}")
    print(f"  Train Accuracy: {train_acc_b:.4f}")
    print(f"  F1 Score:       {f1_b:.4f}")
    print(f"  Precision:      {prec_b:.4f}")
    print(f"  Recall:         {rec_b:.4f}")

    results["svm"] = {
        "accuracy": acc_b,
        "train_accuracy": train_acc_b,
        "f1": f1_b,
        "precision": prec_b,
        "recall": rec_b,
        "confusion_matrix": cm_b,
        "classification_report": report_b,
        "vectorizer": vectorizer_b,
        "model": svm_model,
    }

    # --- Select best model ---
    print("\n--- Model Comparison ---")
    print(f"  Logistic Regression F1: {f1_a:.4f}")
    print(f"  SVM F1:                 {f1_b:.4f}")

    if f1_b >= f1_a:
        best_name = "svm"
        print("  [OK] Selected: LinearSVC (higher or equal F1)")
    else:
        best_name = "logistic_regression"
        print("  [OK] Selected: Logistic Regression (higher F1)")

    best = results[best_name]

    # ─── Save models ──────────────────────────────────────────────────────────
    os.makedirs(model_dir, exist_ok=True)

    vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    classifier_path = os.path.join(model_dir, "complaint_classifier.pkl")
    metadata_path = os.path.join(model_dir, "classifier_metadata.json")

    joblib.dump(best["vectorizer"], vectorizer_path)
    joblib.dump(best["model"], classifier_path)

    metadata = {
        "model_name": "Complaint Classifier (Final)",
        "algorithm": "LinearSVC (Calibrated)" if best_name == "svm" else "Logistic Regression",
        "selected_based_on": "weighted F1 score on test set",
        "accuracy": best["accuracy"],
        "f1_score": best["f1"],
        "precision": best["precision"],
        "recall": best["recall"],
        "train_accuracy": best.get("train_accuracy"),
        "confusion_matrix": best["confusion_matrix"],
        "label_names": label_names,
        "version": "1.0.0",
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n[OK] Vectorizer saved: {vectorizer_path}")
    print(f"[OK] Classifier saved: {classifier_path}")
    print(f"[OK] Metadata saved:   {metadata_path}")

    return results, best_name, metadata


def save_metrics_to_db(results: dict, label_names: list, dataset_size: int,
                        train_size: int, test_size: int):
    """Store evaluation metrics in the database for the admin analytics page."""
    try:
        from app.core.database import SessionLocal
        from app.models.prediction import ModelEvaluation
        import uuid
        from datetime import datetime, timezone

        db = SessionLocal()
        try:
            # Mark existing classifier evaluations as inactive
            db.query(ModelEvaluation).filter(
                ModelEvaluation.model_type == "classifier"
            ).update({"is_active": False})

            algo_map = {
                "logistic_regression": "TF-IDF + Logistic Regression",
                "svm": "TF-IDF + LinearSVC (Calibrated)",
            }

            for model_key, metrics in results.items():
                eval_record = ModelEvaluation(
                    id=str(uuid.uuid4()),
                    model_name=f"Complaint Classifier — {algo_map.get(model_key, model_key)}",
                    model_type="classifier",
                    algorithm=algo_map.get(model_key, model_key),
                    accuracy=metrics["accuracy"],
                    precision_score=metrics["precision"],
                    recall_score=metrics["recall"],
                    f1_score=metrics["f1"],
                    train_accuracy=metrics.get("train_accuracy"),
                    confusion_matrix=metrics["confusion_matrix"],
                    classification_report={
                        k: v for k, v in metrics["classification_report"].items()
                        if k not in ("vectorizer", "model")
                    },
                    label_names=label_names,
                    dataset_size=dataset_size,
                    train_size=train_size,
                    test_size=test_size,
                    is_active=(model_key == "svm"),
                    evaluated_at=datetime.now(timezone.utc),
                )
                db.add(eval_record)

            db.commit()
            print("[OK] Metrics saved to database.")
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: Could not save metrics to DB: {e}")


def main():
    print("=" * 60)
    print("  Complaint Classification Training")
    print("=" * 60)

    DATA_PATH = os.path.join("data", "complaints.csv")
    MODEL_DIR = os.path.join("app", "ml", "models")

    # Load data
    df = load_or_generate_data(DATA_PATH)
    print(f"[OK] Loaded {len(df)} records")
    print(f"  Categories: {df['category'].value_counts().to_dict()}")

    # Preprocess
    df = preprocess_data(df)

    label_names = sorted(df["category"].unique().tolist())
    X = df["processed_text"].values
    y = df["category"].values

    # Split: 70% train, 15% val (unused in simple eval), 15% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp
    )
    # 0.176 of 0.85 ≈ 0.15 of total → 70/15/15 split

    print(f"\nSplit: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")
    print(f"Labels: {label_names}")

    # Train + evaluate
    results, best_name, metadata = train_and_evaluate(
        X_train, X_test, y_train, y_test, label_names, MODEL_DIR
    )

    # Save to DB (only if tables exist)
    save_metrics_to_db(results, label_names, len(df), len(X_train), len(X_test))

    print("\n" + "=" * 60)
    print("  Training Complete")
    print(f"  Best Model: {metadata['algorithm']}")
    print(f"  Test Accuracy: {metadata['accuracy']:.4f}")
    print(f"  F1 Score:      {metadata['f1_score']:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
