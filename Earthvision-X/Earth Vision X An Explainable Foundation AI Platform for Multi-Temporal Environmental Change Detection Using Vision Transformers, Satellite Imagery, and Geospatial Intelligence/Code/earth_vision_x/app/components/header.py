"""
Header and Metric Card Enterprise UI Components for EARTH VISION-X Dashboard.
"""

import streamlit as st

def render_header(title: str = "Change Detection & Explainability Studio", active_model: str = "Swin Transformer v2 (Swin-CD)", confidence: str = "94.8%"):
    st.markdown(
        f"""
        <div class="top-header-bar">
            <div class="header-logo-group">
                <span style="font-size: 1.6rem;">🌍</span>
                <div>
                    <div class="header-title-text">{title}</div>
                </div>
            </div>
            <div class="header-right-group">
                <div class="model-badge">
                    <span>⚡ Model:</span>
                    <span>{active_model}</span>
                </div>
                <div class="confidence-badge">
                    <span>🎯 {confidence}</span>
                </div>
                <div style="cursor: pointer; font-size: 1.1rem; color: #94A3B8;">🔔</div>
                <div class="user-avatar">AI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric_card(title: str, value: str, subtext: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {f'<div class="kpi-sub">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

