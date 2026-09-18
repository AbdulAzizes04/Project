"""
Cyan-themed Plotly charts for BuildVerse AI.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any

CYAN_PRIMARY = "#0891B2"
CYAN_SECONDARY = "#06B6D4"
SEMI_CYAN = "#E0F2FE"

def create_progress_gauge(value: float, title: str = "Overall Construction %") -> go.Figure:
    """Creates a sleek cyan progress gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': '#0F172A', 'family': 'Inter'}},
        number={'suffix': '%', 'font': {'size': 36, 'color': '#0891B2', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
            'bar': {'color': CYAN_PRIMARY},
            'bgcolor': "#FFFFFF",
            'borderwidth': 2,
            'bordercolor': "#BAE6FD",
            'steps': [
                {'range': [0, value], 'color': SEMI_CYAN},
                {'range': [value, 100], 'color': "#F8FAFC"}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        height=220
    )
    return fig

def create_budget_donut_chart(schedules: List[Dict[str, Any]]) -> go.Figure:
    """Creates a budget allocation donut chart across construction phases."""
    labels = [s.get("phase_name", "Phase") for s in schedules]
    values = [s.get("cost", 1000) for s in schedules]
    
    colors = ["#0891B2", "#0284C7", "#0369A1", "#075985", "#0D9488", "#14B8A6", "#06B6D4", "#38BDF8", "#7DD3FC", "#22D3EE", "#67E8F9", "#A5F3FC"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.45,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2))
    )])
    
    fig.update_layout(
        title="Phase Budget Distribution",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="Inter"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=320
    )
    return fig
