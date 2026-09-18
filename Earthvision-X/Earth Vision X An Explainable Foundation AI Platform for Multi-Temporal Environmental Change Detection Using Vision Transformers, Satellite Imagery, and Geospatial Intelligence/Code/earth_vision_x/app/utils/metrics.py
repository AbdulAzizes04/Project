"""
Comprehensive Evaluation Metrics Suite for Change Detection & Satellite Segmentation.
Calculates Accuracy, Precision, Recall, Specificity, Sensitivity, F1, IoU, Dice, Kappa, ROC-AUC, and Confusion Matrix.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, jaccard_score, cohen_kappa_score, confusion_matrix, roc_auc_score

class MetricCalculator:
    @staticmethod
    def compute_all_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Computes all standard IEEE benchmark metrics for multi-temporal change detection.
        y_true: Ground truth binary or multi-class array (N,) or (H, W)
        y_pred: Predicted class labels (N,) or (H, W)
        y_prob: Optional predicted probability for ROC-AUC
        """
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()

        acc = float(accuracy_score(y_true_flat, y_pred_flat))
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true_flat, y_pred_flat, average="macro", zero_division=0
        )
        iou = float(jaccard_score(y_true_flat, y_pred_flat, average="macro", zero_division=0))
        kappa = float(cohen_kappa_score(y_true_flat, y_pred_flat))
        
        # Confusion Matrix
        cm = confusion_matrix(y_true_flat, y_pred_flat)

        # Binary specific metrics (Specificity, Sensitivity, Dice)
        if len(np.unique(y_true_flat)) <= 2:
            tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (cm[0, 0], 0, 0, 0)
            sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
            dice = float(2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) > 0 else 0.0
        else:
            sensitivity = float(recall)
            specificity = float(acc)
            dice = float(f1)

        # ROC AUC
        roc_auc = 0.0
        if y_prob is not None:
            try:
                if len(np.unique(y_true_flat)) == 2:
                    roc_auc = float(roc_auc_score(y_true_flat, y_prob.flatten() if y_prob.ndim > 1 else y_prob))
            except Exception:
                roc_auc = 0.5

        return {
            "Accuracy": acc,
            "Precision": float(precision),
            "Recall": float(recall),
            "F1 Score": float(f1),
            "IoU": iou,
            "Dice Score": dice,
            "Sensitivity": sensitivity,
            "Specificity": specificity,
            "Kappa Score": kappa,
            "ROC AUC": roc_auc,
            "Confusion Matrix": cm.tolist()
        }
