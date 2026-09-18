"""
Explainable AI (XAI) Console Page for EARTH VISION-X.
Implements:
1. Section 17: Interactive switcher between 5 XAI algorithms:
   - Attention Rollout
   - Grad-CAM
   - SHAP Feature Contributions
   - LIME Superpixels
   - Integrated Gradients (Captum)
2. Section 18: Spectral Attribution Breakdown:
   Blue, Green, Red, NIR, SWIR, NDVI, NDWI (Actual calculated values)
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from app.components.header import render_header

def render_xai_page(pipeline):
    """Renders Multi-Modal Explainable AI Console."""
    render_header(
        title="Explainable AI (XAI) Attribution Console",
        subtitle="Transformer Attention Rollout, Spatial Gradients, SHAP, LIME, and Captum Attributions",
        active_model="XAI Multi-Modal Suite",
        status_label="XAI Active"
    )

    if "current_analysis" not in st.session_state:
        st.session_state["current_analysis"] = pipeline.run_pipeline()

    res = st.session_state["current_analysis"]

    # -------------------------------------------------------------
    # Section 18: Spectral Channel SHAP Contributions
    # -------------------------------------------------------------
    st.markdown("### 🌈 Spectral Channel & Index Contributions (Section 18)")
    st.markdown("Measures relative sensitivity of model prediction across Sentinel-2 bands and biophysical indices.")

    shap_data = res["shap_scores"]
    df_shap = pd.DataFrame(list(shap_data.items()), columns=["Spectral Channel / Index", "Attribution (%)"])

    col_chart, col_table = st.columns([1.6, 1], gap="medium")
    with col_chart:
        fig = px.bar(
            df_shap,
            x="Spectral Channel / Index",
            y="Attribution (%)",
            color="Spectral Channel / Index",
            color_discrete_sequence=["#38BDF8", "#34D399", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#06B6D4"],
            text="Attribution (%)"
        )
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            height=280
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.table(df_shap.set_index("Spectral Channel / Index"))

    st.markdown("---")

    # -------------------------------------------------------------
    # Section 17: Interactive Switcher between 5 XAI Methods
    # -------------------------------------------------------------
    st.markdown("### 🔬 Multi-Modal Spatial Explanations Switcher (Section 17)")

    xai_method = st.radio(
        "Select Attribution Method",
        ["Attention Rollout", "Grad-CAM", "SHAP Feature Map", "LIME Superpixels", "Integrated Gradients"],
        horizontal=True
    )

    c_map, c_desc = st.columns([1.3, 1], gap="medium")

    with c_map:
        if xai_method == "Attention Rollout":
            st.markdown("##### 👁️ Vision Transformer Attention Rollout Heatmap")
            st.image(np.clip(res["attention_rollout"], 0.0, 1.0), caption="Self-Attention Rollout across 12 ViT-Base Encoder Blocks", use_container_width=True)

        elif xai_method == "Grad-CAM":
            st.markdown("##### 🌡️ Bitemporal Difference Grad-CAM Heatmap")
            st.image(np.clip(res["grad_cam"], 0.0, 1.0), caption="Gradient-Weighted Class Activation Map on Difference Representation", use_container_width=True)

        elif xai_method == "SHAP Feature Map":
            st.markdown("##### 📊 Spectral Change Magnitude Map")
            st.image(np.clip(res["change_magnitude_map"], 0.0, 1.0), caption="Multispectral Vector Euclidean Distance", use_container_width=True)

        elif xai_method == "LIME Superpixels":
            st.markdown("##### 🧩 SLIC Superpixel Boundary Attribution")
            st.image(res["lime_overlay"], caption="LIME SLIC Superpixel Boundary Regions Driving Classification", use_container_width=True)

        else:
            st.markdown("##### 📐 Captum Integrated Gradients Map")
            st.image(np.clip(res["integrated_gradients"], 0.0, 1.0), caption="Axiomatic Path Integral Pixel Attribution Map", use_container_width=True)

    with c_desc:
        st.markdown("##### 💡 Technical Explanation & Theory")
        if xai_method == "Attention Rollout":
            st.markdown(
                """
                **Vision Transformer Attention Rollout**:
                Recursively tracks token self-attention matrices across all 12 transformer encoder layers:
                $$R_l = (0.5 \\cdot A_l + 0.5 \\cdot I) \\times R_{l-1}$$
                Highlights how information propagates from input patch tokens (16×16 px) to environmental boundary decisions.
                """
            )
        elif xai_method == "Grad-CAM":
            st.markdown(
                """
                **Bitemporal Grad-CAM**:
                Computes gradients of the target change class score with respect to the bitemporal difference feature maps:
                $$\\alpha_k = \\frac{1}{Z} \\sum_{i,j} \\frac{\\partial y_c}{\\partial A_{i,j}^k}$$
                Produces a coarse localization heatmap highlighting discriminative spatial regions.
                """
            )
        elif xai_method == "SHAP Feature Map":
            st.markdown(
                """
                **SHAP (SHapley Additive exPlanations)**:
                Computes Shapley values across spectral bands (B2, B3, B4, B8, B11, NDVI, NDWI) to assign equitable feature importance to each sensor band.
                """
            )
        elif xai_method == "LIME Superpixels":
            st.markdown(
                """
                **LIME (Local Interpretable Model-agnostic Explanations)**:
                Segments the satellite scene into SLIC superpixels and measures prediction sensitivity when superpixels are perturbed, outlining boundary influence.
                """
            )
        else:
            st.markdown(
                """
                **Captum Integrated Gradients**:
                Satisfies completeness and implementation invariance by computing the path integral of gradients along a straight line from a black/neutral baseline.
                """
            )
