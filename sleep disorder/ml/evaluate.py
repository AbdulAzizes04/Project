"""
Evaluation Module for Sleep Disorder Classification Models
"""
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

def evaluate_classification_model(model, X_test, y_test, class_names=None):
    """
    Computes rigorous metrics on test data:
    - Accuracy
    - Precision (Macro & Weighted)
    - Recall (Macro & Weighted)
    - F1-Score (Macro & Weighted)
    - ROC-AUC (One-vs-Rest Macro) if probabilities available
    - Confusion Matrix
    """
    if class_names is None:
        class_names = ["None", "Insomnia", "Sleep Apnea"]
        
    y_pred = model.predict(X_test)
    
    accuracy = float(accuracy_score(y_test, y_pred))
    precision_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    precision_weighted = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    recall_weighted = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    
    # Calculate ROC-AUC if predict_proba is supported
    roc_auc = None
    if hasattr(model, "predict_proba"):
        try:
            y_proba = model.predict_proba(X_test)
            roc_auc = float(roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro"))
        except Exception:
            roc_auc = None
            
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    
    return {
        "accuracy": accuracy,
        "precision_macro": precision_macro,
        "precision_weighted": precision_weighted,
        "recall_macro": recall_macro,
        "recall_weighted": recall_weighted,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
        "classification_report": report
    }
