"""
Dataset Explorer Page Controller.
Inspects Sentinel-2, LEVIR-CD, SYSU-CD, WHU-CD, Landsat, and Dynamic EarthNet datasets.
Generates real satellite benchmark datasets on demand.
"""

import streamlit as st
import pandas as pd
from earth_vision_x.app.components.header import render_header
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator

def render_dataset_explorer_page():
    render_header(
        "Satellite Dataset Explorer",
        "Benchmark Datasets for Bitemporal Change Detection & Vision Transformers"
    )

    datasets_info = [
        {"Dataset": "Sentinel-2 L2A", "Sensor": "Multispectral (13 Bands)", "Resolution": "10m", "Pairs": "10,000+", "Type": "Environmental & Forestry"},
        {"Dataset": "LEVIR-CD", "Sensor": "Optical RGB", "Resolution": "0.5m", "Pairs": "637 pairs", "Type": "Building & Urban Expansion"},
        {"Dataset": "SYSU-CD", "Sensor": "Optical RGB", "Resolution": "0.5m", "Pairs": "20,000 pairs", "Type": "Urban & Vegetation"},
        {"Dataset": "WHU-CD", "Sensor": "Aerial RGB", "Resolution": "0.2m", "Pairs": "12,796 pairs", "Type": "Infrastructure & Building"},
        {"Dataset": "Landsat 8/9", "Sensor": "OLI/TIRS (11 Bands)", "Resolution": "30m", "Pairs": "50,000+", "Type": "Global Environmental Change"},
        {"Dataset": "DynamicEarthNet", "Sensor": "PlanetScope Daily", "Resolution": "3m", "Pairs": "75 cubes", "Type": "Daily Land Cover Dynamics"}
    ]

    st.subheader("📚 Supported Benchmark Datasets")
    df = pd.DataFrame(datasets_info)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("⚡ Generate Real Satellite Benchmark Dataset")
    st.write("Acquire real bitemporal satellite image pairs for immediate training and testing.")

    col1, col2 = st.columns([2, 1])
    with col1:
        num_samples = st.slider("Number of Sample Pairs to Generate", 4, 20, 8)
    with col2:
        st.write("")
        st.write("")
        if st.button("🚀 Generate Benchmark Samples", type="primary"):
            with st.spinner("Retrieving real optical satellite benchmark pairs..."):
                samples = SampleDatasetGenerator.generate_real_benchmark(num_samples=num_samples)
                st.session_state["sample_dataset"] = samples
                st.success(f"Generated {num_samples} real sample pairs successfully!")

    if "sample_dataset" in st.session_state:
        st.markdown("### 🖼️ Generated Sample Dataset Inspection")
        samples = st.session_state["sample_dataset"]
        selected_idx = st.selectbox("Select Sample Index to Preview", range(len(samples["t1_paths"])))

        c1, c2, c3 = st.columns(3)
        with c1:
            st.image(samples["t1_paths"][selected_idx], caption="Time-1 (Before)", use_container_width=True)
        with c2:
            st.image(samples["t2_paths"][selected_idx], caption="Time-2 (After)", use_container_width=True)
        with c3:
            st.image(samples["mask_paths"][selected_idx], caption="Ground Truth Change Mask", use_container_width=True)
