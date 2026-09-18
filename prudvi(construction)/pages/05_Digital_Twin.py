"""
BuildVerse AI — Phase 5: Interactive 3D Digital Twin Platform
"""

import streamlit as st
from config import ASSETS_DIR
from database.db import get_project, get_monitoring_logs
from ai.digital_twin.model_generator import generate_digital_twin_3d
from ai.digital_twin.twin_sync import sync_twin_with_progress

st.set_page_config(
    page_title="Digital Twin 3D — BuildVerse AI",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Digital Twin — Interactive 3D BIM Model</h1>
    <p>Real-time 3D structural model updated dynamically with site photo/video progress inspection logs.</p>
</div>
""", unsafe_allow_html=True)

curr_pid = st.session_state.get("current_project_id")

if not curr_pid:
    st.warning("Please select or create a project in **02 Project Details** first.")
else:
    project = get_project(curr_pid)
    logs = get_monitoring_logs(curr_pid)
    
    # Calculate latest overall progress
    latest_pct = logs[0]["overall_progress_pct"] if logs else 45.0
    
    twin_elements = sync_twin_with_progress(curr_pid, latest_pct)
    
    st.markdown(f"### Live Digital Twin Telemetry — Project: **{project['name']}**")
    
    col_twin, col_info = st.columns([3, 1])
    
    with col_twin:
        fig_twin = generate_digital_twin_3d(twin_elements)
        st.plotly_chart(fig_twin, use_container_width=True)

    with col_info:
        st.markdown("#### 🎨 Color Legend")
        st.markdown("""
        <div style="padding: 0.65rem; border-radius: 8px; background-color: #E0F2FE; border: 1.5px solid #0891B2; margin-bottom: 0.6rem;">
            <span style="color: #0891B2; font-weight: 800;">■ Completed</span> <br><span style="font-size: 0.8rem; color: #0F172A;">Verified site scan & cured structure</span>
        </div>
        <div style="padding: 0.65rem; border-radius: 8px; background-color: #BAE6FD; border: 1.5px solid #0284C7; margin-bottom: 0.6rem;">
            <span style="color: #0284C7; font-weight: 800;">■ In-Progress</span> <br><span style="font-size: 0.8rem; color: #0F172A;">Active phase work ongoing</span>
        </div>
        <div style="padding: 0.65rem; border-radius: 8px; background-color: #F8FAFC; border: 1.5px solid #CBD5E1; margin-bottom: 0.6rem;">
            <span style="color: #475569; font-weight: 800;">■ Pending</span> <br><span style="font-size: 0.8rem; color: #64748B;">Target wireframe phase</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### Element Inspector")
        for elem in twin_elements:
            status = elem['status']
            if status == "Completed":
                badge_html = '<span style="background-color: #E0F2FE; color: #0891B2; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;">Completed</span>'
            elif status == "In-Progress":
                badge_html = '<span style="background-color: #BAE6FD; color: #0284C7; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;">In-Progress</span>'
            else:
                badge_html = '<span style="background-color: #F1F5F9; color: #475569; padding: 2px 10px; border-radius: 12px; font-weight: 600; font-size: 0.8rem;">Pending</span>'
                
            st.markdown(f"• **{elem['element_name']}**: {badge_html}", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Digital Twin Synchronization Event Log")
    if logs:
        log_table = []
        for l in logs:
            log_table.append({
                "Date": l["log_date"],
                "Media Type": l["media_type"].upper(),
                "Verified Progress": f"{l['overall_progress_pct']}%",
                "Quality Index": f"{l['quality_score']}/100",
                "Status": l["status"]
            })
        st.dataframe(log_table, use_container_width=True)
    else:
        st.info("Upload site media in **06 Daily Progress** to see live sync event logs.")
