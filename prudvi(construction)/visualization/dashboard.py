"""
Dashboard UI widget generator for BuildVerse AI.
"""

import streamlit as st
from typing import Dict, Any

def render_kpi_card(title: str, value: str, subtitle: str = "", border_color: str = "#0891B2"):
    """Renders a clean white card metric box with cyan border."""
    st.markdown(f"""
    <div style="
        background-color: #FFFFFF;
        border-left: 5px solid {border_color};
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    ">
        <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform: uppercase;">{title}</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #0F172A; margin: 0.2rem 0;">{value}</div>
        <div style="font-size: 0.8rem; font-weight: 500; color: #0891B2;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
