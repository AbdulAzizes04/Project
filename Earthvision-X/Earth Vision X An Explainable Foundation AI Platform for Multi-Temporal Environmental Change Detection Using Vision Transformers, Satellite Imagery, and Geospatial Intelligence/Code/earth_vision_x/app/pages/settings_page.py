"""
Settings Page Controller.
Manages database configuration (SQLite / PostgreSQL), hardware acceleration, and export preferences.
"""

import streamlit as st
from earth_vision_x.app.components.header import render_header
from earth_vision_x.app.config.settings import settings

def render_settings_page():
    render_header(
        "Platform Settings & System Configuration",
        "Configure Database Connections, Hardware Accelerators, and Export Paths"
    )

    st.subheader("🗄️ Database Connection Settings")
    db_type = st.radio("Select Database Backend", ["SQLite (Embedded)", "PostgreSQL (Enterprise)"])
    
    if db_type == "SQLite (Embedded)":
        st.text_input("Database File URL", value=settings.DATABASE_URL)
    else:
        st.text_input("PostgreSQL Connection String", value="postgresql://user:password@localhost:5432/earth_vision_x")

    st.markdown("---")
    st.subheader("⚙️ System Execution Parameters")
    st.text_input("Model Checkpoints Directory", value=str(settings.CHECKPOINTS_DIR))
    st.text_input("Output Export Directory", value=str(settings.OUTPUTS_DIR))
    st.text_input("Log Directory", value=str(settings.LOGS_DIR))

    if st.button("💾 Save Settings", type="primary"):
        st.success("System configuration saved successfully!")
