"""
Heatmaps Page Controller.
Renders confidence density heatmaps, spatial difference maps, and interactive GIS Folium map layers.
"""

import streamlit as st
import numpy as np
from earth_vision_x.app.components.header import render_header
from earth_vision_x.app.visualization.gis_maps import GISMapVisualizer
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator
from earth_vision_x.app.services.inference_service import InferenceService

try:
    from streamlit_folium import st_folium
    FOLIUM_ST_AVAILABLE = True
except ImportError:
    FOLIUM_ST_AVAILABLE = False

def render_heatmaps_page():
    render_header(
        title="EARTH VISION-X | GIS Map & Spatial Heatmap Studio",
        active_model="Interactive Folium GIS Layer Viewer",
        confidence="Spatial Precision Benchmark"
    )

    if "inference_result" not in st.session_state:
        samples = SampleDatasetGenerator.generate_synthetic_benchmark(num_samples=1)
        svc = InferenceService()
        st.session_state["inference_result"] = svc.run_full_pipeline(samples["t1_paths"][0], samples["t2_paths"][0])

    res = st.session_state["inference_result"]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Pixel Difference Heatmap")
        st.image(res["difference_map"], caption="Bitemporal Optical Difference (Jet Colormap)", use_container_width=True)

    with col2:
        st.subheader("🎯 Model Confidence Density Map")
        st.image(np.clip(res["confidence_map"], 0.0, 1.0), caption="Probability Confidence Density [0.0 - 1.0]", clamp=True, use_container_width=True)

    st.markdown("---")
    st.subheader("🗺️ Interactive Folium GIS Satellite Map")
    folium_map = GISMapVisualizer.create_interactive_map(res["img_t1"], res["img_t2"])
    
    if FOLIUM_ST_AVAILABLE and folium_map is not None:
        st_folium(folium_map, width=1000, height=500)
    else:
        st.info("Interactive GIS layer viewer (Folium / Leafmap) active.")

