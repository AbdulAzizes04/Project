# GuidedGuard: Explainable AI for Scam-Guided Digital Payment Detection

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-red.svg)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-green.svg)](https://xgboost.readthedocs.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-orange.svg)](https://scikit-learn.org/)
[![XAI](https://img.shields.io/badge/XAI-SHAP%20%26%20LIME-purple.svg)](https://shap.readthedocs.io/)
[![Tests: 27 Passed](https://img.shields.io/badge/Tests-27%20Passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Final-Year B.Tech Artificial Intelligence & Data Science Capstone Project**  
> An explainable, behavioral risk assessment framework engineered to identify digital payment transactions exhibiting patterns consistent with **Authorised Push Payment (APP) scam-guided fraud**, operating strictly at pre-transaction authorization time with zero post-settlement data leakage.

---

## 📑 Table of Contents
1. [Project Overview & Problem Formulation](#-project-overview--problem-formulation)
2. [Key Innovations & Technical Architecture](#-key-innovations--technical-architecture)
3. [Leakage-Free Authorization Representation](#-leakage-free-authorization-representation)
4. [Dual-Engine Risk Scoring & 8-Signal Fusion](#-dual-engine-risk-scoring--8-signal-fusion)
5. [Contextual Intervention Framework](#-contextual-intervention-framework)
6. [Explainable AI (XAI) & Actionable Recourse](#-explainable-ai-xai--actionable-recourse)
7. [Scientific Benchmarks & Experimental Results](#-scientific-benchmarks--experimental-results)
8. [Dashboard Overview (13 Modular Views)](#-dashboard-overview-13-modular-views)
9. [Installation & Local Execution Guide](#-installation--local-execution-guide)
10. [Automated Test Suite](#-automated-test-suite)
11. [Viva Demonstration Guide](#-viva-demonstration-guide)
12. [Project Directory Structure](#-project-directory-structure)
13. [Academic Disclaimer](#-academic-disclaimer)

---

## 🛡️ Project Overview & Problem Formulation

In conventional payment fraud (such as account takeover or stolen credit cards), unauthorized intruders initiate transactions. Consequently, traditional fraud detection systems focus primarily on authentication signals (failed passwords, new device logins, IP discrepancies).

In **scam-guided / Authorised Push Payment (APP) fraud**, the paradigm is inverted:
- **Valid Credentials**: The legitimate account holder authenticates the transaction willingly using valid credentials and multi-factor biometric authentication.
- **Social Engineering**: The victim is manipulated through deceptive urgency, fear, or coercion (e.g., impersonation of police, tax authorities, or bank anti-fraud units, investment scams, or remote access takeover).
- **Authentication Failure**: Traditional credential checks and MFA offer zero protection because the authorized user voluntarily approves the payment.

**GuidedGuard** solves this challenge by evaluating the **behavioral and transactional characteristics** of the payment at authorization time, comparing the transfer against the user's historical baseline, transaction cadence, payee relationship, and multi-dimensional anomaly signals before funds leave the account.

---

## 🏗️ Key Innovations & Technical Architecture

```text
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
                      |  - PR-AUC Optimized (0.1205)  |         |  - Normalized Anomaly (0-100) |
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

## 🚫 Leakage-Free Authorization Representation

In historical academic implementations of PaySim, models achieved artificial **100% accuracy** due to severe post-transaction data leakage: `newbalanceOrig` unconditionally dropped to zero during fraud, and `balance_wipeout_orig = ((oldbalanceOrg > 500) & (newbalanceOrig == 0))` was an exact proxy for the target.

GuidedGuard eliminates all post-settlement features:
- **Strictly Prohibited**: `newbalanceOrig`, `newbalanceDest`, `balance_wipeout_orig`, `balance_error_orig`, `balance_diff_orig`.
- **Allowed Authorization Features**: 19 features including `amount`, `oldbalanceOrg`, `log_amount`, `amount_to_old_balance_ratio`, `hour_of_day`, `day_of_week`, `is_weekend`, `is_business_hours`, `is_late_night`, `amount_deviation`, `relative_amount`, `is_large_transaction`, `velocity_1h`, `velocity_6h`, `velocity_24h`, `recent_transaction_spike`, `is_merchant_dest`, and `interaction_amount_x_velocity`.

---

## ⚡ Dual-Engine Risk Scoring & 8-Signal Fusion

1. **Supervised Classifier (XGBoost)**: Trained on historical patterns, calibrated via Platt scaling (Sigmoid) to produce realistic posterior probabilities.
2. **Unsupervised Anomaly Detector (Isolation Forest)**: Trained strictly on legitimate payment patterns ($\mathcal{D}_{\text{legit}}$) to identify zero-day outliers.
3. **8-Signal Fusion Engine**:
   $$\text{Risk Score} = 0.35 S_{\text{ML}} + 0.20 S_{\text{Behav}} + 0.15 S_{\text{Anomaly}} + 0.10 S_{\text{Beneficiary}} + 0.08 S_{\text{Velocity}} + 0.05 S_{\text{Device}} + 0.04 S_{\text{Location}} + 0.03 S_{\text{Temporal}}$$

Risk tiers:
- **LOW** (0 – 30): Normal legitimate payment.
- **MEDIUM** (31 – 60): Minor deviation requiring in-app confirmation.
- **HIGH** (61 – 80): Significant deviation prompting phone verification.
- **CRITICAL** (81 – 100): Multi-vector convergence triggering cooling-off hold.

---

## 🚦 Contextual Intervention Framework

Instead of crude binary blocking, GuidedGuard introduces proportional friction:
- **LOW**: `APPROVE` — Transparent background clearance.
- **MEDIUM**: `STEP_UP_CHALLENGE` — Dynamic in-app prompt highlighting new beneficiary.
- **HIGH**: `FRICTION_CALLBACK` — 15-minute pause and scam awareness questionnaire.
- **CRITICAL**: `COOLING_OFF_HOLD` — 24-hour funds hold, outbound fraud analyst outreach, and push alerts.

---

## 💡 Explainable AI (XAI) & Actionable Recourse

- **SHAP (Shapley Additive exPlanations)**: TreeExplainer game-theoretic contributions, waterfall plots, and global summary curves.
- **LIME (Local Interpretable Model-agnostic Explanations)**: Local surrogate decision rules indicating feature thresholds.
- **Counterfactual Explanations**: Identifies minimal actionable changes (e.g., tranching transfer, transferring during business hours, verifying recipient) to reduce estimated risk.
- **Calibrated Natural Language Narratives**: Non-definitive banking security assessments (*"exhibits characteristics consistent with elevated scam risk"* rather than claiming absolute proof of fraud).

---

## 📊 Scientific Benchmarks & Experimental Results

### Model Benchmark (Leakage-Free Authorization Features on Out-of-Time Test Set)

| Model Architecture | PR-AUC | ROC-AUC | F1-Score | Precision | Recall | Brier Score | Latency |
|---|---|---|---|---|---|---|---|
| **XGBoost (Selected)** | **0.1205** | **0.6835** | **0.2474** | **0.3636** | **0.1875** | **0.0139** | **10.44 ms** |
| HistGradientBoosting | 0.1089 | 0.6789 | 0.0833 | 0.3750 | 0.0469 | 0.0121 | 12.49 ms |
| Random Forest | 0.1072 | 0.6531 | 0.2449 | 0.3529 | 0.1875 | 0.0412 | 36.03 ms |
| Logistic Regression | 0.1047 | 0.7241 | 0.0469 | 0.0243 | 0.6719 | 0.2081 | 1.32 ms |
| Decision Tree | 0.0995 | 0.6094 | 0.0501 | 0.0264 | 0.4844 | 0.1533 | 1.85 ms |
| Gradient Boosting (sklearn) | 0.0675 | 0.7047 | 0.0816 | 0.1176 | 0.0625 | 0.0161 | 16.05 ms |

### External Validation (NeurIPS 2022 Bank Account Fraud Suite)
- **PR-AUC**: **0.1747** (+60.4% lift over PaySim internal baseline)
- **ROC-AUC**: **0.5686**
- **Accuracy**: **86.82%**

---

## 🖥️ Dashboard Overview (13 Modular Views)

1. **🏠 Dashboard Overview**: System health, leakage status banner, KPI cards, and risk distribution gauges.
2. **💳 Payment Simulator**: Real-time transaction simulation with 8-signal breakdown, SHAP plots, and PDF export.
3. **🎭 Scam Scenarios (Viva Demos)**: 7 pre-configured real-world attack simulations (Impersonation, Investment, Romance, Rapid Velocity, etc.).
4. **⏱️ Transaction Timeline**: Visual chronological transaction trajectory and customer risk acceleration.
5. **🔍 Forensic Investigation**: Searchable case dossier with baseline comparison and PDF/JSON/CSV exports.
6. **💡 Explainable AI (XAI)**: Dedicated SHAP waterfall, summary, and LIME rule exploration gallery.
7. **📊 Benchmark & Analytics**: Benchmark comparisons, 12-experiment matrix, and ROC/PR diagnostic curves.
8. **📈 Model & Drift Monitoring**: Inference traffic tracking and Population Stability Index (PSI) drift monitoring.
9. **📁 Batch Prediction**: Bulk CSV upload, schema validation, and vectorized inference.
10. **🗄️ Datasets & Provenance**: PaySim vs. BAF dataset documentation and schema harmonization.
11. **📜 Prediction History & Audit**: Persistent audit trail with multi-parameter filtering and inspection.
12. **⚙️ System Settings**: Configurable risk threshold sliders and environment diagnostics.
13. **ℹ️ Documentation & About**: Architectural flows, research papers, and technical guides.

---

## 🚀 Installation & Local Execution Guide

### Prerequisites
- Python 3.11+
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/your-repo/guidedguard.git
cd guidedguard

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Automated Test Suite

GuidedGuard features a comprehensive unit test suite with 100% pass rate:

```bash
pytest tests/ -v
```

```text
tests/test_behavioral_profile.py::test_profiler_fit PASSED               [  3%]
tests/test_behavioral_profile.py::test_profiler_deviation_scoring_normal PASSED [  7%]
tests/test_behavioral_profile.py::test_profiler_deviation_scoring_anomaly PASSED [ 11%]
tests/test_behavioral_profile.py::test_profiler_cold_start PASSED        [ 14%]
tests/test_feature_engineering.py::test_feature_engineering_excludes_leakage PASSED [ 18%]
tests/test_feature_engineering.py::test_authorization_features_presence PASSED [ 22%]
tests/test_feature_engineering.py::test_filter_authorization_features PASSED [ 25%]
tests/test_prediction.py::test_predict_single_legitimate_transaction PASSED [ 29%]
tests/test_prediction.py::test_predict_single_scam_transaction PASSED    [ 33%]
tests/test_prediction.py::test_predict_batch_transactions PASSED         [ 37%]
tests/test_preprocessing.py::test_validate_dataset_schema_valid PASSED   [ 40%]
tests/test_preprocessing.py::test_validate_dataset_schema_missing_col PASSED [ 44%]
tests/test_preprocessing.py::test_clean_raw_dataset_handles_nulls_and_negatives PASSED [ 48%]
tests/test_preprocessing.py::test_preprocess_pipeline_end_to_end PASSED  [ 51%]
tests/test_risk_engine.py::test_risk_fusion_weights_sum_to_one PASSED    [ 55%]
tests/test_risk_engine.py::test_risk_fusion_low_risk_scenario PASSED     [ 59%]
tests/test_risk_engine.py::test_risk_fusion_critical_risk_scenario PASSED [ 62%]
tests/test_risk_engine.py::test_intervention_engine_low_risk PASSED      [ 66%]
tests/test_risk_engine.py::test_intervention_engine_critical_risk PASSED [ 70%]
tests/test_validation.py::test_temporal_split_chronological_ordering PASSED [ 74%]
tests/test_validation.py::test_leakage_auditor_detects_post_transaction_features PASSED [ 77%]
tests/test_validation.py::test_evaluation_metrics_computation PASSED     [ 81%]
tests/test_validation.py::test_precision_recall_at_k PASSED              [ 85%]
tests/test_xai.py::test_shap_explanation_structure PASSED                [ 88%]
tests/test_xai.py::test_human_readable_summary PASSED                    [ 92%]
tests/test_xai.py::test_counterfactual_engine PASSED                     [ 96%]
tests/test_xai.py::test_security_narrative_engine PASSED                 [100%]

============================= 27 passed in 7.62s ==============================
```

---

## 🎓 Viva Demonstration Guide

When presenting to examiners:
1. **Explain the APP Fraud Differentiation**: Explain why conventional authentication-based fraud models fail when victims willingly approve transfers.
2. **Demonstrate Data Leakage Removal**: Open `docs/leakage_audit.md` and explain why previous 100% accuracy claims were invalid due to `newbalanceOrig == 0`.
3. **Run Scenario 1 (Routine Payment)** in **🎭 Scam Scenarios**: Show that normal amounts to known merchants result in `LOW RISK` and `APPROVE`.
4. **Run Scenario 2 (Urgent Impersonation Transfer)**: Show how a $92,000 transfer to a novel payee triggers `CRITICAL RISK` (85+), SHAP red bars for amount ratio and payee novelty, and a 24-hour cooling-off hold.
5. **Showcase Actionable Recourse**: Scroll to the Counterfactual Recourse section in the Simulator or XAI Portal to demonstrate how the user could safely tranche payments or verify recipients.
6. **Show External Validation**: Present the NeurIPS 2022 Bank Account Fraud (BAF) suite results in **📊 Benchmark & Analytics**.

---

## 📂 Project Directory Structure

```text
GuidedGuard/
│
├── assets/
│   └── style.css                      # Custom dark theme CSS stylesheet
│
├── config.py                          # Global configuration settings & thresholds
├── app.py                             # Main Streamlit application entry point (13 views)
├── requirements.txt                   # Production Python dependencies
├── README.md                          # Project documentation and setup guide
│
├── data/
│   ├── raw/                           # Raw datasets (PaySim & BAF)
│   └── processed/                     # Cleaned & engineered feature CSVs
│
├── dashboard/
│   ├── __init__.py                    # View router exports
│   ├── components.py                  # Shared UI components & Plotly charts
│   ├── overview.py                    # Overview view with honest metrics
│   ├── simulator.py                   # Single transaction payment simulator
│   ├── scenario_simulator.py          # 7 pre-configured viva demo scenarios
│   ├── timeline.py                    # Visual transaction timeline view
│   ├── investigation.py               # Forensic investigation case dossier
│   ├── xai.py                         # Dedicated SHAP & LIME XAI portal
│   ├── analytics.py                   # Benchmark & 12-experiment matrix view
│   ├── model_monitoring.py            # Inference & PSI drift monitor
│   ├── batch_prediction.py            # Bulk CSV batch prediction view
│   ├── datasets.py                    # Dataset provenance & schema matrix
│   ├── history.py                     # Prediction audit trail view
│   ├── settings.py                    # System configuration & thresholds
│   └── about.py                       # Project architecture & documentation
│
├── docs/
│   ├── architecture.md                # System design & boundaries
│   ├── methodology.md                 # Research & modeling formulation
│   ├── feature_engineering.md         # 19 authorization features dictionary
│   ├── model_evaluation.md            # Benchmark & 12 experiments
│   ├── xai.md                         # SHAP, LIME, counterfactuals, narratives
│   ├── leakage_audit.md               # Forensic leakage investigation
│   ├── temporal_validation.md         # Chronological splitting methodology
│   ├── external_validation.md         # BAF NeurIPS benchmark evaluation
│   └── limitations.md                 # Academic boundaries & roadmap
│
├── explainability/
│   ├── __init__.py
│   ├── shap_explainer.py              # SHAP TreeExplainer & waterfall routines
│   ├── lime_explainer.py              # LIME Tabular surrogate engine
│   ├── counterfactual.py              # Minimal actionable recourse engine
│   └── narrative_engine.py            # Calibrated banking security narratives
│
├── models/
│   ├── __init__.py
│   ├── model_loader.py                # Safe multi-artifact loader
│   ├── predict.py                     # Real-time inference & batch orchestration
│   ├── train_model.py                 # 12-experiment training & benchmarking
│   ├── leakage_audit.py               # 4-stage data leakage auditor
│   ├── temporal_validation.py         # Chronological train/val/test splitter
│   ├── evaluation.py                  # Imbalance metrics & plot generator
│   ├── calibration.py                 # Platt sigmoid probability calibration
│   ├── anomaly_detector.py            # Isolation Forest behavioral outlier engine
│   ├── risk_engine.py                 # 8-signal multi-modal risk fusion engine
│   ├── intervention_engine.py         # 4-tier contextual intervention policy
│   ├── cost_analysis.py               # Asymmetric FP vs FN cost optimization
│   ├── external_validation.py         # BAF cross-dataset benchmark evaluation
│   ├── saved_model.pkl                # Trained Calibrated XGBoost classifier
│   ├── scaler.pkl                     # Fitted StandardScaler
│   ├── anomaly_detector.pkl           # Fitted Isolation Forest
│   └── model_metadata.json            # Model evaluation & hyperparameter metadata
│
├── preprocessing/
│   ├── __init__.py
│   ├── preprocessing.py               # Validation, cleaning, scaling pipeline
│   ├── feature_engineering.py         # 19 clean authorization-time features
│   ├── authorization_features.py      # Schema boundary enforcement
│   ├── behavioral_profile.py          # User baseline profiling & deviations
│   ├── velocity_features.py           # Rolling window velocity extractors
│   ├── beneficiary_features.py        # Payee tenure & novelty scoring
│   ├── device_features.py             # Client device trust proxies
│   ├── location_features.py           # Regional location discrepancy proxies
│   ├── temporal_features.py           # Hour, day, and habituation windows
│   └── dataset_adapter.py             # PaySim & BAF schema harmonizers
│
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py          # Preprocessing & schema validation tests
│   ├── test_feature_engineering.py    # Authorization feature & leakage tests
│   ├── test_behavioral_profile.py     # Behavioral baselines & deviation tests
│   ├── test_risk_engine.py            # Fusion engine & intervention tests
│   ├── test_prediction.py             # Inference pipeline & batch tests
│   ├── test_xai.py                    # SHAP, LIME, counterfactual & narrative tests
│   └── test_validation.py            # Temporal split & leakage audit tests
│
├── outputs/
│   └── reports/                       # Generated audit tables, curves, and reports
│       ├── leakage_audit.json
│       ├── leakage_audit.csv
│       ├── model_comparison.json
│       ├── model_comparison.csv
│       ├── experiment_results.csv
│       ├── confusion_matrix.png
│       ├── roc_curve.png
│       ├── precision_recall_curve.png
│       └── calibration_curve.png
│
└── utils/
    ├── __init__.py
    ├── data_loader.py                 # Dataset loading helpers
    ├── helpers.py                     # Logger, formatting, and platform helpers
    └── pdf_generator.py               # Forensic dossier PDF report builder
```

---

## ⚠️ Academic Disclaimer

GuidedGuard is an academic research capstone project developed strictly for educational and scientific demonstration purposes. It does not connect to real-world banking infrastructure, payment gateways, or live financial rails. All simulated intervention policies (holds, warnings, delays) are illustrative models designed to explore human-centric friction in Authorised Push Payment fraud defense.
