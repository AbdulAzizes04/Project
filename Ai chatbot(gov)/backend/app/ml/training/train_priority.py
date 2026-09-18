"""
Priority Prediction Training Script.

Trains a Gradient Boosting classifier to predict complaint priority (Low/Medium/High/Critical).
Features: TF-IDF text features + engineered features (category, severity keywords, duration).

Usage:
    cd backend
    python -m app.ml.training.train_priority
"""
import os
import sys
import json
import uuid
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
import scipy.sparse as sp


PRIORITY_KEYWORDS = {
    "critical": ["fire", "flood", "collapse", "electrocution", "death", "accident happened",
                 "emergency", "disease outbreak", "life risk", "toxic", "hazardous", "crisis"],
    "high": ["no water", "no electricity", "no supply", "not working", "dangerous", "unsafe",
             "people suffering", "elderly", "children", "hospital", "urgent", "severe",
             "broken", "damaged", "entire area", "whole colony", "completely"],
    "medium": ["inconvenient", "problem", "issue", "affecting", "blocking", "irregular",
               "potholes", "dirty", "smell", "not collected", "weeks"],
    "low": ["minor", "small", "slight", "billing", "meter", "timer", "noise", "dim"],
}

CATEGORY_PRIORITY_WEIGHTS = {
    "Water Supply": {"High": 0.4, "Critical": 0.1, "Medium": 0.4, "Low": 0.1},
    "Roads": {"High": 0.3, "Critical": 0.05, "Medium": 0.5, "Low": 0.15},
    "Sanitation": {"High": 0.25, "Critical": 0.05, "Medium": 0.5, "Low": 0.2},
    "Electricity": {"High": 0.35, "Critical": 0.15, "Medium": 0.4, "Low": 0.1},
    "Street Lighting": {"High": 0.3, "Critical": 0.05, "Medium": 0.45, "Low": 0.2},
    "Drainage": {"High": 0.3, "Critical": 0.1, "Medium": 0.45, "Low": 0.15},
}


def extract_priority_features(row: pd.Series) -> dict:
    """Extract engineered features for priority prediction."""
    text = str(row.get("text", "")).lower()

    features = {
        "has_critical_kw": int(any(kw in text for kw in PRIORITY_KEYWORDS["critical"])),
        "has_high_kw": int(any(kw in text for kw in PRIORITY_KEYWORDS["high"])),
        "has_medium_kw": int(any(kw in text for kw in PRIORITY_KEYWORDS["medium"])),
        "has_low_kw": int(any(kw in text for kw in PRIORITY_KEYWORDS["low"])),
        "text_length": min(len(text) / 200.0, 1.0),
        "has_number": int(bool(__import__("re").search(r"\d+", text))),
        "has_urgency": int("urgent" in text or "immediately" in text or "emergency" in text),
        "has_people_ref": int("people" in text or "residents" in text or "families" in text
                              or "children" in text or "elderly" in text or "women" in text),
        "has_safety_risk": int("danger" in text or "unsafe" in text or "accident" in text
                               or "risk" in text or "hazard" in text),
        "has_duration_long": int(
            any(kw in text for kw in ["month", "weeks", "10 days", "15 days", "months"])
        ),
    }

    # Category one-hot
    categories = ["Water Supply", "Roads", "Sanitation", "Electricity", "Street Lighting", "Drainage"]
    cat = str(row.get("category", ""))
    for c in categories:
        features[f"cat_{c.replace(' ', '_').lower()}"] = int(cat == c)

    return features


def main():
    print("=" * 60)
    print("  Priority Prediction Training")
    print("=" * 60)

    DATA_PATH = os.path.join("data", "complaints.csv")
    MODEL_DIR = os.path.join("app", "ml", "models")

    if not os.path.exists(DATA_PATH):
        print(f"Dataset not found. Generating...")
        from app.ml.training.generate_dataset import generate_dataset
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        records = generate_dataset(n_per_category=200, output_path=DATA_PATH)
        df = pd.DataFrame(records)
    else:
        df = pd.read_csv(DATA_PATH)

    df = df.dropna(subset=["text", "priority"])
    print(f"[OK] Loaded {len(df)} records")
    print(f"  Priority distribution: {df['priority'].value_counts().to_dict()}")

    # Preprocess text
    from app.ml.preprocessing.text_preprocessor import preprocess
    print("Preprocessing text...")
    df["processed_text"] = df["text"].apply(preprocess)

    # Extract engineered features
    print("Extracting engineered features...")
    eng_features = df.apply(extract_priority_features, axis=1)
    eng_df = pd.DataFrame(list(eng_features))

    label_names = sorted(df["priority"].unique().tolist())
    X_text = df["processed_text"].values
    X_eng = eng_df.values
    y = df["priority"].values

    # Split
    idx = np.arange(len(df))
    train_idx, test_idx = train_test_split(idx, test_size=0.15, random_state=42, stratify=y)

    X_text_train, X_text_test = X_text[train_idx], X_text[test_idx]
    X_eng_train, X_eng_test = X_eng[train_idx], X_eng[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    print(f"Split: train={len(y_train)}, test={len(y_test)}")

    # TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    X_tfidf_train = vectorizer.fit_transform(X_text_train)
    X_tfidf_test = vectorizer.transform(X_text_test)

    # Combine TF-IDF + engineered features
    X_train_combined = sp.hstack([X_tfidf_train, sp.csr_matrix(X_eng_train)])
    X_test_combined = sp.hstack([X_tfidf_test, sp.csr_matrix(X_eng_test)])

    # Train Gradient Boosting on dense array (after converting)
    print("\nTraining Gradient Boosting Classifier...")
    X_train_dense = X_train_combined.toarray()
    X_test_dense = X_test_combined.toarray()

    model = GradientBoostingClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1,
        subsample=0.8, random_state=42
    )
    model.fit(X_train_dense, y_train)

    y_pred = model.predict(X_test_dense)
    y_train_pred = model.predict(X_train_dense)

    acc = accuracy_score(y_test, y_pred)
    train_acc = accuracy_score(y_train, y_train_pred)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=label_names).tolist()
    report = classification_report(y_test, y_pred, labels=label_names,
                                    target_names=label_names, output_dict=True, zero_division=0)

    print(f"  Test Accuracy:  {acc:.4f}")
    print(f"  Train Accuracy: {train_acc:.4f}")
    print(f"  F1 Score:       {f1:.4f}")
    print(f"  Precision:      {prec:.4f}")
    print(f"  Recall:         {rec:.4f}")

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "priority_vectorizer.pkl"))
    joblib.dump(model, os.path.join(MODEL_DIR, "priority_predictor.pkl"))

    metadata = {
        "model_name": "Priority Predictor",
        "algorithm": "Gradient Boosting",
        "accuracy": acc,
        "train_accuracy": train_acc,
        "f1_score": f1,
        "precision": prec,
        "recall": rec,
        "confusion_matrix": cm,
        "label_names": label_names,
        "version": "1.0.0",
    }
    with open(os.path.join(MODEL_DIR, "priority_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n[OK] Vectorizer saved: {os.path.join(MODEL_DIR, 'priority_vectorizer.pkl')}")
    print(f"[OK] Model saved:      {os.path.join(MODEL_DIR, 'priority_predictor.pkl')}")

    # Save to DB
    try:
        from app.core.database import SessionLocal
        from app.models.prediction import ModelEvaluation
        from datetime import datetime, timezone

        db = SessionLocal()
        try:
            db.query(ModelEvaluation).filter(
                ModelEvaluation.model_type == "priority"
            ).update({"is_active": False})

            eval_record = ModelEvaluation(
                id=str(uuid.uuid4()),
                model_name="Priority Predictor — Gradient Boosting",
                model_type="priority",
                algorithm="Gradient Boosting (TF-IDF + Engineered Features)",
                accuracy=acc,
                train_accuracy=train_acc,
                precision_score=prec,
                recall_score=rec,
                f1_score=f1,
                confusion_matrix=cm,
                classification_report=report,
                label_names=label_names,
                dataset_size=len(df),
                train_size=len(y_train),
                test_size=len(y_test),
                is_active=True,
                evaluated_at=datetime.now(timezone.utc),
            )
            db.add(eval_record)
            db.commit()
            print("[OK] Metrics saved to database.")
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: Could not save metrics to DB: {e}")

    print("\n" + "=" * 60)
    print("  Priority Training Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
