"""
Train all ML models — RF, XGBoost, LightGBM, SVM, ANN
"""
import sys, json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import xgboost as xgb
import lightgbm as lgb

BASE = Path(__file__).resolve().parent
DATASETS_DIR = BASE.parent / "datasets"
MODELS_DIR = BASE / "saved_models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = [
    "age", "gender_enc", "weight", "height", "bmi", "pulse_rate",
    "fatigue", "weight_gain", "weight_loss", "hair_loss", "constipation",
    "anxiety", "depression", "sweating", "neck_swelling", "voice_changes",
    "cold_intolerance", "heat_intolerance", "difficulty_swallowing", "sleep_disturbance",
    "tsh", "t3", "t4", "ft3", "ft4",
    "hemoglobin", "wbc", "rbc", "platelets", "vitamin_d", "calcium",
    "diabetes", "hypertension", "family_history", "smoking", "alcohol"
]


def load_or_generate_dataset():
    csv_path = DATASETS_DIR / "thyroid_dataset.csv"
    if not csv_path.exists():
        print("[Train] Dataset not found — generating...")
        import subprocess
        subprocess.run([sys.executable, str(BASE / "generate_dataset.py")], check=True)
    df = pd.read_csv(csv_path)
    return df


def evaluate(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec  = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1   = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    print(f"  [{name}] Accuracy={acc:.3f} Precision={prec:.3f} Recall={rec:.3f} F1={f1:.3f}")
    return {"accuracy": round(acc, 4), "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}


def train_ann(X_train, y_train, X_test, y_test, n_classes):
    """Train a simple ANN using TensorFlow/Keras and wrap for scikit-learn API."""
    try:
        import tensorflow as tf
        from tensorflow import keras
        from sklearn.preprocessing import LabelBinarizer

        tf.random.set_seed(42)
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(n_classes, activation='softmax'),
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(
            X_train, y_train,
            validation_split=0.1,
            epochs=60, batch_size=32, verbose=0,
            callbacks=[keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True)]
        )

        # Wrap for sklearn-compatible predict_proba
        class ANNWrapper:
            def __init__(self, keras_model):
                self.model = keras_model
                self.classes_ = np.arange(n_classes)

            def predict(self, X):
                return np.argmax(self.model.predict(X, verbose=0), axis=1)

            def predict_proba(self, X):
                return self.model.predict(X, verbose=0)

        wrapper = ANNWrapper(model)
        y_pred = wrapper.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec  = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1   = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        print(f"  [ANN] Accuracy={acc:.3f} Precision={prec:.3f} Recall={rec:.3f} F1={f1:.3f}")
        return wrapper, {"accuracy": round(acc, 4), "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

    except Exception as e:
        print(f"  [ANN] TensorFlow error: {e} — using RF as fallback")
        fallback = RandomForestClassifier(n_estimators=50, random_state=42)
        fallback.fit(X_train, y_train)
        metrics = evaluate(fallback, X_test, y_test, "ANN-fallback")
        return fallback, metrics


def main():
    print("=" * 60)
    print("ThyroAI — Model Training Pipeline")
    print("=" * 60)

    # Load data
    df = load_or_generate_dataset()
    X = df[FEATURE_COLS].values
    y = df['label'].values
    n_classes = len(np.unique(y))
    print(f"[Train] Dataset: {len(df)} samples, {n_classes} classes, {X.shape[1]} features")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Scale
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    print("[Train] Scaler saved")

    metrics = {}

    # ── Random Forest ──────────────────────────────────────────────────────────
    print("\n[Train] Random Forest...")
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train_sc, y_train)
    metrics['rf'] = evaluate(rf, X_test_sc, y_test, "RF")
    joblib.dump(rf, MODELS_DIR / "rf_model.pkl")

    # ── XGBoost ────────────────────────────────────────────────────────────────
    print("[Train] XGBoost...")
    xgb_clf = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        use_label_encoder=False, eval_metric='mlogloss', random_state=42, verbosity=0
    )
    xgb_clf.fit(X_train_sc, y_train, eval_set=[(X_test_sc, y_test)], verbose=False)
    metrics['xgb'] = evaluate(xgb_clf, X_test_sc, y_test, "XGB")
    joblib.dump(xgb_clf, MODELS_DIR / "xgb_model.pkl")

    # ── LightGBM ───────────────────────────────────────────────────────────────
    print("[Train] LightGBM...")
    lgbm_clf = lgb.LGBMClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42, verbose=-1)
    lgbm_clf.fit(X_train_sc, y_train, eval_set=[(X_test_sc, y_test)],
                 callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(period=-1)])
    metrics['lgbm'] = evaluate(lgbm_clf, X_test_sc, y_test, "LGBM")
    joblib.dump(lgbm_clf, MODELS_DIR / "lgbm_model.pkl")

    # ── SVM ────────────────────────────────────────────────────────────────────
    print("[Train] SVM...")
    svm_clf = SVC(kernel='rbf', probability=True, C=10, gamma='scale', random_state=42)
    svm_clf.fit(X_train_sc, y_train)
    metrics['svm'] = evaluate(svm_clf, X_test_sc, y_test, "SVM")
    joblib.dump(svm_clf, MODELS_DIR / "svm_model.pkl")

    # ── ANN ────────────────────────────────────────────────────────────────────
    print("[Train] ANN (TensorFlow/Keras)...")
    ann_model, ann_metrics = train_ann(X_train_sc, y_train, X_test_sc, y_test, n_classes)
    metrics['ann'] = ann_metrics
    joblib.dump(ann_model, MODELS_DIR / "ann_model.pkl")

    # ── Ensemble ───────────────────────────────────────────────────────────────
    print("\n[Train] Evaluating Ensemble...")
    WEIGHTS = {"rf": 0.30, "xgb": 0.30, "lgbm": 0.20, "svm": 0.10, "ann": 0.10}
    models = {"rf": rf, "xgb": xgb_clf, "lgbm": lgbm_clf, "svm": svm_clf, "ann": ann_model}
    ensemble_probas = np.zeros((len(X_test_sc), n_classes))
    for name, w in WEIGHTS.items():
        m = models[name]
        if hasattr(m, 'predict_proba'):
            p = m.predict_proba(X_test_sc)
            if p.shape[1] < n_classes:
                pad = np.zeros((p.shape[0], n_classes))
                pad[:, :p.shape[1]] = p
                p = pad
            ensemble_probas += w * p
    y_ensemble = np.argmax(ensemble_probas, axis=1)
    acc = accuracy_score(y_test, y_ensemble)
    prec = precision_score(y_test, y_ensemble, average='weighted', zero_division=0)
    rec  = recall_score(y_test, y_ensemble, average='weighted', zero_division=0)
    f1   = f1_score(y_test, y_ensemble, average='weighted', zero_division=0)
    print(f"  [Ensemble] Accuracy={acc:.3f} Precision={prec:.3f} Recall={rec:.3f} F1={f1:.3f}")
    metrics['ensemble'] = {"accuracy": round(acc, 4), "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

    # Save metrics
    with open(MODELS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ All models trained and saved!")
    print(f"   Location: {MODELS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
