"""
BuildVerse AI — Phase 4: Automated AI Report PDF Generator
"""

import streamlit as st
import os
from config import ASSETS_DIR
from database.db import get_project, get_monitoring_logs
from api.routes import BuildVerseAPI

st.set_page_config(
    page_title="AI Reports — BuildVerse AI",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Phase 4 — Automated AI Construction Reports</h1>
    <p>Generate professional ReportLab PDF project status reports containing progress metrics, phase timelines, image inspections, and AI recovery plans.</p>
</div>
""", unsafe_allow_html=True)

curr_pid = st.session_state.get("current_project_id")

if not curr_pid:
    st.warning("Please select or create a project in **02 Project Details** first.")
else:
    project = get_project(curr_pid)
    logs = get_monitoring_logs(curr_pid)
    latest_log = logs[0] if logs else None
    
    if not project:
        st.error("Project not found.")
    else:
        st.markdown(f"### Report Configuration — Project: **{project['name']}**")
        
        c_rep1, c_rep2 = st.columns([2, 1])
        
        with c_rep1:
            st.markdown("""
            <div class="buildverse-card-accent">
                <h4 style="color: #0891B2;">📄 Executive PDF Report Structure</h4>
                <ul style="color: #0F172A; font-size: 0.9rem; line-height: 1.6;">
                    <li><b>Executive Summary Header:</b> Project name, owner, site location, plot area, total budget.</li>
                    <li><b>Key Progress Metrics Table:</b> Overall completion %, verified status badge, labor headcount.</li>
                    <li><b>Complete Phase Timeline Breakdown:</b> 12-stage schedule table with costs and dependencies.</li>
                    <li><b>AI Site Inspection Findings:</b> Detailed computer vision analysis and recovery plans.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with c_rep2:
            st.markdown("#### Export Settings")
            include_ai = st.checkbox("Include AI Recommendations", value=True)
            include_timeline = st.checkbox("Include 12-Phase Timeline", value=True)
            
            gen_pdf = st.button("📥 Generate & Export PDF Report", type="primary")

        if gen_pdf:
            pdf_path = BuildVerseAPI.export_pdf_report(project, latest_log)
            
            if os.path.exists(pdf_path):
                st.success("PDF Report generated successfully!")
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.download_button(
                    label="⬇️ Download Construction Executive Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"BuildVerse_Report_{project['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Failed to compile PDF report.")
