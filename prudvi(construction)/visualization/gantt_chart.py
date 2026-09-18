"""
Interactive Plotly Gantt Chart generator for construction phases.
"""

import plotly.express as px
import pandas as pd
from typing import List, Dict, Any

def create_gantt_chart(schedules: List[Dict[str, Any]]) -> px.timeline:
    """Generates an interactive Plotly Gantt chart for construction phases."""
    if not schedules:
        return None
        
    df_data = []
    for s in schedules:
        df_data.append({
            "Phase": s.get("phase_name", "Phase"),
            "Start": s.get("start_date", "2026-01-01"),
            "End": s.get("end_date", "2026-01-15"),
            "Duration (Days)": s.get("duration_days", 14),
            "Progress %": s.get("progress_pct", 0.0),
            "Cost": f"${s.get('cost', 0):,.0f}",
            "Status": s.get("status", "Pending")
        })
        
    df = pd.DataFrame(df_data)
    
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Phase",
        color="Progress %",
        color_continuous_scale=["#E0F2FE", "#06B6D4", "#0891B2"],
        hover_data=["Duration (Days)", "Cost", "Status"],
        title="Interactive Construction Gantt Chart & Phase Schedule"
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="Inter"),
        xaxis=dict(gridcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#E2E8F0"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=450
    )
    
    return fig
