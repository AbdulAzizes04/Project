"""
Evaluation & Imbalance Metrics Engine for GuidedGuard.

In highly imbalanced digital payment fraud datasets (positive class typically 0.1% to 1.5%),
standard Accuracy is dangerously misleading. A trivial classifier predicting 100% legitimate
achieves 99% accuracy while missing all scams.

This module computes comprehensive imbalance evaluation metrics:
- PR-AUC (Precision-Recall AUC / Average Precision) - Primary Metric
- ROC-AUC
- Precision, Recall, F1-Score
- Specificity (True Negative Rate)
- False Positive Rate (FPR), False Negative Rate (FNR)
- Brier Score (Probabilistic Calibration)
- Precision@K & Recall@K (Operational triage capacity)
- Automated generation of publication-grade diagnostic plots (outputs/reports/):
  confusion_matrix.png, roc_curve.png, precision_recall_curve.png, calibration_curve.png
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    precision_recall_curve,
    roc_curve,
    confusion_matrix,
    brier_score_loss,
)
from sklearn.calibration import calibration_curve


def calculate_metrics(y_true: np.ndarray, y_proba: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Calculate full suite of imbalanced classification metrics.
    """
    y_true = np.array(y_true, dtype=int)
    y_proba = np.array(y_proba, dtype=float)
    y_pred = (y_proba >= threshold).astype(int)

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (cm[0, 0], 0, 0, 0)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_proba))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_proba))
    except Exception:
        pr_auc = float(np.mean(y_true))

    spec = float(tn / max(1, tn + fp))
    fpr = float(fp / max(1, fp + tn))
    fnr = float(fn / max(1, fn + tp))
    brier = float(brier_score_loss(y_true, y_proba))

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "average_precision": round(pr_auc, 4),
        "specificity": round(spec, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "brier_score": round(brier, 4),
        "threshold_used": float(threshold),
        "confusion_matrix": cm.tolist(),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def calculate_precision_recall_at_k(y_true: np.ndarray, y_proba: np.ndarray, k_values: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Compute Precision@K and Recall@K for fixed operational review budgets.
    Fraud investigation teams can only review K flagged transactions per shift.
    Precision@K measures: Out of the top K highest-risk alerts, how many are actual fraud?
    """
    y_true = np.array(y_true, dtype=int)
    y_proba = np.array(y_proba, dtype=float)
    n = len(y_true)
    total_positives = int(np.sum(y_true))

    if k_values is None:
        # Dynamically scale K based on test set size
        k_values = [min(n, 50), min(n, 100), min(n, 250), min(n, 500)]
        k_values = sorted(list(set([k for k in k_values if k > 0])))

    order = np.argsort(-y_proba)
    sorted_y_true = y_true[order]

    results = {}
    for k in k_values:
        if k > n:
            continue
        top_k_labels = sorted_y_true[:k]
        tp_k = int(np.sum(top_k_labels))
        prec_k = float(tp_k / k)
        rec_k = float(tp_k / max(1, total_positives))

        results[f"P@{k}"] = round(prec_k, 4)
        results[f"R@{k}"] = round(rec_k, 4)
        results[f"TP@{k}"] = tp_k

    results["total_positives_in_set"] = total_positives
    results["total_evaluated_records"] = n
    return results


def generate_evaluation_plots(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    output_dir: Path,
    model_name: str = "GuidedGuard Model",
) -> Dict[str, str]:
    """
    Generate and save high-resolution diagnostic plots:
    1. confusion_matrix.png
    2. roc_curve.png
    3. precision_recall_curve.png
    4. calibration_curve.png
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    y_true = np.array(y_true, dtype=int)
    y_proba = np.array(y_proba, dtype=float)
    y_pred = (y_proba >= 0.5).astype(int)

    # Styling defaults for dark/clean presentation
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Confusion Matrix
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    cm = confusion_matrix(y_true, y_pred)
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=["Legitimate", "Scam"],
        yticklabels=["Legitimate", "Scam"],
        title=f"Confusion Matrix — {model_name}",
        ylabel="True Label",
        xlabel="Predicted Label",
    )
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"), ha="center", va="center", color="white" if cm[i, j] > thresh else "black", fontweight="bold")
    plt.tight_layout()
    cm_path = output_dir / "confusion_matrix.png"
    plt.savefig(cm_path, bbox_inches="tight")
    plt.close()
    paths["confusion_matrix"] = str(cm_path)

    # 2. ROC Curve
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_val = roc_auc_score(y_true, y_proba)
    ax.plot(fpr, tpr, color="#6366F1", lw=2, label=f"ROC Curve (AUC = {roc_val:.4f})")
    ax.plot([0, 1], [0, 1], color="#94A3B8", lw=1.5, linestyle="--", label="Random Classifier (0.50)")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Recall)")
    ax.set_title(f"ROC Curve — {model_name}")
    ax.legend(loc="lower right")
    plt.tight_layout()
    roc_path = output_dir / "roc_curve.png"
    plt.savefig(roc_path, bbox_inches="tight")
    plt.close()
    paths["roc_curve"] = str(roc_path)

    # 3. Precision-Recall Curve
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    prec_pts, rec_pts, _ = precision_recall_curve(y_true, y_proba)
    pr_val = average_precision_score(y_true, y_proba)
    baseline_prev = np.mean(y_true)
    ax.plot(rec_pts, prec_pts, color="#06B6D4", lw=2, label=f"PR Curve (PR-AUC = {pr_val:.4f})")
    ax.axhline(y=baseline_prev, color="#EF4444", linestyle="--", label=f"Class Prevalence ({baseline_prev:.2%})")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("Recall (Coverage)")
    ax.set_ylabel("Precision (Accuracy of Flags)")
    ax.set_title(f"Precision-Recall Curve — {model_name}")
    ax.legend(loc="upper right")
    plt.tight_layout()
    pr_path = output_dir / "precision_recall_curve.png"
    plt.savefig(pr_path, bbox_inches="tight")
    plt.close()
    paths["precision_recall_curve"] = str(pr_path)

    # 4. Calibration Curve (Reliability Diagram)
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=10, strategy="uniform")
    brier_val = brier_score_loss(y_true, y_proba)
    ax.plot(prob_pred, prob_true, marker="o", lw=2, color="#10B981", label=f"Model (Brier = {brier_val:.4f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="#94A3B8", label="Perfect Calibration")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title(f"Calibration Curve — {model_name}")
    ax.legend(loc="upper left")
    plt.tight_layout()
    cal_path = output_dir / "calibration_curve.png"
    plt.savefig(cal_path, bbox_inches="tight")
    plt.close()
    paths["calibration_curve"] = str(cal_path)

    return paths


# Backward compatibility and test aliases
def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
    """Compatibility wrapper returning metrics dictionary."""
    res = calculate_metrics(y_true, y_prob)
    res["f1_score"] = res["f1"]
    return res


def compute_precision_recall_at_k(y_true: np.ndarray, y_prob: np.ndarray, k: int = 2) -> Tuple[float, float]:
    """Compatibility wrapper returning (Precision@K, Recall@K)."""
    res = calculate_precision_recall_at_k(y_true, y_prob, k_values=[k])
    return res.get(f"P@{k}", 0.0), res.get(f"R@{k}", 0.0)
