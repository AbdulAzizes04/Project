"""
Cost-Sensitive Evaluation & Threshold Optimization for GuidedGuard.

In banking operations, false positives and false negatives carry asymmetric business costs:
- False Positive (FP): Friction to genuine user, SMS challenge cost, or investigator triage time ($15 - $50).
- False Negative (FN): Direct customer loss, unrecoverable scam payout, chargeback liability ($500 - $5,000+).

Cost Matrix:
                     ACTUAL
                 Legitimate (0)     Scam (1)
PRED Legit (0)         $0            FN_COST
PRED Scam  (1)      FP_COST            $0

This module evaluates expected operational costs across candidate thresholds [0.05 ... 0.95]
to locate the cost-optimal decision threshold.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


def evaluate_cost_matrix(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    fp_cost: float = 25.0,
    fn_cost: float = 1000.0,
    thresholds: Optional[List[float]] = None,
) -> pd.DataFrame:
    """
    Evaluate expected cost across decision thresholds.
    """
    if thresholds is None:
        thresholds = [round(t, 2) for t in np.linspace(0.05, 0.95, 19)]

    rows = []
    y_true = np.array(y_true, dtype=int)
    y_proba = np.array(y_proba, dtype=float)
    n = len(y_true)

    for thresh in thresholds:
        y_pred = (y_proba >= thresh).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (cm[0, 0], 0, 0, 0)

        prec = float(tp / max(1, tp + fp))
        rec = float(tp / max(1, tp + fn))
        fpr = float(fp / max(1, fp + tn))
        fnr = float(fn / max(1, fn + tp))

        # Expected operational cost
        total_cost = (fp * fp_cost) + (fn * fn_cost)
        avg_cost_per_txn = total_cost / max(1, n)

        rows.append({
            "Threshold": thresh,
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "FPR": round(fpr, 4),
            "FNR": round(fnr, 4),
            "FP_Count": int(fp),
            "FN_Count": int(fn),
            "Total_Cost": round(total_cost, 2),
            "Expected_Cost_Per_Txn": round(avg_cost_per_txn, 2),
        })

    df_cost = pd.DataFrame(rows)
    return df_cost


def find_optimal_threshold(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    fp_cost: float = 25.0,
    fn_cost: float = 1000.0,
) -> Dict[str, Any]:
    """
    Identify decision threshold that minimizes total financial loss.
    """
    df_cost = evaluate_cost_matrix(y_true, y_proba, fp_cost=fp_cost, fn_cost=fn_cost)
    best_row = df_cost.loc[df_cost["Total_Cost"].idxmin()]

    return {
        "optimal_threshold": float(best_row["Threshold"]),
        "minimum_cost": float(best_row["Total_Cost"]),
        "precision_at_optimal": float(best_row["Precision"]),
        "recall_at_optimal": float(best_row["Recall"]),
        "assumed_fp_cost": fp_cost,
        "assumed_fn_cost": fn_cost,
        "cost_evaluation_table": df_cost,
    }
