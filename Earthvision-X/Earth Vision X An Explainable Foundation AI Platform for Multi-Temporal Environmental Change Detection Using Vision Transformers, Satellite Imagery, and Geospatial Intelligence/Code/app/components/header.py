"""
Enterprise Header & Metric Component for EARTH VISION-X.
"""

import streamlit as st
from typing import Optional

def render_header(
    title: str = "EARTH VISION-X",
    subtitle: str = "Explainable Multi-Temporal Satellite Intelligence Platform",
    active_model: str = "Siamese ViT-Base",
    status_label: str = "ONLINE (T1: 2016 ↔ T2: 2026)"
):
    """Renders sleek, unified top enterprise navbar."""
    st.markdown(
        f"""
        <div class="evx-header">
            <div>
                <div class="evx-header-title">
                    <span>🌍</span> {title}
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 2px;">
                    {subtitle}
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="evx-header-badge">MODEL: {active_model}</span>
                <span class="status-badge"><span class="status-dot"></span>{status_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    theme: str = "cyan" # cyan, emerald, crimson, amber
):
    """Renders high-contrast, scientific metric tile."""
    css_cls = f"metric-tile {theme}"
    st.markdown(
        f"""
        <div class="{css_cls}">
            <div class="metric-title">{title}</div>
            <div class="metric-val">{value}</div>
            <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
