"""
EARTH VISION-X: Primary Streamlit Enterprise Application Launcher.
Sub-title: Explainable Multi-Temporal Satellite Intelligence Platform for Environmental Change Detection

Launches the complete 9-page scientific and research-grade platform.
Can be executed with either:
    streamlit run streamlit_app.py
or:
    streamlit run app/dashboard.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Launch the unified dashboard router
import app.dashboard
