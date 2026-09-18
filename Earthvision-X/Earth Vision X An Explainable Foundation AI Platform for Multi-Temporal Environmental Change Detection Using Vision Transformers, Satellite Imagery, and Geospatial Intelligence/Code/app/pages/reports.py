"""
Executive PDF Reports Page for EARTH VISION-X.
Implements Section 28:
Generates and downloads publication-grade ReportLab PDF reports incorporating all 17 sections.
"""

import os
import streamlit as st
from app.components.header import render_header
from src.reports.pdf_report import PDFReportBuilder

def render_reports_page(pipeline):
    """Renders PDF Report Generation & Export Page."""
    render_header(
        title="Executive PDF Intelligence Reports",
        subtitle="17-Section Automated Publication-Grade Environmental Intelligence Documentation",
        active_model="ReportLab PDF Engine",
        status_label="Export Ready"
    )

    if "current_analysis" not in st.session_state:
        st.session_state["current_analysis"] = pipeline.run_pipeline()

    res = st.session_state["current_analysis"]
    area_m = res["area_metrics"]
    meta_t1 = res["meta_t1"]
    meta_t2 = res["meta_t2"]

    st.markdown("### 📄 Document Summary & Audit Specifications")

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown(
            f"""
            <div style="background: rgba(15, 27, 51, 0.85); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; margin-bottom: 8px;">📍 GEOGRAPHIC & TEMPORAL AUDIT</div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 4px;">Target AOI: <b style="color:#F8FAFC;">{meta_t1.get('AOI', 'Amazon Rainforest')}</b></div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 4px;">Baseline Epoch (T1): <b style="color:#F8FAFC;">{res['t1_year']} ({meta_t1.get('Acquisition Date', '2016-08-15')})</b></div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 4px;">Target Epoch (T2): <b style="color:#F8FAFC;">{res['t2_year']} ({meta_t2.get('Acquisition Date', '2026-02-28')})</b></div>
                <div style="font-size: 0.78rem; color: #94A3B8;">Coordinate BBOX: <b style="color:#F8FAFC;">({res['lat']:.4f}, {res['lon']:.4f})</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_info2:
        st.markdown(
            f"""
            <div style="background: rgba(15, 27, 51, 0.85); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #10B981; margin-bottom: 8px;">🎯 AI VERDICT & KEY FINDINGS</div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 4px;">Primary Classification: <b style="color:#F8FAFC;">{area_m['primary_change']}</b></div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 4px;">Model Confidence: <b style="color:#34D399;">{area_m['confidence_percentage']:.1f}% ({area_m['uncertainty_level']})</b></div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 4px;">Transformed Surface Area: <b style="color:#EF4444;">{area_m['changed_area_km2']:.2f} km² ({area_m['change_percentage']:.2f}%)</b></div>
                <div style="font-size: 0.78rem; color: #94A3B8;">Report Format: <b style="color:#38BDF8;">IEEE Format (17 Sections, Vector Graphics)</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 17 Sections Outline Accordion
    with st.expander("🔍 Preview 17 Mandatory Sections Embedded in Document"):
        st.markdown(
            """
            1. **Project Title & System Subtitle** (EARTH VISION-X)
            2. **Study Area (AOI) Description**
            3. **Geographic Coordinates (Centroid, Bounding Box, CRS)**
            4. **T1 Satellite Sensor Metadata (Sentinel-2A, L1C TOA Harmonized)**
            5. **T2 Satellite Sensor Metadata (Sentinel-2B, L1C TOA Harmonized)**
            6. **Embedded T1 (2016) Satellite Imagery Figure**
            7. **Embedded T2 (2026) Satellite Imagery Figure**
            8. **Embedded Vision Transformer Binary Change Mask Figure**
            9. **NDVI Biophysical Canopy Dynamics & Variance Map**
            10. **NDWI Hydrological Surface Variance & Water Dynamics Map**
            11. **Quantitative Land-Cover Change Statistics Table**
            12. **Categorical Multi-Class Transformation Breakdown Table**
            13. **Prediction Confidence & Uncertainty Classification**
            14. **Embedded Explainable AI (XAI) Visualizations (Attention Rollout, Grad-CAM, SHAP)**
            15. **Grounded AI Change Story Narrative**
            16. **Deep Learning Model Architecture & Parameter Specifications**
            17. **Scientific Benchmark Evaluation & Confusion Matrix Table**
            """
        )

    st.markdown("---")

    # Generation and Download
    c_btn, c_down = st.columns([1, 1], gap="medium")

    with c_btn:
        generate_btn = st.button("🔄 Recompile 17-Section IEEE PDF Report", type="primary", use_container_width=True)

    if generate_btn or "pdf_report_path" not in res or not res.get("pdf_report_path"):
        with st.spinner("Compiling high-resolution vector maps, statistical tables, and narrative into PDF..."):
            pdf_path = PDFReportBuilder.generate_pdf(res)
            res["pdf_report_path"] = pdf_path
            st.session_state["current_analysis"] = res

    pdf_file = res.get("pdf_report_path")
    if pdf_file and os.path.exists(pdf_file):
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()

        with c_down:
            st.download_button(
                label=f"💾 Download IEEE PDF Report ({os.path.basename(pdf_file)})",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_file),
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        st.success(f"PDF Successfully compiled at `{pdf_file}` ({len(pdf_bytes):,} bytes)")
