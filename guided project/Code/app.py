"""
GuidedGuard Streamlit Application Main Entry Point.

This module sets up the page configuration, dark CSS theme injection, top navigation status bar,
collapsible sidebar navigation, dynamic page routing system, and developer footer.

Features:
- Configure Streamlit wide layout and metadata.
- Load custom dark theme design system (`assets/style.css`).
- Route between 13 modular dashboard views including Viva demo scenarios, forensic investigation, and drift monitoring.
- Display system model status and error fallbacks.
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

import config
from dashboard.components import render_sidebar_footer
from dashboard import (
    render_overview_page,
    render_simulator_page,
    render_scenario_simulator_page,
    render_timeline_page,
    render_investigation_page,
    render_xai_page,
    render_analytics_page,
    render_batch_prediction_page,
    render_model_monitoring_page,
    render_datasets_page,
    render_history_page,
    render_settings_page,
    render_about_page,
)

# 1. Page Configuration
st.set_page_config(
    page_title=f"{config.PROJECT_NAME} – XAI Digital Payment Scam Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Essential Session State Variables
if "simulation_history" not in st.session_state:
    st.session_state["simulation_history"] = []
if "risk_thresholds" not in st.session_state:
    st.session_state["risk_thresholds"] = config.RISK_LEVEL_THRESHOLDS.copy()
if "compact_mode" not in st.session_state:
    st.session_state["compact_mode"] = False
if "contrast_mode" not in st.session_state:
    st.session_state["contrast_mode"] = False


# 2. Inject Custom CSS Theme
def load_css(css_path: Path = config.ASSETS_DIR / "style.css"):
    """
    Inject custom dark CSS stylesheet.
    """
    css_path = Path(css_path)
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


load_css()

# 3. Sidebar Navigation Header
st.sidebar.markdown(
    """
    <div style="text-align: center; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 0.8rem;">
        <h2 style="margin: 0; color: #6366F1; font-weight: 700; letter-spacing: 0.5px;">🛡️ GuidedGuard</h2>
        <p style="margin: 3px 0 0 0; color: #38BDF8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
            Explainable APP Scam Detection
        </p>
        <div style="margin-top: 6px;">
            <span style="background: rgba(99, 102, 241, 0.2); color: #818CF8; padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600; border: 1px solid rgba(99, 102, 241, 0.3);">
                Dual ML & Anomaly
            </span>
            <span style="background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.3);">
                Zero Leakage
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Sidebar Page Selection Router (Categorized)
NAV_OPTIONS = {
    # Core Operations
    "🏠 Dashboard Overview": render_overview_page,
    "💳 Payment Simulator": render_simulator_page,
    "🎭 Scam Scenarios (Viva Demos)": render_scenario_simulator_page,
    "⏱️ Transaction Timeline": render_timeline_page,
    "🔍 Forensic Investigation": render_investigation_page,
    # Explainability & Analytics
    "💡 Explainable AI (XAI)": render_xai_page,
    "📊 Benchmark & Analytics": render_analytics_page,
    "📈 Model & Drift Monitoring": render_model_monitoring_page,
    # Data & Operations
    "📁 Batch Prediction": render_batch_prediction_page,
    "🗄️ Datasets & Provenance": render_datasets_page,
    "📜 Prediction History & Audit": render_history_page,
    # System & Docs
    "⚙️ System Settings": render_settings_page,
    "ℹ️ Documentation & About": render_about_page,
}

selected_page = st.sidebar.radio("Navigation", list(NAV_OPTIONS.keys()), label_visibility="collapsed")

# Render Sidebar Developer Footer
render_sidebar_footer()

# 5. Dynamic Page Router Execution
import traceback

try:
    page_func = NAV_OPTIONS.get(selected_page, render_overview_page)
    page_func()
except Exception as e:
    st.error(f"❌ Error encountered while rendering view '{selected_page}': {e}")
    
    with st.expander("🔍 View Complete Stack Trace & Technical Details", expanded=True):
        st.code(traceback.format_exc(), language="python")

    st.info("💡 **Suggested Fix**: Verify input payload values, ensure model/scaler artifacts are present in `models/`, or click Retry below.")
    if st.button("🔄 Retry View"):
        st.rerun()
