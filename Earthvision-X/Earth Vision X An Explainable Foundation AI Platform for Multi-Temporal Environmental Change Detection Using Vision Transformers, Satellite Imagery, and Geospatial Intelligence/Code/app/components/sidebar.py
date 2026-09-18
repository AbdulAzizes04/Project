"""
Enterprise Sidebar Navigation for EARTH VISION-X Dashboard.
Routes between the 9 core functional pages requested in the project specification.
"""

import streamlit as st

def render_sidebar() -> str:
    """
    Renders custom dark enterprise sidebar navigation menu.
    Returns selected page key.
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 12px 6px; margin-bottom: 12px; border-bottom: 1px solid rgba(56, 189, 248, 0.2);">
                <span style="font-size: 1.8rem;">🌍</span>
                <div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.01em;">EARTH VISION-X</div>
                    <div style="font-size: 0.68rem; color: #38BDF8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Explainable Multi-Temporal AI</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 8px;'>NAVIGATION WORKSPACE</div>", unsafe_allow_html=True)

        pages = [
            "📊 Dashboard Overview",
            "🛰️ Satellite Analysis (2016 ↔ 2026)",
            "🎛️ T1/T2 Comparison Slider",
            "🎯 Change Detection & Masks",
            "🌱 Spectral Analysis (NDVI / NDWI)",
            "🔬 Explainable AI (XAI Console)",
            "📈 Area Analytics & Statistics",
            "🧪 Model Evaluation & Experiments",
            "📄 Executive PDF Reports"
        ]

        selected = st.radio("Select View", pages, index=0, label_visibility="collapsed")

        # Telemetry & System Status
        st.markdown(
            """
            <div style="margin-top: 30px; background: rgba(15, 27, 51, 0.85); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span>🖥️ System Telemetry</span>
                    <span style="background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem;">READY</span>
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-bottom: 4px;">Sensor: <b>Sentinel-2 MSI Harmonized</b></div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-bottom: 4px;">Epochs: <b>2016 (T1) → 2026 (T2)</b></div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-bottom: 4px;">Backbone: <b>Siamese ViT-Base (86M)</b></div>
                <div style="font-size: 0.72rem; color: #94A3B8;">CRS: <b>EPSG:4326 | Res: 10m/px</b></div>
            </div>
            <div style="font-size: 0.68rem; color: #475569; text-align: center; margin-top: 14px; font-family: 'JetBrains Mono', monospace;">
                EARTH VISION-X v1.0.0-IEEE
            </div>
            """,
            unsafe_allow_html=True
        )

        route_map = {
            "📊 Dashboard Overview": "dashboard",
            "🛰️ Satellite Analysis (2016 ↔ 2026)": "satellite",
            "🎛️ T1/T2 Comparison Slider": "comparison",
            "🎯 Change Detection & Masks": "change_detection",
            "🌱 Spectral Analysis (NDVI / NDWI)": "spectral",
            "🔬 Explainable AI (XAI Console)": "xai",
            "📈 Area Analytics & Statistics": "analytics",
            "🧪 Model Evaluation & Experiments": "experiments",
            "📄 Executive PDF Reports": "reports"
        }

        return route_map.get(selected, "dashboard")
