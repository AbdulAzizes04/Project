"""
Sleep Disorder AI - Model Training & Selection Pipeline
Trains 5 machine learning models, performs 5-fold cross-validation,
evaluates performance metrics, and saves the best model.
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

# Add root project path to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from ml.preprocess import (
    load_and_inspect_dataset,
    clean_data,
    build_preprocessor,
    TARGET_COLUMN,
    TARGET_MAPPING,
    REVERSE_TARGET_MAPPING,
    CATEGORICAL_COLS,
    NUMERICAL_COLS
)
from ml.evaluate import evaluate_classification_model

def train_and_compare_models(dataset_path="data/dataset.csv", output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    all_models_dir = os.path.join(output_dir, "all_models")
    os.makedirs(all_models_dir, exist_ok=True)
    
    # 1. Load and clean data
    df_raw = load_and_inspect_dataset(dataset_path)
    df_clean = clean_data(df_raw)
    
    X = df_clean.drop(columns=[TARGET_COLUMN])
    y = df_clean[TARGET_COLUMN].map(TARGET_MAPPING).values
    
    # 2. Stratified train-test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    
    print(f"\nTrain set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")
    
    # 3. Fit preprocessor ONLY on training data (Strict No Data Leakage)
    preprocessor = build_preprocessor()
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    # Extract feature names
    ohe = preprocessor.named_transformers_["cat"]
    cat_feature_names = list(ohe.get_feature_names_out(CATEGORICAL_COLS))
    feature_names = NUMERICAL_COLS + cat_feature_names
    
    # Save preprocessor and feature names
    joblib.dump(preprocessor, os.path.join(output_dir, "preprocessor.pkl"))
    joblib.dump(feature_names, os.path.join(output_dir, "feature_names.pkl"))
    
    # 4. Define candidate models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, min_samples_split=4, random_state=42),
        "Support Vector Machine": SVC(probability=True, kernel="rbf", C=1.0, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        "XGBoost": XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            eval_metric="mlogloss",
            random_state=42
        )
    }
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    
    print("\n" + "=" * 90)
    print("MODEL BENCHMARKING & 5-FOLD CROSS VALIDATION")
    print("=" * 90)
    print(f"{'Model':<25} | {'Accuracy':<9} | {'Precision':<9} | {'Recall':<9} | {'F1 (Macro)':<10} | {'ROC-AUC':<8} | {'CV F1 (±Std)':<12}")
    print("-" * 90)
    
    best_model_name = None
    best_f1 = -1.0
    best_model_obj = None
    
    for name, model in models.items():
        # Stratified 5-Fold Cross Validation on Training Data
        cv_scores = cross_val_score(model, X_train_proc, y_train, cv=skf, scoring="f1_macro")
        cv_mean = float(np.mean(cv_scores))
        cv_std = float(np.std(cv_scores))
        
        # Train on full training set
        model.fit(X_train_proc, y_train)
        
        # Save individual model
        slug = name.lower().replace(" ", "_")
        joblib.dump(model, os.path.join(all_models_dir, f"{slug}.pkl"))
        
        # Evaluate on unseen test set
        metrics = evaluate_classification_model(
            model, X_test_proc, y_test, class_names=["None", "Insomnia", "Sleep Apnea"]
        )
        metrics["cv_f1_mean"] = cv_mean
        metrics["cv_f1_std"] = cv_std
        results[name] = metrics
        
        auc_str = f"{metrics['roc_auc']:.4f}" if metrics['roc_auc'] is not None else "N/A"
        print(f"{name:<25} | {metrics['accuracy']:.4f}    | {metrics['precision_macro']:.4f}    | {metrics['recall_macro']:.4f}    | {metrics['f1_macro']:.4f}     | {auc_str:<8} | {cv_mean:.3f} (±{cv_std:.3f})")
        
        # Selection criterion: Macro F1-score (balances minority classes: Insomnia & Sleep Apnea)
        if metrics["f1_macro"] > best_f1:
            best_f1 = metrics["f1_macro"]
            best_model_name = name
            best_model_obj = model
            
    print("=" * 90)
    print(f"\n[WINNER] Best Performing Model: {best_model_name} with Macro-F1 = {best_f1:.4f}")
    
    # 5. Save best model and all metrics
    joblib.dump(best_model_obj, os.path.join(output_dir, "best_model.pkl"))
    
    output_metadata = {
        "best_model_name": best_model_name,
        "selection_metric": "Macro F1-Score",
        "best_f1_macro": best_f1,
        "target_mapping": TARGET_MAPPING,
        "reverse_target_mapping": {str(k): v for k, v in REVERSE_TARGET_MAPPING.items()},
        "feature_count": len(feature_names),
        "models": results
    }
    
    with open(os.path.join(output_dir, "model_metrics.json"), "w") as f:
        json.dump(output_metadata, f, indent=4)
        
    print(f"[OK] Best model saved to: {os.path.join(output_dir, 'best_model.pkl')}")
    print(f"[OK] Metrics saved to: {os.path.join(output_dir, 'model_metrics.json')}")
    
    return best_model_name, results

if __name__ == "__main__":
    train_and_compare_models()
