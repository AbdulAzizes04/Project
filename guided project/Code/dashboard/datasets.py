"""
Dataset Information & Provenance Documentation Page for GuidedGuard.

Presents rigorous metadata, provenance, class imbalance, and scientific limitations
for datasets evaluated within the GuidedGuard research framework:
1. PaySim Mobile Money Simulator (Synthetic financial transaction benchmark)
2. Bank Account Fraud - BAF (Real-world European bank account opening benchmark, NeurIPS 2022)

DATA SCIENCE ETHICS & PROVENANCE POLICY:
Scientific integrity demands complete transparency regarding data origins.
PaySim is strictly declared as a SYNTHETIC agent-based simulation.
BAF is declared as an external real-world benchmark used exclusively for transferability testing.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

import config
from dashboard.components import render_header_status_bar, render_glass_card


def render_datasets_page():
    """
    Render complete Dataset Information and Provenance view.
    """
    render_header_status_bar(
        page_title="Dataset Provenance & Benchmark Validation",
        page_description="Transparent documentation of training datasets, synthetic vs real-world provenance, and experimental boundaries.",
    )

    # 1. Overview Summary Cards
    st.markdown("### 🗄️ Evaluated Datasets Overview")
    d_col1, d_col2 = st.columns(2)

    with d_col1:
        render_glass_card(
            title="📱 PaySim Mobile Money Simulator",
            content_markdown="""
            - **Status**: **SYNTHETIC DATASET** (Agent-Based Simulation)
            - **Total Records in Benchmark**: 25,000 transactions (sample subset)
            - **Class Distribution**: 24,698 Legitimate (98.79%) vs 302 Fraud (1.21%)
            - **Simulation Engine**: Developed by NTNU (Lopez-Rojas et al.) using real anonymized financial aggregates
            - **Available Features**: Step, Type, Amount, Sender ID, Receiver ID, Balances
            - **Severe Limitation**: Post-transaction balances (`newbalanceOrig`, `newbalanceDest`) induce 100% data leakage if unhandled.
            - **Role in Project**: Primary behavioural & transaction-time feature engineering evaluation.
            """,
        )

    with d_col2:
        render_glass_card(
            title="🏦 Bank Account Fraud (BAF) Benchmark",
            content_markdown="""
            - **Status**: **REAL-WORLD BENCHMARK** (NeurIPS 2022 Suite)
            - **Total Records Evaluated**: 20,000 application instances
            - **Class Distribution**: 17,443 Legitimate (87.22%) vs 2,557 Fraud (12.78%)
            - **Data Origin**: Major European financial institution (anonymized tabular release)
            - **Available Features**: Velocity (6h, 24h, 4w), Credit limits, Income, Device count, Age
            - **Domain Boundary**: Focuses on account opening / synthetic identity fraud.
            - **Role in Project**: External generalization benchmark testing feature adapter transferability.
            """,
        )

    st.markdown("---")

    # 2. Detailed Schema & Feature Availability Comparison Table
    st.markdown("### 📊 Feature Availability & Engineering Status")

    feature_matrix = [
        {"Domain Signal": "Transaction Amount", "PaySim Availability": "✅ Native (`amount`)", "BAF Availability": "🔄 Mapped (`proposed_credit_limit`)", "Project Classification": "TRANSACTION_TIME"},
        {"Domain Signal": "Transaction Velocity", "PaySim Availability": "⚙️ Derived (Rolling Steps)", "BAF Availability": "✅ Native (`velocity_6h`, `24h`)", "Project Classification": "TRANSACTION_TIME / VELOCITY"},
        {"Domain Signal": "Temporal Context", "PaySim Availability": "⚙️ Step-derived (`hour`, `day`)", "BAF Availability": "✅ Native (`month`)", "Project Classification": "TRANSACTION_TIME / TEMPORAL"},
        {"Domain Signal": "Customer Baseline", "PaySim Availability": "⚙️ Computed per `nameOrig`", "BAF Availability": "⚠️ Unavailable (Cross-sectional)", "Project Classification": "PRE_TRANSACTION"},
        {"Domain Signal": "Beneficiary Tenure", "PaySim Availability": "⚙️ Computed per `nameDest`", "BAF Availability": "❌ Not applicable", "Project Classification": "PRE_TRANSACTION"},
        {"Domain Signal": "Client Device Signature", "PaySim Availability": "🏷️ Explicitly Simulated (Prototype)", "BAF Availability": "✅ Native (`device_fraud_count`)", "Project Classification": "SIMULATED / DEMO"},
        {"Domain Signal": "Location Anomaly", "PaySim Availability": "🏷️ Explicitly Simulated (Prototype)", "BAF Availability": "✅ Zip code counts (`zip_count_4w`)", "Project Classification": "SIMULATED / DEMO"},
        {"Domain Signal": "Post-Settlement Balances", "PaySim Availability": "⚠️ Present (`newbalanceOrig`) — REMOVED", "BAF Availability": "✅ Absent", "Project Classification": "LEAKAGE (STRICTLY EXCLUDED)"},
    ]

    st.dataframe(pd.DataFrame(feature_matrix), use_container_width=True)

    st.markdown("---")

    # 3. Scientific Integrity & Claims Policy Banner
    st.markdown("### ⚖️ Academic Research Boundaries")
    st.info(
        """
        **Official Claims Policy for B.Tech Viva & Academic Assessment**:
        1. **No Claims of Social Engineering Proof**: GuidedGuard identifies statistical behavioural deviations consistent with scam transactions. It cannot definitively confirm user state-of-mind.
        2. **Explicit Labeling of Synthetic Inputs**: Device types and regional location tags in the Payment Simulator are explicitly marked as prototype demonstration inputs.
        3. **Honest Metric Reporting**: We report genuine, leakage-free validation metrics (PR-AUC: 0.092, Precision@50: 24.0%), rather than deceptive 100% scores caused by post-transaction balance leakage.
        """
    )
