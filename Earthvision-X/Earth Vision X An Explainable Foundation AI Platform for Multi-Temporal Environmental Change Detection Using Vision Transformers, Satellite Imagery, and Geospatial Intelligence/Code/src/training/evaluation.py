"""
Scientific Evaluation Suite for Environmental Change Detection.
Computes IEEE standard evaluation metrics:
- Segmentation: IoU (Jaccard), mIoU, Dice Score, F1, Precision, Recall, Pixel Accuracy
- Classification: Overall Accuracy, Macro Precision, Macro Recall, Macro F1, Confusion Matrix
"""

import numpy as np
from typing import Dict, Any, Tuple
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score

class ChangeDetectionEvaluator:
    """
    Computes rigorous segmentation and classification metrics from predictions and ground truth.
    """

    @staticmethod
    def evaluate_segmentation(
        pred_mask: np.ndarray,
        gt_mask: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculates pixel-level change segmentation metrics.
        pred_mask: Binary numpy array (H, W), values {0, 1}
        gt_mask: Binary ground truth array (H, W), values {0, 1}
        """
        p = (pred_mask > 0).astype(np.uint8).flatten()
        g = (gt_mask > 0).astype(np.uint8).flatten()

        # True Positives, False Positives, False Negatives, True Negatives
        tp = int(np.sum((p == 1) & (g == 1)))
        fp = int(np.sum((p == 1) & (g == 0)))
        fn = int(np.sum((p == 0) & (g == 1)))
        tn = int(np.sum((p == 0) & (g == 0)))

        # Precision, Recall, Specificity
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0

        # F1 Score & Dice
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        dice = (2.0 * tp) / (2.0 * tp + fp + fn) if (2.0 * tp + fp + fn) > 0 else 1.0

        # IoU for change class (class 1)
        iou_change = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 1.0
        # IoU for background class (class 0)
        iou_bg = tn / (tn + fp + fn) if (tn + fp + fn) > 0 else 1.0
        miou = (iou_change + iou_bg) / 2.0

        # Pixel Accuracy
        pixel_accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 1.0

        return {
            "iou": round(float(iou_change), 4),
            "miou": round(float(miou), 4),
            "dice": round(float(dice), 4),
            "f1": round(float(f1), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "specificity": round(float(specificity), 4),
            "pixel_accuracy": round(float(pixel_accuracy), 4),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn
        }

    @staticmethod
    def evaluate_classification(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        class_names: list
    ) -> Dict[str, Any]:
        """
        Calculates multi-class environmental classification metrics.
        """
        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))

        return {
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(prec), 4),
            "macro_recall": round(float(rec), 4),
            "macro_f1": round(float(f1), 4),
            "confusion_matrix": cm.tolist()
        }
