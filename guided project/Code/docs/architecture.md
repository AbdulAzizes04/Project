# GuidedGuard Architecture Documentation

## 1. System Overview

**GuidedGuard** is an Explainable AI (XAI) behavioural risk assessment framework engineered specifically to identify digital payment transactions exhibiting patterns consistent with **Authorised Push Payment (APP) scam-guided fraud**. 

In conventional unauthorized fraud (e.g., account takeover, credential theft), unauthorized actors initiate transactions from foreign environments. In contrast, in APP scams, legitimate authenticated customers are socially engineered into willingly authorizing payments to fraudulent accounts under coercion, false pretenses, or deceptive urgency (e.g., impersonation of law enforcement, tax officials, or bank security teams).

GuidedGuard addresses this paradigm by evaluating transactions strictly at **pre-transaction authorization time**, using a **dual-engine architecture** (Calibrated Supervised Machine Learning + Unsupervised Anomaly Detection) coupled with an **8-signal risk fusion engine** and **multi-layered explainability**.

```
                               +--------------------------------------------------------+
                               |              TRANSACTION AUTHORIZATION EVENT           |
                               |  Amount, Type, Origin Balance Before, Sender, Recipient |
                               +--------------------------------------------------------+
                                                           |
                                                           v
                               +--------------------------------------------------------+
                               |          AUTHORIZATION FEATURE PIPELINE (19 Feats)     |
                               |  - Behavioral Baseline Profiling  - Temporal Windows   |
                               |  - Rolling Velocity Trackers      - Recipient Risk     |
                               |  - Device & Location Proxies      - ZERO TARGET LEAKAGE|
                               +--------------------------------------------------------+
                                                           |
                                      +--------------------+--------------------+
                                      |                                         |
                                      v                                         v
                      +-------------------------------+         +-------------------------------+
                      |   SUPERVISED ML CLASSIFIER    |         |  UNSUPERVISED ANOMALY DETECTOR|
                      |  - Calibrated XGBoost         |         |  - Isolation Forest           |
                      |  - PR-AUC Optimized (0.0923)  |         |  - Normalized Anomaly (0-100) |
                      +-------------------------------+         +-------------------------------+
                                      |                                         |
                                      +--------------------+--------------------+
                                                           |
                                                           v
                               +--------------------------------------------------------+
                               |               8-SIGNAL RISK FUSION ENGINE              |
                               |  Supervised (35%) + Behavioral (20%) + Anomaly (15%) + |
                               |  Beneficiary (10%) + Velocity (8%) + Device (5%) +     |
                               |  Location (4%) + Temporal (3%) -> Score (0 - 100)       |
                               +--------------------------------------------------------+
                                                           |
                                      +--------------------+--------------------+
                                      |                                         |
                                      v                                         v
                      +-------------------------------+         +-------------------------------+
                      |   EXPLAINABILITY & RECOURSE   |         |    CONTEXTUAL INTERVENTION    |
                      |  - SHAP Waterfall & LIME      |         |  - LOW: Instant Approve       |
                      |  - Minimal Counterfactuals    |         |  - MEDIUM: Dynamic Warning    |
                      |  - Natural Security Narrative |         |  - HIGH: Friction / Callback  |
                      |  - Forensic Case Dossier      |         |  - CRITICAL: 24h Cooling Hold |
                      +-------------------------------+         +-------------------------------+
```

---

## 2. Authorization-Time vs. Post-Settlement Boundaries

A foundational principle of GuidedGuard is the strict boundary between **Authorization Time** and **Post-Settlement Time**:

| Pipeline Stage | Feature Category | Features Included | Allowed at Authorization? |
|---|---|---|---|
| **Pre-Transaction** | Behavioral Baselines | Customer 30-day mean amount, transaction frequency, habitual active hours, known payee whitelist | **YES** (Readily available in customer data store) |
| **Transaction-Time** | Authorization Parameters | Current transaction amount, payment type, origin account balance *prior* to transfer, recipient ID, timestamp | **YES** (Passed in payment gateway payload) |
| **Transaction-Time** | Velocity Trackers | Rolling transaction count and cumulative amount in past 5m, 15m, 1h, 24h | **YES** (Computed from transaction history ledger) |
| **Transaction-Time** | Proxy Novelty | New device indicator, new geographic region indicator, off-hours deviation | **YES** (Computed from session headers) |
| **Post-Transaction** | Post-Settlement Balance | `newbalanceOrig` (origin balance after settlement), `newbalanceDest` (recipient balance after settlement) | **STRICTLY PROHIBITED** (Target Leakage) |
| **Post-Transaction** | Derived Post-Settlement | `balance_wipeout_orig`, `balance_error_orig`, `balance_error_dest` | **STRICTLY PROHIBITED** (Mathematically leaks settlement) |

By filtering all post-settlement features prior to model ingestion, GuidedGuard guarantees that inference relies exclusively on data accessible at the instant the customer clicks "Pay."

---

## 3. Dual-Engine Architecture

### Engine 1: Calibrated Supervised Classifier (XGBoost)
- **Role**: Detects complex non-linear combinations of known historical fraud patterns.
- **Optimization Target**: Precision-Recall AUC (PR-AUC), optimized for extreme class imbalance (1.12% positive prevalence).
- **Calibration**: Probability calibration via Platt scaling (Sigmoid) ensures output probabilities represent empirical likelihood rather than raw overconfident margins.
- **Artifact**: `models/saved_model.pkl` with parameters `max_depth=5, learning_rate=0.1, n_estimators=100`.

### Engine 2: Unsupervised Anomaly Detector (Isolation Forest)
- **Role**: Identifies novel, zero-day, or emerging scam topologies that supervised models have not encountered in training data.
- **Training Corpus**: Fitted exclusively on legitimate transaction patterns (`isFraud == 0`) with `contamination=0.015`.
- **Normalization**: Raw path length decision function is normalized via min-max scaling into a standard 0–100 behavioral anomaly index.
- **Separation**: The anomaly score is treated as an orthogonal risk indicator, never conflated directly with class probability.
- **Artifact**: `models/anomaly_detector.pkl`.

---

## 4. 8-Signal Multi-Modal Risk Fusion

GuidedGuard aggregates disparate risk indicators using a calibrated linear combination model:

$$\text{Composite Risk} = \sum_{i=1}^{8} w_i \cdot S_i$$

Where:
- $S_1$ = Supervised Probability Score ($P \times 100$), weight $w_1 = 0.35$
- $S_2$ = Behavioral Deviation Score (Amount Z-score & Ratio), weight $w_2 = 0.20$
- $S_3$ = Unsupervised Isolation Forest Anomaly Index (0–100), weight $w_3 = 0.15$
- $S_4$ = Beneficiary Risk Index (Payee tenure & novelty), weight $w_4 = 0.10$
- $S_5$ = Rolling Velocity Spike Score (5m, 15m, 1h frequency), weight $w_5 = 0.08$
- $S_6$ = Device Novelty & Risk Indicator, weight $w_6 = 0.05$
- $S_7$ = Geographic Location Discrepancy Indicator, weight $w_7 = 0.04$
- $S_8$ = Temporal / Active Hours Deviation Index, weight $w_8 = 0.03$

Constraint: $\sum_{i=1}^{8} w_i = 1.00$.

### Risk Categorization:
- **LOW** (0 – 29): Normal legitimate payment.
- **MEDIUM** (30 – 59): Minor behavioral or temporal deviation.
- **HIGH** (60 – 79): Significant deviation (unusual amount to newly added payee).
- **CRITICAL** (80 – 100): Severe multi-vector convergence (large velocity spike, novel payee, high anomaly score).

---

## 5. Contextual Intervention Engine

Rather than offering binary "allow" or "block" decisions, GuidedGuard pairs risk tiers with proportional banking friction:

1. **LOW (0–29)**: `APPROVE` — Instant payment pass-through with background ledger logging.
2. **MEDIUM (30–59)**: `STEP_UP_CHALLENGE` — Dynamic in-app warning highlighting payee novelty, requiring biometric or 2FA re-authentication.
3. **HIGH (60–79)**: `FRICTION_CALLBACK` — 1-hour delay with interactive scam awareness checklist ("Are you paying someone who called claiming to be police?").
4. **CRITICAL (80–100)**: `COOLING_OFF_HOLD` — 24-hour cooling-off hold on funds release, outbound security operations center (SOC) verification, and customer push alert.

---

## 6. Software Architecture & Modularity

The codebase is organized into decoupled layers:

```
GuidedGuard/
├── preprocessing/         # Data adapters, schema enforcement, feature extractors
├── models/                # ML training, calibration, anomaly detection, risk fusion, prediction
├── explainability/        # SHAP, LIME, counterfactual search, narrative generation
├── dashboard/             # 13 Streamlit views, Plotly visualizations, UI design system
├── tests/                 # Full unit test suite for preprocessing, modeling, XAI, validation
├── outputs/reports/       # Audit tables, ROC/PR curves, experiment results, serialized metrics
└── docs/                  # Formal research and architectural documentation
```
