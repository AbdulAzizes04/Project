"""
Dashboard Package.

Contains UI component libraries, page view handlers, and navigation routers for GuidedGuard.
"""

from dashboard.overview import render_overview_page
from dashboard.simulator import render_simulator_page
from dashboard.scenario_simulator import render_scenario_simulator_page
from dashboard.timeline import render_timeline_page
from dashboard.investigation import render_investigation_page
from dashboard.xai import render_xai_page
from dashboard.analytics import render_analytics_page
from dashboard.batch_prediction import render_batch_prediction_page
from dashboard.model_monitoring import render_model_monitoring_page
from dashboard.datasets import render_datasets_page
from dashboard.history import render_history_page
from dashboard.settings import render_settings_page
from dashboard.about import render_about_page

__all__ = [
    "render_overview_page",
    "render_simulator_page",
    "render_scenario_simulator_page",
    "render_timeline_page",
    "render_investigation_page",
    "render_xai_page",
    "render_analytics_page",
    "render_batch_prediction_page",
    "render_model_monitoring_page",
    "render_datasets_page",
    "render_history_page",
    "render_settings_page",
    "render_about_page",
]
