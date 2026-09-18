"""
BuildVerse AI — Phase 6: Executive Analytics Dashboard & Virtual Site Telemetry
"""

import streamlit as st
from config import ASSETS_DIR
from database.db import get_project, get_monitoring_logs
from visualization.charts import create_progress_gauge, create_budget_donut_chart
from visualization.progress_graph import create_s_curve_graph
from visualization.dashboard import render_kpi_card

st.set_page_config(
    page_title="Executive Dashboard — BuildVerse AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Phase 6 — Executive Analytics & Construction Telemetry Dashboard</h1>
    <p>Real-time telemetry on overall project progress, room-by-room completion, stage timelines, productivity speed metrics, and AI recovery advice.</p>
</div>
""", unsafe_allow_html=True)

curr_pid = st.session_state.get("current_project_id")

if not curr_pid:
    st.warning("Please select or create a project in **02 Project Details** first.")
else:
    project = get_project(curr_pid)
    logs = get_monitoring_logs(curr_pid)
    
    if not project:
        st.error("Project data not found.")
    else:
        st.markdown(f"### Executive Project Overview — **{project['name']}**")
        
        # 1. Overall Project Progress Banner
        st.markdown("""
        <div style="background-color: #E0F2FE; border-left: 6px solid #0891B2; padding: 1.2rem; border-radius: 10px; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.2rem; font-weight: 800; color: #0F172A;">Overall Project Progress</span>
                <span style="font-size: 1.6rem; font-weight: 800; color: #0891B2;">72%</span>
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #0891B2; margin-top: 0.3rem;">
                ██████████████████░░░░ 72%
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. KPI Summary Row
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card("Current Stage", "Brick Work", "Stage 4 of 15", "#0891B2")
        with k2:
            render_kpi_card("Masonry Speed", "2.1 m²/day", "Target: 3.4 m²/day", "#F59E0B")
        with k3:
            render_kpi_card("Budget Consumption", f"${project['budget']*0.72:,.0f}", f"Budget: ${project['budget']:,.0f}", "#0284C7")
        with k4:
            render_kpi_card("Safety Index", "98/100", "Zero Incidents", "#10B981")

        st.divider()
        st.markdown("### 📊 Room-by-Room Construction Progress")
        
        r_cols = st.columns(4)
        rooms_demo = [
            ("Hall", 100, "Completed", "#10B981"),
            ("Kitchen", 84, "In Progress", "#0891B2"),
            ("Bedroom 1", 60, "In Progress", "#0284C7"),
            ("Balcony", 48, "In Progress", "#F59E0B")
        ]
        
        for idx, (r_name, r_pct, r_status, r_color) in enumerate(rooms_demo):
            with r_cols[idx]:
                num_blocks = int(r_pct / 10)
                bar_str = "█" * num_blocks + "░" * (10 - num_blocks)
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #BAE6FD; border-left: 5px solid {r_color}; padding: 1rem; border-radius: 8px;">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">{r_name}</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: {r_color}; margin: 0.2rem 0;">{r_pct}%</div>
                    <div style="font-family: monospace; font-weight: 700; color: {r_color}; font-size: 0.9rem;">{bar_str}</div>
                    <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; margin-top: 0.3rem;">Status: {r_status}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📅 Construction Timeline & Phase Badges")
        
        st.markdown("""
        <div style="display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
            <div style="background-color: #D1FAE5; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">✔ Foundation (Done)</div>
            <div style="background-color: #D1FAE5; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">✔ Columns (Done)</div>
            <div style="background-color: #D1FAE5; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">✔ Beam (Done)</div>
            <div style="background-color: #FEF3C7; color: #92400E; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">🟡 Brick Work (In Progress)</div>
            <div style="background-color: #E0F2FE; color: #0369A1; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">Upcoming Plastering</div>
            <div style="background-color: #F1F5F9; color: #475569; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">Pending Painting</div>
            <div style="background-color: #F1F5F9; color: #475569; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">Pending Interior</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🤖 AI Engineering Productivity Suggestions")
        
        c_sug1, c_sug2 = st.columns([1.2, 1])
        
        with c_sug1:
            st.markdown("""
            <div style="background-color: #FFFBEB; border-left: 6px solid #F59E0B; padding: 1.2rem; border-radius: 10px;">
                <h4 style="color: #92400E; margin-top: 0;">⚠️ Brickwork Velocity Advisory</h4>
                <p style="color: #78350F; font-size: 0.95rem; margin-bottom: 0.5rem;">
                    <b>Brick masonry is progressing slower than planned.</b>
                </p>
                <div style="font-size: 0.9rem; color: #451A03; line-height: 1.6;">
                    • <b>Current Speed:</b> <code>2.1 m²/day</code><br>
                    • <b>Required Speed:</b> <code>3.4 m²/day</code><br>
                    • <b>Recommendation:</b> Add one mason and two helpers.<br>
                    • <b>Expected Recovery:</b> Within 2 Days.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_sug2:
            schedules = project.get("schedules", [])
            if schedules:
                fig_donut = create_budget_donut_chart(schedules)
                st.plotly_chart(fig_donut, use_container_width=True)
