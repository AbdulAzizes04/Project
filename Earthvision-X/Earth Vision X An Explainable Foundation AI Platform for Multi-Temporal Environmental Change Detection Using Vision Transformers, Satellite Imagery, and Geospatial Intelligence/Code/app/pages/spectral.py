"""
Multispectral, NDVI, and NDWI Analysis Studio for EARTH VISION-X.
Implements:
1. Section 7: Multispectral Bands (Blue, Green, Red, NIR, SWIR)
2. Section 21: NDVI Analysis (NDVI_T1, NDVI_T2, NDVI_CHANGE) and canopy gain/loss
3. Section 22: NDWI Analysis (NDWI_T1, NDWI_T2, NDWI_CHANGE) and water dynamics
"""

import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
from app.components.header import render_header, render_metric_card

def render_spectral_page(pipeline):
    """Renders Multispectral, NDVI, and NDWI Studio."""
    render_header(
        title="Multispectral & Biophysical Index Studio",
        subtitle="Spectral Radiance, NDVI Canopy Analytics, and NDWI Hydrological Dynamics",
        active_model="Sentinel-2 MSI Indices",
        status_label="Spectral Mode"
    )

    if "current_analysis" not in st.session_state:
        st.session_state["current_analysis"] = pipeline.run_pipeline()

    res = st.session_state["current_analysis"]
    bands_t1 = res["bands_t1"]
    bands_t2 = res["bands_t2"]
    ndvi_m = res["ndvi_metrics"]
    ndwi_m = res["ndwi_metrics"]
    t1_yr = res["t1_year"]
    t2_yr = res["t2_year"]

    tab_ndvi, tab_ndwi, tab_bands = st.tabs([
        "🌱 NDVI Vegetation Analysis",
        "💧 NDWI Hydrological Analysis",
        "🌈 Sentinel-2 Multispectral Stack (B2, B3, B4, B8, B11)"
    ])

    # -------------------------------------------------------------
    # Tab 1: Section 21 NDVI Analysis
    # -------------------------------------------------------------
    with tab_ndvi:
        st.markdown("### 🌲 Normalized Difference Vegetation Index (NDVI)")
        st.markdown("$$\\text{NDVI} = \\frac{\\text{NIR (B8)} - \\text{Red (B4)}}{\\text{NIR (B8)} + \\text{Red (B4)}}$$")

        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card(f"Mean NDVI ({t1_yr})", f"{ndvi_m['mean_ndvi_t1']:.3f}", "Baseline Photosynthesis", "emerald")
        with c2:
            render_metric_card(f"Mean NDVI ({t2_yr})", f"{ndvi_m['mean_ndvi_t2']:.3f}", "Current Epoch", "emerald")
        with c3:
            render_metric_card("Net NDVI Change", f"{ndvi_m['mean_ndvi_change']:+.3f}", f"{ndvi_m['canopy_loss_percentage']:.1f}% Canopy Loss", "crimson" if ndvi_m['mean_ndvi_change'] < 0 else "emerald")

        st.markdown("---")

        img_n1, img_n2, img_ndelta = st.columns(3)
        with img_n1:
            st.markdown(f"##### NDVI T1 ({t1_yr})")
            st.image(np.clip((ndvi_m["ndvi_t1"] + 1) / 2, 0.0, 1.0), caption=f"Mean NDVI: {ndvi_m['mean_ndvi_t1']:.3f}", use_container_width=True)
        with img_n2:
            st.markdown(f"##### NDVI T2 ({t2_yr})")
            st.image(np.clip((ndvi_m["ndvi_t2"] + 1) / 2, 0.0, 1.0), caption=f"Mean NDVI: {ndvi_m['mean_ndvi_t2']:.3f}", use_container_width=True)
        with img_ndelta:
            st.markdown("##### NDVI Change Map (Delta)")
            st.image(np.clip((ndvi_m["ndvi_change"] + 1) / 2, 0.0, 1.0), caption=f"Net Delta: {ndvi_m['mean_ndvi_change']:+.3f}", use_container_width=True)

        # Average NDVI Table from Section 21
        st.markdown("##### 📋 Average NDVI Verification Table")
        df_ndvi = pd.DataFrame([
            {"Epoch": f"{t1_yr}", "Average NDVI": f"{ndvi_m['mean_ndvi_t1']:.2f}"},
            {"Epoch": f"{t2_yr}", "Average NDVI": f"{ndvi_m['mean_ndvi_t2']:.2f}"},
            {"Epoch": "Change", "Average NDVI": f"{ndvi_m['mean_ndvi_change']:+.2f}"}
        ])
        st.table(df_ndvi.set_index("Epoch"))

    # -------------------------------------------------------------
    # Tab 2: Section 22 NDWI Analysis
    # -------------------------------------------------------------
    with tab_ndwi:
        st.markdown("### 💧 Normalized Difference Water Index (NDWI)")
        st.markdown("$$\\text{NDWI} = \\frac{\\text{Green (B3)} - \\text{NIR (B8)}}{\\text{Green (B3)} + \\text{NIR (B8)}}$$")

        w1, w2, w3 = st.columns(3)
        with w1:
            render_metric_card(f"Mean NDWI ({t1_yr})", f"{ndwi_m['mean_ndwi_t1']:.3f}", "Baseline Water Fraction", "cyan")
        with w2:
            render_metric_card(f"Mean NDWI ({t2_yr})", f"{ndwi_m['mean_ndwi_t2']:.3f}", "Current Epoch", "cyan")
        with w3:
            render_metric_card("Surface Water Delta", f"{ndwi_m['water_surface_delta_percentage']:+.1f}%", "Hydrological Surface Variance", "amber")

        st.markdown("---")

        img_w1, img_w2, img_wdelta = st.columns(3)
        with img_w1:
            st.markdown(f"##### NDWI T1 ({t1_yr})")
            st.image(np.clip((ndwi_m["ndwi_t1"] + 1) / 2, 0.0, 1.0), caption=f"Mean NDWI: {ndwi_m['mean_ndwi_t1']:.3f}", use_container_width=True)
        with img_w2:
            st.markdown(f"##### NDWI T2 ({t2_yr})")
            st.image(np.clip((ndwi_m["ndwi_t2"] + 1) / 2, 0.0, 1.0), caption=f"Mean NDWI: {ndwi_m['mean_ndwi_t2']:.3f}", use_container_width=True)
        with img_wdelta:
            st.markdown("##### NDWI Change Map (Delta)")
            st.image(np.clip((ndwi_m["ndwi_change"] + 1) / 2, 0.0, 1.0), caption=f"Net Delta: {ndwi_m['mean_ndwi_change']:+.3f}", use_container_width=True)

    # -------------------------------------------------------------
    # Tab 3: Section 7 Multispectral Stack
    # -------------------------------------------------------------
    with tab_bands:
        st.markdown("### 🛰️ Sentinel-2 Multispectral Channel Separation (T2)")
        b1, b2, b3, b4, b5 = st.columns(5)
        with b1:
            st.image(bands_t2["blue"], caption="Band 2 (Blue - 490nm)", use_container_width=True)
        with b2:
            st.image(bands_t2["green"], caption="Band 3 (Green - 560nm)", use_container_width=True)
        with b3:
            st.image(bands_t2["red"], caption="Band 4 (Red - 665nm)", use_container_width=True)
        with b4:
            st.image(bands_t2["nir"], caption="Band 8 (NIR - 842nm)", use_container_width=True)
        with b5:
            st.image(bands_t2["swir"], caption="Band 11 (SWIR - 1610nm)", use_container_width=True)
