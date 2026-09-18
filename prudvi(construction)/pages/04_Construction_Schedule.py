"""
BuildVerse AI — Phase 2: AI Construction Planner & Gantt Schedule
"""

import streamlit as st
from datetime import datetime, date
from config import ASSETS_DIR
from database.db import get_project, save_schedules, save_project
from ai.construction.scheduler import generate_full_construction_schedule
from visualization.gantt_chart import create_gantt_chart
from visualization.charts import create_budget_donut_chart

st.set_page_config(
    page_title="Construction Schedule — BuildVerse AI",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Phase 2 — AI Construction Schedule Generator</h1>
    <p>Automated 12-phase construction breakdown, critical path Gantt charts, cost allocation, and trade labor scheduling.</p>
</div>
""", unsafe_allow_html=True)

curr_pid = st.session_state.get("current_project_id")

if not curr_pid:
    st.warning("Please select or create a project in **02 Project Details** first.")
else:
    project = get_project(curr_pid)
    
    if not project:
        st.error("Project data not found.")
    else:
        st.subheader("1. Construction Parameters & Inputs")
        
        with st.form("schedule_input_form"):
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                start_d = st.date_input("Construction Start Date", value=date.today())
                comp_d = st.date_input("Desired Completion Date", value=date(2026, 12, 31))
            with sc2:
                workers = st.number_input("Workers Available On-Site", min_value=2, max_value=100, value=project.get("workers_available", 12))
                work_hrs = st.number_input("Working Hours Per Day", min_value=4.0, max_value=16.0, value=project.get("working_hours_per_day", 8.0))
            with sc3:
                mat_pref = st.selectbox("Material Preference", ["Premium / High Strength", "Standard Commercial", "Eco-Friendly / Flyash"], index=1)
                weather = st.selectbox("Weather Region", ["Moderate / Ideal", "Monsoon Heavy", "Extreme Heat / Arid"], index=0)
                
            generate_btn = st.form_submit_button("🚀 Generate AI Phase Schedule", type="primary")

        if generate_btn or not project.get("schedules"):
            # Total sqft calculation across floors
            total_sqft = 0.0
            for f in project.get("floors", []):
                for r in f.get("rooms", []):
                    total_sqft += r.get("length", 10.0) * r.get("width", 10.0)
                    
            if total_sqft == 0.0:
                total_sqft = project["plot_area"]
                
            schedules_data = generate_full_construction_schedule(
                project_id=curr_pid,
                total_sqft=total_sqft,
                num_floors=project.get("num_floors", 1),
                total_budget=project.get("budget", 200000.0),
                start_date=start_d.strftime("%Y-%m-%d"),
                desired_completion_date=comp_d.strftime("%Y-%m-%d"),
                workers_available=workers,
                working_hours_per_day=work_hrs
            )
            
            save_schedules(curr_pid, schedules_data)
            
            # Update project timeline fields
            project["start_date"] = start_d.strftime("%Y-%m-%d")
            project["completion_date"] = comp_d.strftime("%Y-%m-%d")
            project["workers_available"] = workers
            project["working_hours_per_day"] = work_hrs
            save_project(project)
            
            project = get_project(curr_pid) # Refresh
            st.success("AI Construction Schedule generated and saved to database!")

        schedules = project.get("schedules", [])
        
        if schedules:
            st.divider()
            st.subheader("2. Visual Schedule & Critical Path Analytics")
            
            tab_gantt, tab_timeline, tab_budget = st.tabs(["📊 Interactive Gantt Chart", "📅 Phase Timeline List", "💰 Cost & Material Distribution"])
            
            with tab_gantt:
                fig_gantt = create_gantt_chart(schedules)
                st.plotly_chart(fig_gantt, use_container_width=True)

            with tab_timeline:
                st.markdown("#### Complete 12-Phase Schedule Breakdown")
                st_data = []
                for s in schedules:
                    st_data.append({
                        "Phase": s.get("phase_name"),
                        "Start Date": s.get("start_date"),
                        "End Date": s.get("end_date"),
                        "Duration": f"{s.get('duration_days')} Days",
                        "Cost Allocation": f"${s.get('cost'):,.2f}",
                        "Assigned Labor": f"{s.get('labor')} Workers",
                        "Dependencies": ", ".join(s.get("dependencies", [])) or "None",
                        "Required Materials": s.get("materials")
                    })
                st.dataframe(st_data, use_container_width=True)

            with tab_budget:
                c1, c2 = st.columns(2)
                with c1:
                    fig_donut = create_budget_donut_chart(schedules)
                    st.plotly_chart(fig_donut, use_container_width=True)
                with c2:
                    st.markdown("""
                    <div class="buildverse-card-accent">
                        <h4 style="color: #0891B2;">🛠️ Material Allocation Insights</h4>
                        <p style="font-size: 0.85rem; color: #0F172A;">
                            • <b>Foundation & Slab:</b> Accounts for 55% of structural steel and high-grade cement.<br>
                            • <b>Plastering & Masonry:</b> Sand and fine aggregate dispatch planned during Month 2.<br>
                            • <b>Electrical & Plumbing:</b> Conduit piping installed prior to plaster curing.<br>
                            • <b>Finishing:</b> Low-VOC eco paint and porcelain flooring tiles staged.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
