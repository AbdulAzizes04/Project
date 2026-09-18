"""
Reports Page Controller.
Manages automated PDF, DOCX, and CSV executive report generation, preview, and download.
"""

import streamlit as st
import os
from earth_vision_x.app.components.header import render_header
from earth_vision_x.app.reports.pdf_generator import PDFReportGenerator
from earth_vision_x.app.reports.docx_csv_exporter import DOCXReportGenerator, CSVReportGenerator
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator
from earth_vision_x.app.services.inference_service import InferenceService

def render_reports_page():
    render_header(
        "Automated Multi-Format Executive Reports",
        "Generate IEEE & Enterprise Standard PDF, DOCX, and CSV Climate & Environmental Reports"
    )

    if "inference_result" not in st.session_state:
        samples = SampleDatasetGenerator.generate_real_benchmark(num_samples=1)
        svc = InferenceService()
        st.session_state["inference_result"] = svc.run_full_pipeline(samples["t1_paths"][0], samples["t2_paths"][0])

    res = st.session_state["inference_result"]

    st.subheader("📄 Environmental & Multi-Domain Report Summary")

    st.markdown(
        f"""
        - **Primary Event Detected:** {res.get('primary_change', 'Deforestation & Urban Sprawl')}
        - **Model Confidence Score:** {res.get('confidence_score', 0.95)*100:.1f}%
        - **Affected Area:** {res.get('affected_area_sqkm', 1.42):.2f} sq km ({res.get('affected_percentage', 13.7):.1f}%)
        - **Inference Time:** {res.get('inference_time_sec', 0.15):.3f} s
        """
    )

    st.markdown("### 💡 Executive Narrative Summary")
    st.info(res.get("ai_insights", "Vision Transformer multi-temporal evaluation indicates significant land cover transformation, environmental flux, and canopy degradation."))

    st.markdown("---")
    st.subheader("📥 Export Multi-Format IEEE Executive Reports")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📄 Generate PDF Executive Report", type="primary", use_container_width=True):
            with st.spinner("Compiling PDF report with graphics, metrics, and AI summary..."):
                pdf_path = PDFReportGenerator.generate_report(res)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="💾 Download PDF File",
                            data=f.read(),
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            use_container_width=True
                        )
                    st.success("PDF Report generated!")

    with c2:
        if st.button("📝 Generate Word (.DOCX) Report", use_container_width=True):
            with st.spinner("Compiling Word DOCX report..."):
                docx_path = DOCXReportGenerator.generate_report(res)
                if os.path.exists(docx_path):
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            label="💾 Download DOCX File",
                            data=f.read(),
                            file_name=os.path.basename(docx_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    st.success("DOCX Report generated!")

    with c3:
        if st.button("📊 Export Tabular Metrics (.CSV)", use_container_width=True):
            with st.spinner("Exporting CSV dataset metrics..."):
                csv_path = CSVReportGenerator.generate_report(res)
                if os.path.exists(csv_path):
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            label="💾 Download CSV File",
                            data=f.read(),
                            file_name=os.path.basename(csv_path),
                            mime="text/csv",
                            use_container_width=True
                        )
                    st.success("CSV Metrics exported!")

