"""
Main Dashboard Page Controller for EARTH VISION-X.
Implements the exact layout specified in Section 25:
1. Header & System Subtitle
2. AOI and Temporal Selectors (T1: 2016, T2: 2026)
3. Satellite Imagery Previews (T1 - 2016 vs T2 - 2026)
4. Interactive Folium Change Map with layer controls
5. Key Performance Indicators: Change Area (km²), Change (%), Primary Change, Confidence (%)
"""

import streamlit as st
import numpy as np
from streamlit_folium import folium_static

from app.components.header import render_header, render_metric_card
from src.geospatial.maps import MapVisualizer
from src.data.satellite_api import SatelliteDataService

def render_dashboard_page(pipeline):
    """Renders Section 25 Main Dashboard."""
    render_header(
        title="EARTH VISION-X",
        subtitle="Explainable Multi-Temporal Satellite Intelligence Platform for Environmental Change Detection",
        active_model="Siamese ViT-Base",
        status_label="ONLINE (2016 ↔ 2026)"
    )

    # -------------------------------------------------------------
    # 1. AOI Selection & Temporal Epoch Controls
    # -------------------------------------------------------------
    st.markdown("<div class='evx-card'>", unsafe_allow_html=True)
    st.markdown("##### 📍 Select Area of Interest (AOI) & Temporal Epochs")

    loc_mode = st.radio(
        "Location Mode",
        ["🔍 Search Any City / Region on Earth (Custom)", "🧭 Custom GPS Coordinates (Lat / Lon)", "⭐ Demonstration Sites"],
        horizontal=True,
        index=0
    )

    if loc_mode == "🔍 Search Any City / Region on Earth (Custom)":
        with st.form("aoi_custom_search_form"):
            c_search, c_t1, c_t2, c_btn = st.columns([3.0, 1, 1, 1.5], gap="small")
            with c_search:
                custom_query = st.text_input(
                    "Enter City, Landmark, or Geographic Region",
                    value=st.session_state.get("active_custom_query", "bengaluru, india"),
                    placeholder="e.g. Bengaluru, Cairo, Paris, Tokyo, Mumbai, Las Vegas, London"
                )
            with c_t1:
                t1_yr = st.number_input("T1 Year", min_value=2015, max_value=2026, value=2016, step=1, key="t1_c")
            with c_t2:
                t2_yr = st.number_input("T2 Year", min_value=2016, max_value=2026, value=2026, step=1, key="t2_c")
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                search_btn = st.form_submit_button("🚀 Analyze Location", type="primary", use_container_width=True)

        target_name = custom_query
        target_lat, target_lon = None, None
        if search_btn:
            st.session_state["active_custom_query"] = custom_query

    elif loc_mode == "🧭 Custom GPS Coordinates (Lat / Lon)":
        with st.form("aoi_gps_search_form"):
            c_lat, c_lon, c_name, c_t1, c_t2, c_btn = st.columns([1.3, 1.3, 1.8, 0.9, 0.9, 1.4], gap="small")
            with c_lat:
                target_lat = st.number_input("Latitude", value=12.9716, format="%.4f")
            with c_lon:
                target_lon = st.number_input("Longitude", value=77.5946, format="%.4f")
            with c_name:
                target_name = st.text_input("Region Name", value="Bengaluru AOI")
            with c_t1:
                t1_yr = st.number_input("T1 Year", min_value=2015, max_value=2026, value=2016, step=1, key="t1_g")
            with c_t2:
                t2_yr = st.number_input("T2 Year", min_value=2016, max_value=2026, value=2026, step=1, key="t2_g")
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                search_btn = st.form_submit_button("🚀 Analyze AOI", type="primary", use_container_width=True)

    else:
        c_aoi, c_t1, c_t2, c_btn = st.columns([3.0, 1, 1, 1.5], gap="small")
        curated_sites = list(SatelliteDataService.CURATED_SITES.keys())
        with c_aoi:
            sel_site = st.selectbox("Area of Interest (Study Region)", curated_sites, index=0)
        with c_t1:
            t1_yr = st.number_input("T1 Year", min_value=2015, max_value=2026, value=2016, step=1, key="t1_s")
        with c_t2:
            t2_yr = st.number_input("T2 Year", min_value=2016, max_value=2026, value=2026, step=1, key="t2_s")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            search_btn = st.button("🔍 Search Satellite Imagery", type="primary", use_container_width=True, key="btn_curated")

        target_name = sel_site
        site_data = SatelliteDataService.CURATED_SITES[sel_site]
        target_lat, target_lon = site_data["lat"], site_data["lon"]

    st.markdown("</div>", unsafe_allow_html=True)

    # Resolve coordinates if geocoding is needed
    if target_lat is None or target_lon is None:
        geo = SatelliteDataService.geocode_location(target_name)
        lat, lon = geo["lat"], geo["lon"]
        display_name = geo.get("name", target_name)
    else:
        lat, lon = target_lat, target_lon
        display_name = target_name

    location_key = f"{display_name}_{lat:.4f}_{lon:.4f}_{t1_yr}_{t2_yr}"

    needs_run = (
        search_btn or 
        "current_analysis" not in st.session_state or 
        st.session_state.get("current_location_key") != location_key or
        st.session_state.get("t1_yr") != t1_yr or
        st.session_state.get("t2_yr") != t2_yr
    )

    if needs_run:
        with st.spinner(f"Retrieving Sentinel-2 L1C imagery ({t1_yr} vs {t2_yr}) for {display_name} and running Siamese-ViT inference..."):
            res = pipeline.run_pipeline(
                lat=lat, lon=lon, aoi_name=display_name,
                t1_year=t1_yr, t2_year=t2_yr, max_cloud_percent=15.0,
                generate_pdf=False
            )
            st.session_state["current_analysis"] = res
            st.session_state["current_location_key"] = location_key
            st.session_state["selected_site"] = display_name
            st.session_state["t1_yr"] = t1_yr
            st.session_state["t2_yr"] = t2_yr

    res = st.session_state["current_analysis"]
    area_metrics = res["area_metrics"]
    meta_t1 = res["meta_t1"]
    meta_t2 = res["meta_t2"]

    st.markdown("---")

    # -------------------------------------------------------------
    # 2. Side-by-Side Satellite Imagery: T1 (2016) vs T2 (2026)
    # -------------------------------------------------------------
    col_t1, col_t2 = st.columns(2, gap="medium")

    with col_t1:
        st.markdown(
            f"""
            <div class="sat-frame">
                <div class="sat-frame-header">
                    <span>🛰️ T1 — {res['t1_year']} (Baseline Epoch)</span>
                    <span style="color: #94A3B8;">{meta_t1.get('Satellite', 'Sentinel-2A')} | {meta_t1.get('Acquisition Date', '2016-08-15')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.image(np.clip(res["img_t1"], 0.0, 1.0), caption=f"Sentinel-2 T1 ({res['t1_year']}) - Cloud Cover: {meta_t1.get('Cloud Percentage', '0.0%')}", use_container_width=True)

    with col_t2:
        st.markdown(
            f"""
            <div class="sat-frame">
                <div class="sat-frame-header">
                    <span>🛰️ T2 — {res['t2_year']} (Current Epoch)</span>
                    <span style="color: #94A3B8;">{meta_t2.get('Satellite', 'Sentinel-2B')} | {meta_t2.get('Acquisition Date', '2026-02-28')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.image(np.clip(res["img_t2"], 0.0, 1.0), caption=f"Sentinel-2 T2 ({res['t2_year']}) - Cloud Cover: {meta_t2.get('Cloud Percentage', '0.0%')}", use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # 3. Interactive Change Map
    # -------------------------------------------------------------
    st.markdown("### 🗺️ CHANGE MAP & GEOSPATIAL LAYERS")
    m = MapVisualizer.create_interactive_map(
        lat=res["lat"],
        lon=res["lon"],
        aoi_bbox=res["bbox"],
        img_t1=res["img_t1"],
        img_t2=res["img_t2"],
        change_mask=res["change_mask"],
        ndvi_change=res["ndvi_metrics"]["ndvi_change"],
        zoom_start=12
    )
    folium_static(m, width=1100, height=480)

    st.markdown("---")

    # -------------------------------------------------------------
    # 4. Key Performance Indicators (KPIs) from Section 25
    # -------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        render_metric_card(
            title="Change Area",
            value=f"{area_metrics['changed_area_km2']:.2f} km²",
            subtitle=f"of {area_metrics['total_area_km2']:.1f} km² AOI",
            theme="crimson"
        )

    with k2:
        render_metric_card(
            title="Change %",
            value=f"{area_metrics['change_percentage']:.2f}%",
            subtitle="Scene Surface Flux",
            theme="amber"
        )

    with k3:
        render_metric_card(
            title="Primary Change",
            value=area_metrics["primary_change"],
            subtitle="Detected Transformation",
            theme="emerald"
        )

    with k4:
        render_metric_card(
            title="Model Confidence",
            value=f"{area_metrics['confidence_percentage']:.1f}%",
            subtitle=area_metrics["uncertainty_level"],
            theme="cyan"
        )

    # -------------------------------------------------------------
    # 5. Executive AI Change Story Box
    # -------------------------------------------------------------
    st.markdown(
        f"""
        <div class="ai-story-box">
            <div style="font-weight: 700; color: #38BDF8; margin-bottom: 6px;">💡 AI CHANGE STORY</div>
            {res['ai_story'].replace(chr(10), '<br/>')}
        </div>
        """,
        unsafe_allow_html=True
    )
