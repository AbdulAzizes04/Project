"""
Progress Graph module for generating S-Curve comparison charts (Planned vs Actual progress).
"""

import plotly.graph_objects as go
from typing import List, Dict, Any

def create_s_curve_graph(planned_curve: List[float], actual_curve: List[float], dates: List[str]) -> go.Figure:
    """Generates Planned vs Actual S-Curve progress line chart."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=planned_curve,
        mode='lines+markers',
        name='Planned Target %',
        line=dict(color='#0891B2', width=3, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=actual_curve,
        mode='lines+markers',
        name='Actual Site Progress %',
        line=dict(color='#06B6D4', width=4),
        fill='tozeroy',
        fillcolor='rgba(224, 242, 254, 0.4)'
    ))
    
    fig.update_layout(
        title="Construction Progress S-Curve (Planned Target vs Actual Site Progress)",
        xaxis=dict(title="Timeline Date", gridcolor="#E2E8F0"),
        yaxis=dict(title="Progress Percentage (%)", range=[0, 105], gridcolor="#E2E8F0"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )
    
    return fig
