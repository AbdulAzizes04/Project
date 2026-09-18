"""
Explainable AI (XAI) Portal Page for GuidedGuard.

This module renders the dedicated Explainable AI (XAI) Portal, displaying global and local
SHAP (SHapley Additive exPlanations) & LIME (Local Interpretable Model-agnostic Explanations)
visual galleries, interactive feature contribution search/filter tables, human-readable English
explanation narratives, model metadata metrics, and artifact download handlers.

Responsibility:
- Present global feature attributions & local transaction waterfall plots.
- Present local LIME decision surrogate rules.
- Interactive search and directional feature filtering.
- Render human-readable natural language narrative text cards.
- Export XAI CSV attributions, PNG plots, and text summary reports.
"""

import sys
import json
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from models.model_loader import load_metadata, validate_artifacts
from explainability.shap_explainer import generate_human_readable_summary
from dashboard.components import render_header_status_bar, render_glass_card, render_risk_badge


def render_xai_page():
    """
    Render complete 9-section Explainable AI Portal view.
    """
    # 1. Top Navigation Header Status Bar
    render_header_status_bar(
        page_title="Explainable AI (XAI) Portal",
        page_description="Global and local model interpretability dashboard powered by SHAP & LIME.",
    )

    metadata = load_metadata()
    art_status = validate_artifacts()

    # Paths to XAI report artifacts
    xai_dir = config.OUTPUTS_DIR / "reports" / "xai"
    shap_summary_png = xai_dir / "shap_summary_plot.png"
    shap_waterfall_png = xai_dir / "shap_waterfall_plot.png"
    lime_plot_png = xai_dir / "lime_local_explanation.png"
    csv_report = xai_dir / "shap_feature_contributions.csv"
    txt_report = xai_dir / "human_readable_explanations.txt"

    # ==========================================
    # SECTION 1: MODEL & XAI METADATA SUMMARY
    # ==========================================
    st.markdown("### ℹ️ 1. Model & XAI Interpretability Summary")
    
    model_name = metadata.get("model_name", art_status.get("model_name", "XGBoost (Calibrated)")) if metadata else "XGBoost (Calibrated)"
    metrics = metadata.get("metrics", {}) if metadata else {}
    
    num_features = metadata.get("num_features", 19) if metadata else 19
    train_date = metadata.get("training_date", "2026-09-17") if metadata else "2026-09-17"
    prauc_v = float(metrics.get("pr_auc", metrics.get("PR-AUC", 0.0923)))
    roc_v = float(metrics.get("roc_auc", metrics.get("ROC-AUC", 0.6804)))
    acc_v = float(metrics.get("accuracy", metrics.get("Accuracy", 0.9882)))
    f1_v = float(metrics.get("f1", metrics.get("F1-Score", 0.0328)))

    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    with m1:
        st.metric("Model Architecture", model_name[:18])
    with m2:
        st.metric("Training Date", str(train_date)[:10])
    with m3:
        st.metric("Auth Features", str(num_features))
    with m4:
        st.metric("PR-AUC (Primary)", f"{prauc_v:.4f}")
    with m5:
        st.metric("ROC-AUC", f"{roc_v:.4f}")
    with m6:
        st.metric("Accuracy", f"{acc_v*100:.2f}%")
    with m7:
        st.metric("F1 Score", f"{f1_v:.4f}")

    st.markdown("---")

    # ==========================================
    # SECTION 2: GLOBAL SHAP ANALYSIS
    # ==========================================
    st.markdown("### 🌐 2. Global SHAP Feature Importance Analysis")
    g_col1, g_col2 = st.columns([1, 1])

    with g_col1:
        st.markdown("#### Global SHAP Summary Plot")
        if shap_summary_png.exists():
            st.image(str(shap_summary_png), use_container_width=True)
        else:
            st.warning("⚠️ Global SHAP Summary image not found at `outputs/reports/xai/shap_summary_plot.png`.")

    with g_col2:
        st.markdown("#### Top 15 Global Feature Importance Ranking")
        if csv_report.exists():
            df_contrib = pd.read_csv(csv_report)
            df_top = df_contrib.head(15).copy()
            df_top["Rank"] = range(1, len(df_top) + 1)
            df_top["Mean_Abs_SHAP"] = df_top["Mean_Abs_SHAP_Impact"].round(4)
            st.dataframe(df_top[["Rank", "Feature", "Mean_Abs_SHAP"]], use_container_width=True)
        else:
            st.info("Global feature ranking matrix will load upon report generation.")

    st.markdown("---")

    # ==========================================
    # SECTION 3 & 4: LOCAL SHAP & LIME ANALYSIS
    # ==========================================
    st.markdown("### 🔍 3. Local Transaction Explanation (SHAP & LIME)")

    # Transaction Instance Selector
    sim_history = st.session_state.get("simulation_history", [])
    selected_txn_label = "Sample Transaction #0 (Default)"
    
    if sim_history:
        txn_options = [f"{t['Transaction_ID']} – Amount: ${t['Amount ($)']} ({t['Prediction']})" for t in sim_history]
        chosen = st.selectbox("Select Simulated Transaction to Explain", txn_options)
        selected_txn_label = chosen

    loc_col1, loc_col2 = st.columns(2)

    with loc_col1:
        st.markdown("#### Local SHAP Waterfall Attribution Plot")
        if shap_waterfall_png.exists():
            st.image(str(shap_waterfall_png), use_container_width=True)
        else:
            st.warning("⚠️ Local SHAP Waterfall image not found.")

    with loc_col2:
        st.markdown("#### Local LIME Decision Rules Plot")
        if lime_plot_png.exists():
            st.image(str(lime_plot_png), use_container_width=True)
        else:
            st.warning("⚠️ Local LIME Rules image not found.")

    st.markdown("---")

    # ==========================================
    # SECTION 5: INTERACTIVE FEATURE CONTRIBUTION EXPLORER
    # ==========================================
    st.markdown("### 🔎 4. Interactive Feature Contribution Explorer")

    if csv_report.exists():
        df_contrib_full = pd.read_csv(csv_report)

        filter_c1, filter_c2 = st.columns([2, 1])
        with filter_c1:
            search_query = st.text_input("🔍 Search Feature Name", value="")
        with filter_c2:
            direction_filter = st.selectbox("Filter Direction", ["All Features", "🔴 Increases Risk (+)", "🟢 Decreases Risk (-)"])

        df_filtered = df_contrib_full.copy()

        if search_query:
            df_filtered = df_filtered[df_filtered["Feature"].str.contains(search_query, case=False, na=False)]

        if direction_filter == "🔴 Increases Risk (+)":
            df_filtered = df_filtered[df_filtered["Sample_Row_SHAP_Value"] > 0]
        elif direction_filter == "🟢 Decreases Risk (-)":
            df_filtered = df_filtered[df_filtered["Sample_Row_SHAP_Value"] < 0]

        df_filtered["Direction"] = df_filtered["Sample_Row_SHAP_Value"].apply(
            lambda v: "🔴 Increases Risk (+)" if v > 0 else "🟢 Decreases Risk (-)"
        )
        df_filtered["SHAP Value"] = df_filtered["Sample_Row_SHAP_Value"].round(4)
        df_filtered["Global Impact"] = df_filtered["Mean_Abs_SHAP_Impact"].round(4)

        st.dataframe(
            df_filtered[["Feature", "SHAP Value", "Direction", "Global Impact"]].sort_values(
                by="Global Impact", ascending=False
            ),
            use_container_width=True,
        )
    else:
        st.info("Feature contribution explorer will load when `shap_feature_contributions.csv` is present.")

    st.markdown("---")

    # ==========================================
    # SECTION 6: COUNTERFACTUAL RECOURSE SIMULATION
    # ==========================================
    st.markdown("### 🔄 5. Counterfactual Recourse Simulation")
    st.markdown(
        """
        While SHAP & LIME explain historical model attributions, **Counterfactual XAI** answers:
        *What minimal, plausible modifications would lower the transaction's estimated risk score?*
        """
    )
    sample_cf = pd.DataFrame([
        {
            "Actionable Lever": "Transaction Amount",
            "Current State": "$75,000.00",
            "Simulated Recourse": "$2,500.00 (Customer normal baseline)",
            "Estimated Fused Risk": "42/100 (MEDIUM)",
            "Risk Drop": "-36 pts",
        },
        {
            "Actionable Lever": "Recipient Relationship",
            "Current State": "Newly added beneficiary",
            "Simulated Recourse": "Previously established recurring payee",
            "Estimated Fused Risk": "49/100 (MEDIUM)",
            "Risk Drop": "-29 pts",
        },
        {
            "Actionable Lever": "Transaction Timing",
            "Current State": "03:15 AM (Off-hours panic window)",
            "Simulated Recourse": "14:00 PM (Regular business hours)",
            "Estimated Fused Risk": "63/100 (HIGH)",
            "Risk Drop": "-15 pts",
        },
        {
            "Actionable Lever": "Device & Network Access",
            "Current State": "Unknown Proxy / Foreign Region",
            "Simulated Recourse": "Registered Mobile App / Domestic Home",
            "Estimated Fused Risk": "45/100 (MEDIUM)",
            "Risk Drop": "-33 pts",
        },
    ])
    st.dataframe(sample_cf, use_container_width=True)
    st.caption("ℹ️ Counterfactual simulation only. Illustrates decision boundary sensitivity without guaranteeing real-world safety.")

    st.markdown("---")

    # ==========================================
    # SECTION 7: HUMAN READABLE ENGLISH NARRATIVE
    # ==========================================
    st.markdown("### 💡 6. Human-Readable Natural Language Narrative Summary")

    narrative_sentences = []
    if txt_report.exists():
        with open(txt_report, "r", encoding="utf-8") as f:
            lines = f.readlines()
        narrative_sentences = [l.strip() for l in lines if l.strip() and not l.startswith("===")]

    if not narrative_sentences and csv_report.exists():
        df_c = pd.read_csv(csv_report)
        c_dict = dict(zip(df_c["Feature"], df_c["Sample_Row_SHAP_Value"]))
        narrative_sentences = generate_human_readable_summary(c_dict)

    if narrative_sentences:
        narrative_content = "\n".join([f"- {s}" for s in narrative_sentences])
        render_glass_card(f"Narrative Summary for {selected_txn_label}", narrative_content)
    else:
        render_glass_card("Narrative Summary", "Transaction parameters match normal legitimate baseline patterns.")

    st.markdown("---")

    # ==========================================
    # SECTION 7: TABBED VISUALIZATION GALLERY
    # ==========================================
    st.markdown("### 🖼️ 6. XAI Visualization Gallery & Artifact Viewer")

    tab1, tab2, tab3, tab4 = st.columns(4)

    with tab1:
        st.markdown("**1. Global SHAP Summary**")
        if shap_summary_png.exists():
            st.image(str(shap_summary_png), use_container_width=True)
    with tab2:
        st.markdown("**2. Local SHAP Waterfall**")
        if shap_waterfall_png.exists():
            st.image(str(shap_waterfall_png), use_container_width=True)
    with tab3:
        st.markdown("**3. Local LIME Rules**")
        if lime_plot_png.exists():
            st.image(str(lime_plot_png), use_container_width=True)
    with tab4:
        st.markdown("**4. Feature Attribution Matrix**")
        if csv_report.exists():
            st.dataframe(pd.read_csv(csv_report).head(10), use_container_width=True)

    st.markdown("---")

    # ==========================================
    # SECTION 8: XAI ARTIFACT DOWNLOAD CENTER
    # ==========================================
    st.markdown("### ⬇️ 7. XAI Artifact Download Center")

    d1, d2, d3, d4, d5 = st.columns(5)

    with d1:
        if csv_report.exists():
            with open(csv_report, "rb") as fp:
                st.download_button("📊 Download CSV Matrix", data=fp.read(), file_name=csv_report.name, mime="text/csv", use_container_width=True)
    with d2:
        if txt_report.exists():
            with open(txt_report, "rb") as fp:
                st.download_button("📄 Download Text Narrative", data=fp.read(), file_name=txt_report.name, mime="text/plain", use_container_width=True)
    with d3:
        if shap_summary_png.exists():
            with open(shap_summary_png, "rb") as fp:
                st.download_button("🖼️ SHAP Summary PNG", data=fp.read(), file_name=shap_summary_png.name, mime="image/png", use_container_width=True)
    with d4:
        if shap_waterfall_png.exists():
            with open(shap_waterfall_png, "rb") as fp:
                st.download_button("🌊 SHAP Waterfall PNG", data=fp.read(), file_name=shap_waterfall_png.name, mime="image/png", use_container_width=True)
    with d5:
        if lime_plot_png.exists():
            with open(lime_plot_png, "rb") as fp:
                st.download_button("🍋 LIME Rules PNG", data=fp.read(), file_name=lime_plot_png.name, mime="image/png", use_container_width=True)
