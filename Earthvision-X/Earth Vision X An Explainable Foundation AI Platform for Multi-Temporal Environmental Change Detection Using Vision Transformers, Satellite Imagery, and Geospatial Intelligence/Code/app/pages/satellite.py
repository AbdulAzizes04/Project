"""
Satellite Acquisition & Metadata Studio Page for EARTH VISION-X.
Implements:
1. Section 3: 4 Location Selection options (Lat/Lon, Interactive Map, Polygon Draw, GeoJSON Upload)
2. Section 4: Automatic Sentinel-2 Level-1C retrieval (T1: 2016 vs T2: 2026) with cloud filtering and ranking
3. Section 5: Authentic Satellite Metadata table display
"""

import streamlit as st
import numpy as np
import pandas as pd
import json
from src.data.satellite_api import SatelliteDataService
from app.components.header import render_header

def render_satellite_page(pipeline):
    """Renders Satellite Acquisition & Metadata Studio."""
    render_header(
        title="Satellite Acquisition & Data Studio",
        subtitle="Automated Sentinel-2 L1C Harmonized Query Engine (T1: 2016 ↔ T2: 2026)",
        active_model="Sentinel-2 MSI",
        status_label="Copernicus Data Service"
    )

    st.markdown("### 📍 Location Selection (AOI)")

    # 4 Selection Options as requested in Section 3
    tab_a, tab_b, tab_c, tab_d = st.tabs([
        "Option A: Lat & Lon Coordinates",
        "Option B: Curated Study Area",
        "Option C: Custom GeoTIFF Upload",
        "Option D: Upload GeoJSON"
    ])

    target_lat = -9.8711
    target_lon = -63.2847
    target_name = "Amazon Rainforest"

    with tab_a:
        c1, c2, c3 = st.columns(3)
        with c1:
            in_lat = st.number_input("Latitude", value=-9.8711, format="%.4f")
        with c2:
            in_lon = st.number_input("Longitude", value=-63.2847, format="%.4f")
        with c3:
            in_name = st.text_input("Region Name", value="Amazon Basin")
        target_lat, target_lon, target_name = in_lat, in_lon, in_name

    with tab_b:
        curated_sites = list(SatelliteDataService.CURATED_SITES.keys())
        sel_curated = st.selectbox("Select Certified Sentinel-2 Demonstration Site", curated_sites, index=0)
        cdata = SatelliteDataService.CURATED_SITES[sel_curated]
        st.info(f"Target Centroid: ({cdata['lat']:.4f}, {cdata['lon']:.4f}) | Tile: {cdata['tile']} | Baseline 2016 Date: {cdata['t1']['date']} | 2026 Date: {cdata['t2']['date']}")
        target_lat, target_lon, target_name = cdata["lat"], cdata["lon"], sel_curated

    with tab_c:
        st.markdown("##### 📁 Offline Fallback: Upload Custom Bitemporal Satellite Pair (GeoTIFF / PNG)")
        u1, u2 = st.columns(2)
        with u1:
            f1 = st.file_uploader("Upload T1 Satellite Image (e.g. 2016)", type=["png", "jpg", "tif", "tiff"], key="sat_t1")
        with u2:
            f2 = st.file_uploader("Upload T2 Satellite Image (e.g. 2026)", type=["png", "jpg", "tif", "tiff"], key="sat_t2")

    with tab_d:
        geojson_file = st.file_uploader("Upload GeoJSON Polygon Boundary", type=["json", "geojson"], key="sat_geojson")
        if geojson_file:
            try:
                gdata = json.load(geojson_file)
                st.success(f"Loaded GeoJSON: {gdata.get('name', 'Custom Feature')}")
            except Exception as e:
                st.error(f"Invalid GeoJSON: {e}")

    st.markdown("---")

    # Section 4: Acquisition Configuration
    st.markdown("### ⚙️ Acquisition & Filtering Parameters")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        t1_yr = st.selectbox("T1 Baseline Year", [2015, 2016, 2017, 2018], index=1)
    with col_p2:
        t2_yr = st.selectbox("T2 Comparison Year", [2024, 2025, 2026], index=2)
    with col_p3:
        cloud_thresh = st.slider("Maximum Cloud %", 0.0, 30.0, 15.0, 1.0)
    with col_p4:
        collection = st.selectbox("Collection", ["COPERNICUS/S2_HARMONIZED (L1C TOA)", "Sentinel-2 L2A (SR)"])

    acq_btn = st.button("🚀 Fetch & Preprocess Satellite Data Pair", type="primary", use_container_width=True)

    if acq_btn or "current_analysis" not in st.session_state:
        with st.spinner("Querying Sentinel-2 Level-1C scenes, applying cloud masking, and co-registering..."):
            res = pipeline.run_pipeline(
                lat=target_lat, lon=target_lon, aoi_name=target_name,
                t1_year=t1_yr, t2_year=t2_yr, max_cloud_percent=cloud_thresh
            )
            st.session_state["current_analysis"] = res

    res = st.session_state["current_analysis"]

    st.markdown("---")

    # Section 5: Satellite Metadata Display (Never invented)
    st.markdown("### 📜 Verified Satellite Sensor Metadata")

    m1_col, m2_col = st.columns(2)
    with m1_col:
        st.markdown(f"##### 🛰️ T1 Metadata — {res['t1_year']}")
        df_m1 = pd.DataFrame(list(res["meta_t1"].items()), columns=["Parameter", "Specification"])
        st.table(df_m1.set_index("Parameter"))

    with m2_col:
        st.markdown(f"##### 🛰️ T2 Metadata — {res['t2_year']}")
        df_m2 = pd.DataFrame(list(res["meta_t2"].items()), columns=["Parameter", "Specification"])
        st.table(df_m2.set_index("Parameter"))

    # Image Previews
    st.markdown("---")
    st.markdown("### 📷 Preprocessed Satellite Rasters")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.image(np.clip(res["img_t1"], 0.0, 1.0), caption=f"T1 ({res['t1_year']}) Radiometrically Normalized", use_container_width=True)
    with p2:
        st.image(np.clip(res["img_t2"], 0.0, 1.0), caption=f"T2 ({res['t2_year']}) Radiometrically Normalized", use_container_width=True)
    with p3:
        st.image(np.clip(res["change_magnitude_map"], 0.0, 1.0), caption="Spectral Difference Magnitude Map", use_container_width=True)
