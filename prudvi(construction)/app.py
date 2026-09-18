"""
BuildVerse AI — Main Application Entry Point
"""

import streamlit as st
from pathlib import Path
from config import APP_NAME, APP_TAGLINE, THEME, ASSETS_DIR
from database.db import get_all_projects, get_project

# Set Page Config
st.set_page_config(
    page_title="BuildVerse AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS System
css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State Variables
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None

# Sidebar Header & Project Switcher
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #0891B2; margin: 0; font-size: 1.8rem; font-weight: 800;'>🏗️ BuildVerse AI</h1>
        <p style='color: #475569; font-size: 0.8rem; margin-top: 0.2rem;'>Digital Twin & Construction Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    projects = get_all_projects()
    if projects:
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #0891B2;'>Active Project</p>", unsafe_allow_html=True)
        proj_options = {p["name"]: p["id"] for p in projects}
        
        # Determine default index
        selected_name = st.selectbox(
            "Select Working Project:",
            options=list(proj_options.keys()),
            key="sb_project_select"
        )
        st.session_state.current_project_id = proj_options[selected_name]
        
        curr_p = get_project(st.session_state.current_project_id)
        if curr_p:
            st.info(f"📍 **{curr_p['location']}** | 📐 {curr_p['plot_area']} {curr_p['plot_unit']} | 💰 ${curr_p['budget']:,.0f}")
    else:
        st.warning("No saved projects found. Go to **02 Project Details** to create one.")
        
    st.divider()
    st.markdown("<p style='font-size: 0.75rem; color: #64748B; text-align: center;'>BuildVerse AI v1.0 • Modern Light Theme</p>", unsafe_allow_html=True)

# Landing Page Content if app.py run directly
st.markdown("""
<div class="header-banner">
    <h1>Welcome to BuildVerse AI</h1>
    <p>AI-Powered Digital Twin Platform for Architectural Planning, Scheduling, Site Monitoring & Executive Analytics.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="buildverse-card">
        <h3 style="color: #0891B2;">📐 Phase 1: AI House Planner</h3>
        <p style="color: #475569; font-size: 0.9rem;">Define plot boundaries and room dimensions. Generate 2D vector blueprints and interactive 3D house previews.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="buildverse-card">
        <h3 style="color: #0891B2;">📅 Phase 2: AI Construction Planner</h3>
        <p style="color: #475569; font-size: 0.9rem;">Automated 12-phase timeline scheduling, Gantt chart visualization, labor allocation, and material estimations.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="buildverse-card">
        <h3 style="color: #0891B2;">🔍 Phase 3: Site Monitoring & Twin</h3>
        <p style="color: #475569; font-size: 0.9rem;">Upload images, videos, and drone footage. AI vision evaluates progress, detects delays, and syncs the 3D Digital Twin.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 👈 Use the Sidebar Navigation to Access Platform Pages")
