"""
About Project & Documentation Portal Page for GuidedGuard.

This module renders the comprehensive About Project & Interactive Documentation Portal for GuidedGuard,
covering hero branding, problem statements, solution architecture flow diagrams, end-to-end workflow timelines,
technology stack cards, dataset summaries, machine learning pipeline documentation, Explainable AI concepts (SHAP & LIME),
application module breakdowns, project folder tree, user guide instructions, future enhancements, and credits.

Responsibility:
- Interactive system documentation portal presentation.
- Solution architecture flow diagram rendering.
- Workflow timeline & technology stack cards.
- User guide instructions & future roadmap.
"""

import sys
import platform
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import streamlit as st

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from dashboard.components import render_header_status_bar, render_glass_card, render_timeline_steps


def render_about_page():
    """
    Render complete 14-section About Project & Interactive Documentation Portal view.
    """
    # 1. Hero Header Banner
    render_header_status_bar(
        page_title=f"{config.PROJECT_NAME} – Interactive Documentation Portal",
        page_description="System architecture, machine learning pipeline, Explainable AI framework, and user guide documentation.",
    )

    # ==========================================
    # SECTION 1: HERO BANNER
    # ==========================================
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 14px; padding: 2rem; text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #6366F1; margin-bottom: 0.5rem; font-size: 2.5rem;">🛡️ {config.PROJECT_NAME}</h1>
            <h4 style="color: #38BDF8; margin-top: 0; font-weight: 500;">Explainable AI for Scam-Guided Digital Payment Detection</h4>
            <p style="color: #94A3B8; max-width: 800px; margin: 1rem auto; font-size: 1rem;">
                An end-to-end, production-ready Explainable AI (XAI) application built to detect social-engineering scam-guided digital payment transactions using Gradient Boosting machine learning models, providing transparent SHAP & LIME local attributions and human-understandable English explanation narratives.
            </p>
            <span class="status-badge status-badge-low">VERSION {config.VERSION}</span> &nbsp;
            <span class="status-badge status-badge-medium">PYTHON 3.11</span> &nbsp;
            <span class="status-badge status-badge-low">SHAP & LIME ACTIVE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================================
    # SECTION 2: PROJECT OVERVIEW
    # ==========================================
    st.markdown("### 📘 2. Project Overview")
    ov_c1, ov_c2 = st.columns(2)

    with ov_c1:
        render_glass_card(
            title="🎯 Primary Objectives",
            content_markdown="""
            - **Scam-Guided APP Fraud Detection**: Identify Authorised Push Payment (APP) fraud patterns at authorization time without post-transaction balance leakage.
            - **Dual ML & Behavioral Anomaly Engine**: Calibrated supervised learning (XGBoost) combined with unsupervised Isolation Forest for novel zero-day anomalies.
            - **8-Signal Risk Fusion**: Blend Supervised, Behavioral, Anomaly, Beneficiary, Velocity, Device, Location, and Temporal risk signals into a composite score (0-100).
            - **Transparent Interpretability**: Provide SHAP waterfall attributions, LIME local rules, counterfactual recourse scenarios, and natural English risk narratives.
            """,
        )

    with ov_c2:
        render_glass_card(
            title="✨ Key Features & Capabilities",
            content_markdown="""
            - **Interactive Payment Simulator**: Real-time transaction simulation with instant fraud predictions (<45ms).
            - **Batch CSV Inference Engine**: Automated bulk transaction fraud detection and risk reporting.
            - **Dedicated XAI Portal**: Interactive global & local SHAP/LIME visualization gallery and feature search explorer.
            - **Audit Trail & History**: Centralized transaction audit logs with multi-parameter search, filtering, and JSON/CSV export.
            """,
        )

    st.markdown("---")

    # ==========================================
    # SECTION 3: PROBLEM STATEMENT
    # ==========================================
    st.markdown("### ⚠️ 3. Problem Statement & Background")
    p_c1, p_c2 = st.columns(2)

    with p_c1:
        render_glass_card(
            title="🚨 The Rise of Scam-Guided Fraud",
            content_markdown="""
            Digital payment platforms (UPI, peer-to-peer transfers, online banking) have witnessed a massive surge in **scam-guided authorized push payment (APP) fraud**.
            
            Unlike traditional stolen-credential fraud, victims are manipulated via social engineering (impersonation, lottery scams, urgent bank alerts) into voluntarily authorizing high-value transfers.
            """,
        )

    with p_c2:
        render_glass_card(
            title="💡 Why Explainable AI (XAI) is Mandatory",
            content_markdown="""
            - **Limitations of Legacy Rules**: Static rule engines fail to capture subtle behavioral anomalies like velocity spikes or account wipeouts.
            - **Black-Box Opacity**: Standard Machine Learning models output raw probability numbers without explaining *why* a transaction was flagged.
            - **Regulatory & User Trust**: Regulators and fraud analysts require transparent, interpretable rationales before blocking customer funds.
            """,
        )

    st.markdown("---")

    # ==========================================
    # SECTION 4: SOLUTION ARCHITECTURE FLOW
    # ==========================================
    st.markdown("### 🏗️ 4. Solution Architecture Flow")

    st.markdown(
        """
        ```
        +--------------------------------------------------------------------------------+
        |                          INPUT TRANSACTION EVENT                               |
        |              Amount, Type, Prior Balance, Customer, Beneficiary               |
        +--------------------------------------------------------------------------------+
                                               |
                                               v
        +--------------------------------------------------------------------------------+
        |                  PRE-TRANSACTION AUTHORIZATION PIPELINE                        |
        |  - Temporal Windows       - Behavioral Baselines     - Velocity Trackers       |
        |  - Beneficiary Scoring    - Device & Location Proxies- Zero Post-Txn Leakage   |
        +--------------------------------------------------------------------------------+
                                               |
                        +----------------------+----------------------+
                        |                                             |
                        v                                             v
        +-------------------------------+             +-------------------------------+
        |  SUPERVISED ML ENGINE         |             |  UNSUPERVISED ANOMALY ENGINE  |
        |  - Calibrated XGBoost         |             |  - Isolation Forest           |
        |  - PR-AUC Optimized           |             |  - Normalized Anomaly Score   |
        +-------------------------------+             +-------------------------------+
                        |                                             |
                        +----------------------+----------------------+
                                               |
                                               v
        +--------------------------------------------------------------------------------+
        |                     8-SIGNAL MULTI-MODAL RISK FUSION ENGINE                    |
        | Supervised (35%) + Behavioral (20%) + Anomaly (15%) + Beneficiary (10%) +     |
        | Velocity (8%) + Device (5%) + Location (4%) + Temporal (3%) -> Score (0-100)   |
        +--------------------------------------------------------------------------------+
                                               |
                        +----------------------+----------------------+
                        |                                             |
                        v                                             v
        +-------------------------------+             +-------------------------------+
        |  EXPLAINABILITY & RECOURSE    |             |  INTERVENTION POLICIES        |
        |  - SHAP Waterfall & LIME      |             |  - Low: Approve               |
        |  - Minimal Counterfactuals    |             |  - Med: Biometric / Warning   |
        |  - Natural Security Narrative |             |  - High: 24h Cooling Hold     |
        +-------------------------------+             +-------------------------------+
        ```
        """
    )

    st.markdown("---")

    # ==========================================
    # SECTION 5: END-TO-END WORKFLOW TIMELINE
    # ==========================================
    st.markdown("### ⏱️ 5. End-to-End Execution Workflow")
    render_timeline_steps(current_step=6)

    st.markdown("---")

    # ==========================================
    # SECTION 6: TECHNOLOGY STACK CARDS
    # ==========================================
    st.markdown("### 🛠️ 6. Technology Stack")
    t1, t2, t3, t4 = st.columns(4)

    with t1:
        render_glass_card(
            title="🐍 Core & Runtime",
            content_markdown="""
            - **Python**: 3.11
            - **Streamlit**: Web Application UI
            - **Joblib**: Model Artifact Serialization
            """,
        )

    with t2:
        render_glass_card(
            title="🤖 Machine Learning",
            content_markdown="""
            - **Scikit-Learn**: Scalers & Baseline Models
            - **Gradient Boosting**: Top Classifier
            - **HistGradientBoosting**: Candidate Model
            """,
        )

    with t3:
        render_glass_card(
            title="💡 Explainable AI",
            content_markdown="""
            - **SHAP**: TreeExplainer & Waterfall Plots
            - **LIME**: Tabular Linear Surrogate Rules
            - **Natural English Generator**: Text Summaries
            """,
        )

    with t4:
        render_glass_card(
            title="📊 Data & Visuals",
            content_markdown="""
            - **Pandas & NumPy**: Data Matrices
            - **Plotly**: Gauge, Donut & Radar Charts
            - **Matplotlib**: XAI Figure Exports
            """,
        )

    st.markdown("---")

    # ==========================================
    # SECTION 7: DATASET INFORMATION
    # ==========================================
    st.markdown("### 📁 7. Primary Datasets Overview")
    d_c1, d_c2 = st.columns(2)

    with d_c1:
        render_glass_card(
            title="PaySim Synthetic Financial Dataset",
            content_markdown="""
            - **Records Count**: 25,000 transaction samples
            - **Engineered Columns**: 56 domain feature columns
            - **Fraud Imbalance**: ~1.20% positive scam transactions
            - **Primary Target**: `isFraud` (0 = Legitimate, 1 = Fraud)
            """,
        )

    with d_c2:
        render_glass_card(
            title="Bank Account Fraud (BAF) Dataset",
            content_markdown="""
            - **Records Count**: 20,000 base samples
            - **Engineered Columns**: 70 domain feature columns
            - **Fraud Imbalance**: ~1.20% positive scam transactions
            - **Primary Target**: `fraud_bool` (0 = Legitimate, 1 = Fraud)
            """,
        )

    st.markdown("---")

    # ==========================================
    # SECTION 8 & 9: ML PIPELINE & XAI CONCEPTS
    # ==========================================
    st.markdown("### 🧠 8. Machine Learning & Explainable AI Pipeline")

    tab_ml, tab_xai = st.tabs(["🤖 Machine Learning Pipeline", "💡 Explainable AI Framework"])

    with tab_ml:
        st.markdown(
            """
            1. **Dataset Collection**: Automated dataset loading and metadata validation.
            2. **Exploratory Data Analysis (EDA)**: Target distribution analysis, outlier inspection, correlation heatmaps.
            3. **Data Preprocessing**: Imputation, duplicate handling, dtype optimization, `StandardScaler` scaling.
            4. **Feature Engineering**: 10 domain categories (Velocity, Balance Wipeouts, Device Risk, Temporal Windows).
            5. **Model Training & Selection**: Trained 7 classifiers (Gradient Boosting, HistGradientBoosting, Random Forest, Logistic Regression, etc.).
            6. **Serialization**: Saved top model (`saved_model.pkl`), scaler (`scaler.pkl`), and metadata (`model_metadata.json`).
            """
        )

    with tab_xai:
        st.markdown(
            """
            - **SHAP (SHapley Additive exPlanations)**: Calculates Shapley game-theoretic contributions for each feature, establishing fair global importance rankings and local waterfall attributions.
            - **LIME (Local Interpretable Model-agnostic Explanations)**: Builds a local linear surrogate model around a single prediction instance, extracting decision rule boundaries (e.g. `'amount > $10,000'`).
            - **Human-Readable Text Summaries**: Translates numerical SHAP/LIME weights into actionable English sentences (e.g. *'Origin account balance wipeout increased scam risk score'*).
            """
        )

    st.markdown("---")

    # ==========================================
    # SECTION 10 & 11: APPLICATION MODULES & FOLDER TREE
    # ==========================================
    st.markdown("### 📂 9. Project Directory Structure & Application Modules")

    with st.expander("📁 View Complete GuidedGuard Folder Structure Tree", expanded=False):
        st.code(
            """
GuidedGuard/
│
├── assets/
│   └── style.css                      # Custom dark theme CSS stylesheet
│
├── config.py                          # Global configuration settings & thresholds
├── app.py                             # Main Streamlit application entry point & router
│
├── data/
│   ├── raw/                           # Raw input CSV datasets
│   └── processed/                     # Preprocessed & engineered feature CSVs
│
├── dashboard/
│   ├── __init__.py
│   ├── components.py                  # Shared UI components & Plotly charts
│   ├── overview.py                    # Dashboard Overview page
│   ├── simulator.py                   # Payment Transaction Simulator page
│   ├── history.py                     # Prediction History & Audit Log page
│   ├── xai.py                         # Dedicated Explainable AI Portal page
│   ├── analytics.py                   # Executive Fraud Analytics page
│   ├── batch_prediction.py            # Batch CSV Prediction page
│   ├── settings.py                    # System Settings page
│   └── about.py                       # About Project & Documentation Portal
│
├── explainability/
│   ├── __init__.py
│   ├── shap_explainer.py              # SHAP TreeExplainer & plot routines
│   └── lime_explainer.py              # LIME Tabular Explainer & rule plot routines
│
├── models/
│   ├── __init__.py
│   ├── model_loader.py                # Artifact loader & validator
│   ├── predict.py                     # Prediction & batch inference engine
│   ├── train_model.py                 # MLOps model training & tuning library
│   ├── saved_model.pkl                # Serialized trained classifier artifact
│   ├── scaler.pkl                     # Serialized StandardScaler artifact
│   └── model_metadata.json            # Model evaluation & hyperparameter metadata
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 05_xai_analysis.ipynb
│
├── outputs/
│   └── reports/                       # Exported CSV, PNG, JSON reports & XAI plots
│
├── preprocessing/
│   ├── __init__.py
│   ├── preprocessing.py               # Preprocessing pipeline library
│   └── feature_engineering.py         # 10 domain feature engineering pipeline
│
└── utils/
    ├── __init__.py
    ├── data_loader.py                 # Dataset I/O helper
    ├── helpers.py                     # Logger & environment helpers
    └── risk_score.py                  # Normalized risk score & level engine
            """,
            language="text",
        )

    st.markdown("---")

    # ==========================================
    # SECTION 12: USER GUIDE
    # ==========================================
    st.markdown("### 📖 10. Application User Guide")
    g1, g2, g3 = st.columns(3)

    with g1:
        render_glass_card(
            title="1. Payment Simulation",
            content_markdown="""
            - Navigate to **💳 Payment Simulator**.
            - Select a preset (e.g. *Account Wipeout Scam*) or input transaction fields.
            - Click **⚡ Analyze Payment Transaction** to view risk scores, SHAP/LIME plots, and English narratives.
            """,
        )

    with g2:
        render_glass_card(
            title="2. Batch CSV Inference",
            content_markdown="""
            - Navigate to **📁 Batch Prediction**.
            - Drag and drop your transaction CSV file.
            - Click **⚡ Run Batch Fraud Analysis** to process bulk predictions and download output reports.
            """,
        )

    with g3:
        render_glass_card(
            title="3. XAI & Audit Log",
            content_markdown="""
            - Navigate to **💡 Explainable AI** to explore SHAP global rankings and local waterfall plots.
            - Navigate to **📜 Prediction History** to search, filter, inspect, and export audit logs.
            """,
        )

    st.markdown("---")

    # ==========================================
    # SECTION 13 & 14: FUTURE ROADMAP & CREDITS
    # ==========================================
    st.markdown("### 🚀 11. Future Roadmap & Developer Credits")
    f_c1, f_c2 = st.columns(2)

    with f_c1:
        render_glass_card(
            title="🌟 Future Roadmap Enhancements",
            content_markdown="""
            - **Real Banking API Integration**: REST API endpoints for real-time payment gateway webhooks.
            - **Live Streaming Fraud Monitoring**: Kafka / Event-driven streaming inference pipelines.
            - **Deep Learning Sequence Models**: Recurrent Neural Networks (RNNs) for sequential behavioral patterns.
            - **Cloud Deployment**: One-click containerized deployment on AWS / GCP / Azure.
            """,
        )

    with f_c2:
        render_glass_card(
            title="👨‍💻 Credits & License",
            content_markdown=f"""
            - **Lead Developer**: GuidedGuard AI Lab
            - **Project Version**: {config.VERSION}
            - **Open Source Stack**: Python 3.11, Streamlit, Scikit-Learn, SHAP, LIME, Plotly
            - **Dataset Credits**: PaySim Synthetic Financial Dataset & BAF Project
            - **License**: MIT License – Open Educational & Research Use
            """,
        )
