"""
Unified API Routes handler for BuildVerse AI.
"""

from api.planner_api import process_floor_plan_request
from api.monitoring_api import process_monitoring_upload
from api.report_api import generate_pdf_report

class BuildVerseAPI:
    @staticmethod
    def generate_floor_plan(plot_area, rooms):
        return process_floor_plan_request(plot_area, rooms)
        
    @staticmethod
    def analyze_monitoring_media(path, mtype, planned_pct, phase):
        return process_monitoring_upload(path, mtype, planned_pct, phase)
        
    @staticmethod
    def export_pdf_report(project, log=None):
        return generate_pdf_report(project, log)
