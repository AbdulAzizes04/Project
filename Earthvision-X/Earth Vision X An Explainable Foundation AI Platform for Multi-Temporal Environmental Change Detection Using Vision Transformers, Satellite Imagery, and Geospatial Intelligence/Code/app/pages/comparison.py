"""
Interactive Before/After Slider & Comparison Studio for EARTH VISION-X.
Implements Section 26:
Interactive slider: 2016 ◄──────────●──────────► 2026 revealing T1/T2 imagery.
"""

import streamlit as st
import numpy as np
import cv2
from app.components.header import render_header

def render_comparison_page(pipeline):
    """Renders Before/After Interactive Comparison Studio."""
    render_header(
        title="Interactive Before/After Satellite Comparison",
        subtitle="Multi-Temporal Split Swipe, Opacity Blending, and Pixel Flicker Analysis",
        active_model="Bitemporal Visualizer",
        status_label="Interactive Comparison"
    )

    if "current_analysis" not in st.session_state:
        st.info("Loading default baseline Sentinel-2 pair...")
        st.session_state["current_analysis"] = pipeline.run_pipeline()

    res = st.session_state["current_analysis"]
    img1 = res["img_t1"]
    img2 = res["img_t2"]
    t1_yr = res["t1_year"]
    t2_yr = res["t2_year"]

    st.markdown("### 🎛️ Interactive Multi-Temporal Slider")
    st.markdown(f"Drag the slider below to smoothly transition and compare satellite imagery between **{t1_yr}** and **{t2_yr}**.")

    # Section 26 Slider
    col_s1, col_s2, col_s3 = st.columns([1, 6, 1])
    with col_s1:
        st.markdown(f"<div style='text-align: right; font-weight: 700; color: #38BDF8; margin-top: 8px;'>{t1_yr} ◄</div>", unsafe_allow_html=True)
    with col_s2:
        blend_val = st.slider(
            "Temporal Transition (2016 ↔ 2026)",
            min_value=0.0,
            max_value=1.0,
            value=0.50,
            step=0.01,
            label_visibility="collapsed"
        )
    with col_s3:
        st.markdown(f"<div style='text-align: left; font-weight: 700; color: #10B981; margin-top: 8px;'>► {t2_yr}</div>", unsafe_allow_html=True)

    # Blend Mode Selector
    mode = st.radio("Comparison Mode", ["Vertical Split Curtain (Wipe)", "Alpha Opacity Blend", "Difference Heatmap Wipe"], horizontal=True)

    h, w = img1.shape[:2]

    if mode == "Vertical Split Curtain (Wipe)":
        split_x = int(w * blend_val)
        combined = img2.copy()
        combined[:, :split_x] = img1[:, :split_x]
        # Draw luminous divider line
        if 0 < split_x < w:
            combined[:, max(0, split_x - 2):min(w, split_x + 2)] = [0.22, 0.74, 0.97] # Cyan line
        st.image(np.clip(combined, 0.0, 1.0), caption=f"Split View: Left = {t1_yr} ({blend_val*100:.0f}%) | Right = {t2_yr} ({(1-blend_val)*100:.0f}%)", use_container_width=True)

    elif mode == "Alpha Opacity Blend":
        blended = (1.0 - blend_val) * img1 + blend_val * img2
        st.image(np.clip(blended, 0.0, 1.0), caption=f"Alpha Blend ({blend_val*100:.0f}% {t2_yr})", use_container_width=True)

    else:
        diff = np.abs(img1 - img2)
        diff_mag = np.mean(diff, axis=2)
        diff_colored = cv2.applyColorMap((diff_mag * 255).astype(np.uint8), cv2.COLORMAP_JET)
        diff_colored = cv2.cvtColor(diff_colored, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        st.image(diff_colored, caption=f"Absolute Difference Heatmap ({t1_yr} vs {t2_yr})", use_container_width=True)

    st.markdown("---")

    # Side-by-side synchronizer
    st.markdown("### 🔍 Side-by-Side Synchronized Inspector")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"##### 📷 Sentinel-2 ({t1_yr})")
        st.image(np.clip(img1, 0.0, 1.0), use_container_width=True)
    with c2:
        st.markdown(f"##### 📷 Sentinel-2 ({t2_yr})")
        st.image(np.clip(img2, 0.0, 1.0), use_container_width=True)
