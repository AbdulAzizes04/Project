# GuidedGuard Data Leakage Audit: Forensic Report & Methodology

## 1. Executive Summary: The 100% Accuracy Myth

In preliminary and historical iterations of fraud detection on the PaySim benchmark, models frequently reported **100.0% accuracy, 1.00 ROC-AUC, and 0 false negatives**. 

GuidedGuard's systematic codebase audit revealed that these metrics were not evidence of superior algorithmic performance, but the artifact of **catastrophic post-transaction data leakage**:
- In the PaySim synthetic data generation process, fraudulent transactions (`isFraud == 1`) unconditionally zeroed out the victim's account balance: `newbalanceOrig = 0.0`.
- Classifiers trained on `newbalanceOrig` or engineered features such as `balance_wipeout_orig = ((oldbalanceOrg > 500) & (newbalanceOrig == 0))` simply memorized this deterministic post-clearing signature.
- In production, `newbalanceOrig` **does not exist at the time of payment authorization**. Feeding post-settlement variables into an authorization-time classifier is fatal to real-world deployment.

---

## 2. Forensic Analysis of Leaking Columns

| Leaking Feature | Type of Leakage | Leakage Mechanism | Correlation with Target | Action Taken |
|---|---|---|---|---|
| `newbalanceOrig` | Post-Settlement State | Origin account balance *after* funds have been cleared and debited. | Strong negative correlation with fraud. | **PERMANENTLY EXCLUDED** |
| `newbalanceDest` | Post-Settlement State | Recipient account balance *after* funds have cleared. | Strong positive correlation with fraud. | **PERMANENTLY EXCLUDED** |
| `balance_wipeout_orig` | Derived Post-Settlement | Explicit flag checking if `oldbalanceOrg > 0` and `newbalanceOrig == 0`. | Near-deterministic target proxy ($>0.95$). | **PERMANENTLY EXCLUDED** |
| `balance_diff_orig` | Post-Settlement Arithmetic | `oldbalanceOrg - newbalanceOrig`. | Bypasses authorization uncertainty. | **PERMANENTLY EXCLUDED** |
| `balance_error_orig` | Post-Settlement Discrepancy | $| \text{oldbalanceOrg} - \text{amount} - \text{newbalanceOrig} |$. | Directly indicates irregular settlement. | **PERMANENTLY EXCLUDED** |

---

## 3. The 4-Stage Leakage Audit Protocol

GuidedGuard implements an automated leakage audit pipeline in `models/leakage_audit.py` that verifies 4 categories of data leakage:

### Stage 1: Target Leakage Detection
Evaluates whether any input feature is mathematically derived from the ground truth target `isFraud` or shares mutual information approaching 1.0 with the label.

### Stage 2: Temporal Availability Audit
Audits every feature against a banking ledger lifecycle schema:
- **PRE_TRANSACTION**: Available prior to payment initiation (customer history, whitelists).
- **TRANSACTION_TIME**: Observable in the payment API payload (`amount`, `timestamp`, `channel`).
- **POST_TRANSACTION**: Observable only after clearing/settlement. **Flagged as Leakage.**

### Stage 3: Duplicate Record Leakage
Detects identical or near-identical payment payloads spanning training, validation, and test splits that could cause cross-partition memorization.

### Stage 4: Out-of-Order Temporal Leakage
Validates that temporal ordering is strictly preserved and that global aggregations do not leak future summary statistics into historical records.

---

## 4. Audit Artifacts & Verification

The complete audit is programmatically generated and exported to:
- `outputs/reports/leakage_audit.json`: Machine-readable summary with column categorizations and remediation actions.
- `outputs/reports/leakage_audit.csv`: Comprehensive tabular audit matrix listing all 56 candidate features.

### Scientific Impact of Remediation:
- Pre-Remediation (with leakage): PR-AUC = **0.7357**, Accuracy = **99.55%** (Exp 1).
- Post-Remediation (authorization-time only): PR-AUC = **0.1205** (XGBoost), PR-AUC = **0.1089** (HistGBM).
- While numerical scores are lower, post-remediation models are **scientifically honest, publication-quality, and viable for real-world deployment**.
