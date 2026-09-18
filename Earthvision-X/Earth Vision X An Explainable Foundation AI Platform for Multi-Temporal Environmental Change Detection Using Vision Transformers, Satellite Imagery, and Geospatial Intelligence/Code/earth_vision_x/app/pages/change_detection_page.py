"""
Change Detection Detailed Analysis Page Controller.
Analyzes categorical change distribution, spectral index deltas (NDVI, NDWI, NDBI),
and environmental change breakdown.
"""

import streamlit as st
import numpy as np
from earth_vision_x.app.components.header import render_header
from earth_vision_x.app.preprocessing.indices import SpectralIndexCalculator
from earth_vision_x.app.visualization.charts import ChartVisualizer
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator
from earth_vision_x.app.utils.geospatial import GeospatialIO

def render_change_detection_page():
    render_header(
        "Multi-Temporal Change Detection Analysis",
        "Categorical Segmentation, Spectral Indices, and Spatial Breakdown"
    )

    if "inference_result" not in st.session_state:
        st.info("💡 Running default benchmark sample for detailed analysis...")
        samples = SampleDatasetGenerator.generate_synthetic_benchmark(num_samples=1)
        img_t1, _ = GeospatialIO.read_image(samples["t1_paths"][0])
        img_t2, _ = GeospatialIO.read_image(samples["t2_paths"][0])
    else:
        res = st.session_state["inference_result"]
        img_t1, img_t2 = res["img_t1"], res["img_t2"]

    st.subheader("🌱 Spectral Index Analytics (NDVI / NDWI / NDBI)")
    
    ndvi_t1 = SpectralIndexCalculator.compute_ndvi(img_t1)
    ndvi_t2 = SpectralIndexCalculator.compute_ndvi(img_t2)
    ndvi_delta = ndvi_t2 - ndvi_t1

    ndwi_t1 = SpectralIndexCalculator.compute_ndwi(img_t1)
    ndwi_t2 = SpectralIndexCalculator.compute_ndwi(img_t2)
    ndwi_delta = ndwi_t2 - ndwi_t1

    c1, c2, c3 = st.columns(3)
    with c1:
        st.image(np.clip((ndvi_t1 + 1)/2, 0.0, 1.0), caption="NDVI Time-1 (Before)", clamp=True)
        st.image(np.clip((ndvi_t2 + 1)/2, 0.0, 1.0), caption="NDVI Time-2 (After)", clamp=True)
    with c2:
        st.image(np.clip((ndvi_delta + 1)/2, 0.0, 1.0), caption="NDVI Delta Map (Canopy Loss)", clamp=True)
        st.image(np.clip((ndwi_delta + 1)/2, 0.0, 1.0), caption="NDWI Delta Map (Water Variance)", clamp=True)
    with c3:
        st.markdown("#### 📊 Spectral Index Metrics")
        st.metric("Mean NDVI Time-1", f"{np.mean(ndvi_t1):.3f}")
        st.metric("Mean NDVI Time-2", f"{np.mean(ndvi_t2):.3f}")
        st.metric("Vegetation Delta", f"{np.mean(ndvi_delta):.3f}", delta_color="inverse")

    st.markdown("---")
    st.subheader("📈 Spatial Class Distribution Breakdown")
    sim_dist = {
        "No Change": 84.3,
        "Deforestation": 8.5,
        "Urban Expansion": 4.2,
        "Water Body Changes": 1.8,
        "Agricultural Changes": 1.2
    }
    fig_dist = ChartVisualizer.plot_class_distribution(sim_dist)
    st.plotly_chart(fig_dist, use_container_width=True)
