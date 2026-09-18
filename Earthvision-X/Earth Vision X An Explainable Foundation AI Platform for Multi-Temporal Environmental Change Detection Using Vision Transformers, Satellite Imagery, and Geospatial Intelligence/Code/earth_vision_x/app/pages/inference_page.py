"""
Inference Page Controller.
Executes change detection on uploaded or benchmark image pairs,
displaying detected change category, confidence score, affected spatial area, and prediction time.
"""

import streamlit as st
import numpy as np
from earth_vision_x.app.components.header import render_header, render_metric_card
from earth_vision_x.app.config.constants import SupportedModels
from earth_vision_x.app.services.inference_service import InferenceService
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator

def render_inference_page():
    render_header(
        "Bitemporal Change Detection Inference",
        "High-Speed Vision Transformer Predictions with Area Metrics"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("⚙️ Inference Settings")
        model_choice = st.selectbox("Select Model Architecture", [m.value for m in SupportedModels])
        use_tta = st.checkbox("Test-Time Augmentation (TTA)", value=False)
        generate_pdf = st.checkbox("Generate PDF Report", value=True)

        input_option = st.radio("Select Image Input Source", ["Uploaded Images", "Use Real Satellite Benchmark Pair"])

        run_btn = st.button("🚀 Run Inference", type="primary")

    with col2:
        st.subheader("🛰️ Input Pair Selection")
        t1_input = None
        t2_input = None

        if input_option == "Uploaded Images":
            if "uploaded_t1" in st.session_state and "uploaded_t2" in st.session_state:
                t1_input = st.session_state["uploaded_t1"]
                t2_input = st.session_state["uploaded_t2"]
                c1, c2 = st.columns(2)
                c1.image(np.clip(t1_input, 0.0, 1.0), caption="Uploaded Time-1", clamp=True)
                c2.image(np.clip(t2_input, 0.0, 1.0), caption="Uploaded Time-2", clamp=True)
            else:
                st.warning("No uploaded images found! Please upload images on the 'Upload Images' page or select 'Use Real Satellite Benchmark Pair'.")
        else:
            samples = SampleDatasetGenerator.generate_real_benchmark(num_samples=1)
            t1_input = samples["t1_paths"][0]
            t2_input = samples["t2_paths"][0]
            c1, c2 = st.columns(2)
            c1.image(t1_input, caption="Benchmark Time-1")
            c2.image(t2_input, caption="Benchmark Time-2")

    if run_btn and t1_input is not None and t2_input is not None:
        with st.spinner("Executing Vision Transformer inference..."):
            service = InferenceService(model_name=model_choice)
            res = service.run_full_pipeline(t1_input, t2_input, use_tta=use_tta, generate_pdf=generate_pdf)
            st.session_state["inference_result"] = res
            st.success("Inference execution completed successfully!")

    if "inference_result" in st.session_state:
        st.markdown("---")
        res = st.session_state["inference_result"]
        st.subheader("📊 Inference Results & Impact Metrics")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Primary Change Detected", res["primary_change"])
        with m2:
            render_metric_card("Confidence Score", f"{res['confidence_score']*100:.1f}%")
        with m3:
            render_metric_card("Affected Area", f"{res['affected_area_sqkm']:.2f} sq km", f"{res['affected_percentage']:.1f}% of frame")
        with m4:
            render_metric_card("Prediction Time", f"{res['inference_time_sec']:.3f} s")

        st.markdown("### 🖼️ Change Overlay & Difference Maps")
        o1, o2, o3 = st.columns(3)
        with o1:
            st.image(res["color_mask"], caption="Categorical Change Mask")
        with o2:
            st.image(res["overlay"], caption="Change Overlay on Time-2")
        with o3:
            st.image(res["difference_map"], caption="Pixel Difference Heatmap")

        if "report_pdf_path" in res:
            st.info(f"📄 PDF Report generated and saved to `{res['report_pdf_path']}`")
