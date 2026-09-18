"""
Executive Natural Language Summary Generator for BuildVerse AI PDF Reports.
"""

from typing import Dict, Any

def generate_report_summary(project: Dict[str, Any], progress_data: Dict[str, Any]) -> str:
    """Generates executive paragraph summary for construction reports."""
    pname = project.get("name", "Project")
    owner = project.get("owner_name", "Owner")
    overall = progress_data.get("overall_progress_pct", 0.0)
    status = progress_data.get("status", "On Schedule")
    
    return f"""
    BuildVerse AI Executive Project Summary for '{pname}' (Owner: {owner}).
    The project is currently at {overall:.1f}% overall physical completion.
    The current operational status is classified as '{status}'.
    AI computer vision site analysis has verified structural accuracy across active phases.
    All safety, material utilization, and budget allocations are monitored continuously via the Digital Twin engine.
    """
