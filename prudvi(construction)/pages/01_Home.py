"""
BuildVerse AI — Home Page
"""

import streamlit as st
from config import ASSETS_DIR

st.set_page_config(
    page_title="Home — BuildVerse AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>🏗️ BuildVerse AI — Platform Overview</h1>
    <p>End-to-End AI Architectural & Intelligent Construction Management Engine</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Platform Architectural Workflow")

st.markdown("""
```
 ┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
 │ 1. Project & Rooms Setup│ ───► │ 2. AI 2D/3D Floor Plan  │ ───► │ 3. AI Construction Plan │
 └────────────────────────┘      └────────────────────────┘      └────────────────────────┘
                                                                             │
 ┌────────────────────────┐      ┌────────────────────────┐                  ▼
 │ 6. PDF Report & Dash   │ ◄─── │ 5. 3D Digital Twin Sync │ ◄─── ┌────────────────────────┐
 └────────────────────────┘      └────────────────────────┘      │ 4. Daily Media Monitor │
                                                                 └────────────────────────┘
```
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="buildverse-card-accent">
        <h4 style="color: #0891B2;">✨ Key Capabilities</h4>
        <ul style="color: #0F172A; font-size: 0.9rem; line-height: 1.6;">
            <li><b>Automated 2D Blueprint Layouts:</b> Wall thickness, door arc swings, window slots, room area tags.</li>
            <li><b>Interactive 3D House Preview:</b> Multi-floor mesh visualization with dimension limits.</li>
            <li><b>Phase Scheduler Engine:</b> 12-stage construction breakdown with critical path Gantt charts.</li>
            <li><b>Material & Labor Calculator:</b> Estimates cement, steel, bricks, sand, paint, and trade labor.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="buildverse-card-accent">
        <h4 style="color: #0891B2;">🤖 AI Computer Vision & Digital Twin</h4>
        <ul style="color: #0F172A; font-size: 0.9rem; line-height: 1.6;">
            <li><b>Daily Media Inspection:</b> Analyze site photos, video frame captures, and drone footage.</li>
            <li><b>Deviation & Delay Detection:</b> Calculates planned vs actual completion % and delay days.</li>
            <li><b>Recovery Plan Advice:</b> AI-generated worker reallocation and material suggestions.</li>
            <li><b>Real-Time Digital Twin:</b> Live 3D model status updates synced with site inspection logs.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
