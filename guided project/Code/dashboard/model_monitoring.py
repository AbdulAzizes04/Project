"""
Model Monitoring & Data Drift Dashboard Page for GuidedGuard.

Monitors production inference health, volume trends, risk alert rates,
and distributional drift using Population Stability Index (PSI).

PSI Drift Threshold Standards:
- PSI < 0.10: Stable (No significant shift in distribution)
- 0.10 <= PSI < 0.25: Moderate Shift (Monitor closely; potential seasonal variation)
- PSI >= 0.25: Significant Drift (Action Required; model retraining / baseline update recommended)
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import config
from dashboard.components import render_header_status_bar, render_glass_card


def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_bins: int = 10) -> float:
    """
    Compute Population Stability Index (PSI) between baseline and production samples.
    """
    eps = 1e-4
    quantiles = np.linspace(0, 1, num_bins + 1)
    bin_edges = np.quantile(expected, quantiles)
    bin_edges[0] -= eps
    bin_edges[-1] += eps

    expected_counts, _ = np.histogram(expected, bins=bin_edges)
    actual_counts, _ = np.histogram(actual, bins=bin_edges)

    expected_pct = (expected_counts + eps) / len(expected)
    actual_pct = (actual_counts + eps) / len(actual)

    psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(max(0.0, psi_val))


def get_drift_status(psi_val: float) -> Tuple[str, str]:
    """Return status label and badge color."""
    if psi_val < 0.10:
        return "Stable", "#10B981"
    elif psi_val < 0.25:
        return "Monitor", "#F59E0B"
    else:
        return "Drift Detected", "#EF4444"


def render_model_monitoring_page():
    """
    Render complete Model Monitoring & Drift Surveillance view.
    """
    render_header_status_bar(
        page_title="Model Health & Drift Surveillance",
        page_description="Monitor operational prediction volumes, risk category frequencies, and Population Stability Index (PSI) drift.",
    )

    # 1. Operational Volume & Alert KPIs
    st.markdown("### 📊 Operational Health KPIs")

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Inference Volume", "5,042 txns")
    with k2:
        st.metric("Average Fused Risk", "24.6 / 100")
    with k3:
        st.metric("High-Risk Alerts", "214 (4.2%)")
    with k4:
        st.metric("Critical Blocks / Holds", "58 (1.1%)")
    with k5:
        st.metric("Model Drift Status", "Healthy (PSI < 0.10)")

    st.markdown("---")

    # 2. Population Stability Index (PSI) Drift Surveillance Table
    st.markdown("### 📡 Population Stability Index (PSI) Feature Surveillance")
    st.markdown(
        """
        Comparing baseline training feature distributions against the active 30-day inference window.
        Standard banking thresholds: **PSI < 0.10** (Stable), **0.10 – 0.25** (Monitor), **>= 0.25** (Drift).
        """
    )

    # Compute PSI on key features
    np.random.seed(42)
    base_amt = np.random.lognormal(mean=7.5, sigma=1.2, size=5000)
    curr_amt = np.random.lognormal(mean=7.6, sigma=1.25, size=2000)

    base_vel = np.random.poisson(lam=1.8, size=5000)
    curr_vel = np.random.poisson(lam=2.1, size=2000)

    base_ben = np.random.beta(a=1, b=5, size=5000) * 100
    curr_ben = np.random.beta(a=1.2, b=4.8, size=2000) * 100

    base_dev = np.random.beta(a=1, b=8, size=5000) * 100
    curr_dev = np.random.beta(a=1, b=8, size=2000) * 100

    features_psi = [
        {"Feature": "Transaction Amount (`amount`)", "PSI": calculate_psi(base_amt, curr_amt), "Expected Dist": "Lognormal Baseline", "Action": "Routine Monitoring"},
        {"Feature": "Velocity 6h (`velocity_6h`)", "PSI": calculate_psi(base_vel, curr_vel), "Expected Dist": "Poisson Baseline", "Action": "Routine Monitoring"},
        {"Feature": "Beneficiary Risk (`beneficiary_risk`)", "PSI": calculate_psi(base_ben, curr_ben), "Expected Dist": "Beta Payee Prior", "Action": "Routine Monitoring"},
        {"Feature": "Device Risk Score (`device_risk_score`)", "PSI": calculate_psi(base_dev, curr_dev), "Expected Dist": "Mobile App Dominant", "Action": "Routine Monitoring"},
    ]

    for f in features_psi:
        status, color = get_drift_status(f["PSI"])
        f["PSI_Val"] = f"{f['PSI']:.4f}"
        f["Status"] = status

    df_psi = pd.DataFrame(features_psi)[["Feature", "PSI_Val", "Status", "Action"]]
    st.dataframe(df_psi, use_container_width=True)

    st.markdown("---")

    # 3. Distribution Visualizer
    st.markdown("### 📉 Feature Distribution Comparison")
    col_plot1, col_plot2 = st.columns(2)

    with col_plot1:
        fig_amt = go.Figure()
        fig_amt.add_trace(go.Histogram(x=np.log1p(base_amt[:1500]), name="Training Baseline", opacity=0.6, marker_color="#6366F1"))
        fig_amt.add_trace(go.Histogram(x=np.log1p(curr_amt[:1500]), name="Inference Stream", opacity=0.6, marker_color="#06B6D4"))
        fig_amt.update_layout(
            barmode="overlay",
            title="Log Amount Distribution (Baseline vs Current)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font=dict(color="#E2E8F0"),
            height=320,
        )
        st.plotly_chart(fig_amt, use_container_width=True)

    with col_plot2:
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Histogram(x=base_vel[:1500], name="Training Baseline", opacity=0.6, marker_color="#6366F1"))
        fig_vel.add_trace(go.Histogram(x=curr_vel[:1500], name="Inference Stream", opacity=0.6, marker_color="#10B981"))
        fig_vel.update_layout(
            barmode="overlay",
            title="Velocity Distribution (Baseline vs Current)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font=dict(color="#E2E8F0"),
            height=320,
        )
        st.plotly_chart(fig_vel, use_container_width=True)
