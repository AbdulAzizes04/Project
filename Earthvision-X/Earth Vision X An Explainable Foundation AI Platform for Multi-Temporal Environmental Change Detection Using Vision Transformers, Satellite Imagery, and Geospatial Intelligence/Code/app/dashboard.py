"""
EARTH VISION-X: Primary Streamlit Enterprise Application Launcher.
Sub-title: Explainable Multi-Temporal Satellite Intelligence Platform for Environmental Change Detection

Can be launched via:
    streamlit run app/dashboard.py
or:
    python run.py --app
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="EARTH VISION-X | Satellite Intelligence Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

from app.ui.theme import inject_custom_css
from app.components.sidebar import render_sidebar
from src.pipeline import EarthVisionXPipeline

# Import Page Controllers with hot reloading
import importlib
import src.data.satellite_api
import src.pipeline
import app.pages.overview
import app.pages.satellite
import app.pages.comparison
import app.pages.change_detection
import app.pages.spectral
import app.pages.xai
import app.pages.analytics
import app.pages.experiments
import app.pages.reports

importlib.reload(src.data.satellite_api)
importlib.reload(src.pipeline)
importlib.reload(app.pages.overview)
importlib.reload(app.pages.satellite)

from app.pages.overview import render_dashboard_page
from app.pages.satellite import render_satellite_page
from app.pages.comparison import render_comparison_page
from app.pages.change_detection import render_change_detection_page
from app.pages.spectral import render_spectral_page
from app.pages.xai import render_xai_page
from app.pages.analytics import render_analytics_page
from app.pages.experiments import render_experiments_page
from app.pages.reports import render_reports_page

# Inject Global Enterprise Scientific CSS
inject_custom_css()

# Initialize Cached Pipeline
@st.cache_resource
def get_pipeline():
    return EarthVisionXPipeline(model_type="Siamese-ViT", device="auto")

pipeline = get_pipeline()
pipeline.data_service = src.data.satellite_api.SatelliteDataService()

# Render Sidebar Navigation
active_page = render_sidebar()

# Page Routing Controller
if active_page == "dashboard":
    render_dashboard_page(pipeline)
elif active_page == "satellite":
    render_satellite_page(pipeline)
elif active_page == "comparison":
    render_comparison_page(pipeline)
elif active_page == "change_detection":
    render_change_detection_page(pipeline)
elif active_page == "spectral":
    render_spectral_page(pipeline)
elif active_page == "xai":
    render_xai_page(pipeline)
elif active_page == "analytics":
    render_analytics_page(pipeline)
elif active_page == "experiments":
    render_experiments_page(pipeline)
elif active_page == "reports":
    render_reports_page(pipeline)
else:
    render_dashboard_page(pipeline)
