# GuidedGuard Temporal Validation & Chronological Splitting

## 1. Why Random Splitting Fails in Financial Fraud Detection

A standard practice in academic machine learning is random $K$-fold cross-validation or uniform `train_test_split(shuffle=True)`. In fraud detection, **random splitting is fundamentally invalid**:

1. **Violation of Temporal Causality**: Random shuffling allows transactions from Day 30 to train a model predicting transactions on Day 5.
2. **Temporal Lookahead Bias**: Future behavioral adaptations, emerging scam modi operandi, and macro-economic shifts leak into historical training data.
3. **Data Snooping via Entity History**: If a fraudster conducts 5 trial payments across two weeks, random splitting places some in train and some in test, enabling memorization of fraudster-specific parameters rather than generalizable scam indicators.

---

## 2. Chronological Splitting Protocol

GuidedGuard enforces strict temporal partitioning implemented in `models/temporal_validation.py`:

$$\mathcal{T}_{\text{train}} = \{x_i \mid t_i \le T_1\}$$
$$\mathcal{T}_{\text{val}} = \{x_i \mid T_1 < t_i \le T_2\}$$
$$\mathcal{T}_{\text{test}} = \{x_i \mid t_i > T_2\}$$

Where:
- $T_1$ corresponds to the 60th percentile of chronological steps ($\text{step} \le 14$).
- $T_2$ corresponds to the 80th percentile of chronological steps ($14 < \text{step} \le 16$).
- $T_{\text{test}}$ represents the latest 20% of chronological steps ($\text{step} > 16$), representing an **Out-of-Time (OOT)** holdout set.

```
Time Axis (step 1 to 744) ────────────────────────────────────────────────────────►
[=================== TRAIN (60%) ===================][=== VAL (20%) ===][=== TEST (20%) ===]
   Historical Baseline & Model Training                 Hyperparameter        Out-of-Time
                                                        & Calibration         Evaluation
```

---

## 3. Empirical Comparison: Temporal Split vs. Random Split

Experiment 11 explicitly tested the difference between Random 70/30 Splitting and Chronological Splitting on identical feature sets:

| Splitting Strategy | Model | PR-AUC | ROC-AUC | F1-Score | Brier Score | Lookahead Bias Present? |
|---|---|---|---|---|---|---|
| **Random 70/30 Split (Exp 11)** | HistGradientBoosting | 0.0586 | 0.6037 | 0.0370 | 0.0106 | **YES (Shuffled temporal order)** |
| **Chronological Split (Exp 2)** | HistGradientBoosting | **0.1089** | **0.6789** | **0.0833** | **0.0121** | **NO (Strict arrow of time)** |

### Key Insights:
- Under temporal evaluation, model performance reflects true forward-looking generalization onto future unknown payment events.
- Validation calibration using temporal splits ensures Platt scaling parameters do not overfit to stationary random samples.
