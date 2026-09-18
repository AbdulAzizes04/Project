"""
Shared Streamlit UI Components Library for GuidedGuard.

This module provides reusable dashboard elements: glassmorphic cards, metric displays,
risk status badges, header status bars, alert boxes, Plotly gauge/bar/pie/radar/donut charts,
report file downloaders, probability progress meters, and transaction timelines.

Responsibility:
- Render consistent top navigation status bars.
- Render styled metric cards and risk badges.
- Render custom Glassmorphism card containers.
- Render Plotly gauge, bar, pie, radar, and donut charts.
- Render transaction timeline steps and probability meters.
- Render report file download components.
"""

import streamlit as st
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
import plotly.express as px

import config
from models.model_loader import validate_artifacts


def render_header_status_bar(page_title: str, page_description: str):
    """
    Render top navigation header banner with title, timestamp, and model status indicator.

    Parameters:
        page_title (str): Title of the active page.
        page_description (str): Short description subtitle.
    """
    artifacts_status = validate_artifacts()
    is_ready = artifacts_status.get("ready_for_inference", False)
    model_name = artifacts_status.get("model_name", "Gradient Boosting")

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_html = f"""
    <div class="guided-header">
        <div>
            <h2 style="margin: 0; padding: 0; color: #F8FAFC;">{page_title}</h2>
            <p style="margin: 0.25rem 0 0 0; color: #94A3B8; font-size: 0.9rem;">{page_description}</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.8rem; color: #94A3B8;">🕒 {current_time}</div>
            <div style="margin-top: 0.3rem;">
                <span class="status-badge {'status-badge-low' if is_ready else 'status-badge-medium'}">
                    {'🟢 Model Online: ' + model_name if is_ready else '🟡 Model Offline'}
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(status_html, unsafe_allow_html=True)


def render_risk_badge(risk_level: str) -> str:
    """
    Generate HTML markup for a risk level status badge.

    Parameters:
        risk_level (str): "LOW", "MEDIUM", "HIGH", or "CRITICAL".

    Returns:
        str: Badge HTML string.
    """
    level_lower = risk_level.lower()
    return f'<span class="status-badge status-badge-{level_lower}">{risk_level.upper()} RISK</span>'


def render_glass_card(title: str, content_markdown: str):
    """
    Render a styled Glassmorphism container card.

    Parameters:
        title (str): Card title.
        content_markdown (str): Body content inside the card.
    """
    st.markdown(
        f"""
        <div class="guided-card">
            <h4 style="margin-top: 0; color: #38BDF8;">{title}</h4>
            <div style="color: #E2E8F0;">{content_markdown}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gauge_chart(title: str, val: float, max_val: float = 100.0) -> go.Figure:
    """
    Render Plotly indicator gauge chart.

    Parameters:
        title (str): Chart title.
        val (float): Current value (e.g. 100.0).
        max_val (float): Maximum scale value.

    Returns:
        go.Figure: Plotly figure object.
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": "%", "font": {"color": "#38BDF8", "size": 36}},
            title={"text": title, "font": {"color": "#F8FAFC", "size": 16}},
            gauge={
                "axis": {"range": [0, max_val], "tickwidth": 1, "tickcolor": "#64748B"},
                "bar": {"color": "#6366F1"},
                "bgcolor": "#1E293B",
                "borderwidth": 1,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, max_val * 0.5], "color": "rgba(34, 197, 94, 0.2)"},
                    {"range": [max_val * 0.5, max_val * 0.8], "color": "rgba(234, 179, 8, 0.2)"},
                    {"range": [max_val * 0.8, max_val], "color": "rgba(239, 68, 68, 0.2)"},
                ],
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def render_metrics_bar_chart(metrics_dict: Dict[str, float]) -> go.Figure:
    """
    Render Plotly horizontal bar chart of evaluation metrics.

    Parameters:
        metrics_dict (Dict[str, float]): Dictionary of metric names and scores.

    Returns:
        go.Figure: Plotly figure object.
    """
    names = list(metrics_dict.keys())
    scores = [float(v) * 100.0 if float(v) <= 1.0 else float(v) for v in metrics_dict.values()]

    fig = go.Figure(
        go.Bar(
            x=scores,
            y=names,
            orientation="h",
            marker=dict(color="#38BDF8", line=dict(color="#6366F1", width=1.5)),
            text=[f"{s:.2f}%" for s in scores],
            textposition="inside",
        )
    )
    fig.update_layout(
        title="Model Performance Metrics Overview",
        title_font=dict(color="#F8FAFC", size=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 105], title="Score (%)", color="#94A3B8", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(color="#F8FAFC", autorange="reversed"),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def render_completion_pie_chart(module_status: Dict[str, str]) -> go.Figure:
    """
    Render Plotly donut chart showing project module completion status.

    Parameters:
        module_status (Dict[str, str]): Dictionary of module names and status string.

    Returns:
        go.Figure: Plotly figure object.
    """
    ready_count = sum(1 for v in module_status.values() if v.lower() == "ready")
    total_count = len(module_status)

    labels = ["Completed Modules", "Remaining"]
    values = [ready_count, total_count - ready_count]
    colors = ["#22C55E", "#334155"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors),
                textinfo="label+percent",
                insidetextfont=dict(color="#FFFFFF"),
            )
        ]
    )
    fig.update_layout(
        title="System Architecture Completion Rate",
        title_font=dict(color="#F8FAFC", size=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=220,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def render_radar_chart(metrics_dict: Dict[str, float]) -> go.Figure:
    """
    Render Plotly Radar / Spider Chart for model evaluation metrics.

    Parameters:
        metrics_dict (Dict[str, float]): Metric names and float values (0.0 to 1.0).

    Returns:
        go.Figure: Plotly figure handle.
    """
    categories = list(metrics_dict.keys())
    values = [float(v) * 100.0 if float(v) <= 1.0 else float(v) for v in metrics_dict.values()]
    
    # Close polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.3)",
            line=dict(color="#6366F1", width=2),
            name="Gradient Boosting",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(color="#F8FAFC"),
            bgcolor="rgba(30, 41, 59, 0.5)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title="Model Performance Radar Overview",
        title_font=dict(color="#F8FAFC", size=16),
        height=320,
        margin=dict(l=40, r=40, t=50, b=30),
    )
    return fig


def render_risk_donut_chart(risk_counts: Dict[str, int]) -> go.Figure:
    """
    Render Plotly Donut Chart for risk level categories.

    Parameters:
        risk_counts (Dict[str, int]): Dictionary of risk levels and item counts.

    Returns:
        go.Figure: Plotly figure handle.
    """
    labels = list(risk_counts.keys())
    values = list(risk_counts.values())
    colors = ["#22C55E", "#FACC15", "#FB923C", "#EF4444"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(colors=colors),
                textinfo="label+value",
                insidetextfont=dict(color="#FFFFFF"),
            )
        ]
    )
    fig.update_layout(
        title="Risk Level Category Breakdown",
        title_font=dict(color="#F8FAFC", size=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#F8FAFC")),
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def render_timeline_steps(current_step: int = 6):
    """
    Render transaction execution timeline HTML widget.

    Parameters:
        current_step (int): Step completion index (1 to 6).
    """
    steps = [
        "1. Transaction Submitted",
        "2. Schema Validated",
        "3. Feature Matrix Prepared",
        "4. ML Inference Prediction",
        "5. Risk Score Engine",
        "6. XAI Analysis Complete",
    ]

    html_steps = []
    for idx, s in enumerate(steps, 1):
        is_done = idx <= current_step
        color = "#4ADE80" if is_done else "#64748B"
        icon = "✓" if is_done else "○"
        html_steps.append(
            f'<div style="color: {color}; font-size: 0.85rem; font-weight: 600;">{icon} {s}</div>'
        )

    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
            <h5 style="margin-top: 0; color: #38BDF8;">⏱️ Transaction Execution Timeline</h5>
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
                {''.join(html_steps)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_footer():
    """
    Render version, developer credits, and system info in the sidebar footer.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.75rem; color: #64748B; text-align: center;">
            <p style="margin: 0;"><b>{config.PROJECT_NAME}</b></p>
            <p style="margin: 2px 0;">Version {config.VERSION}</p>
            <p style="margin: 2px 0;">Developer: <b>GuidedGuard AI Lab</b></p>
            <p style="margin: 4px 0 0 0; font-style: italic;">Explainable Scam Detection System</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_banking_recommendation_card(rec_obj: Dict[str, Any]):
    """Render commercial banking recommendation card with actionable directives."""
    action = rec_obj.get("action", "Approve")
    recommendation = rec_obj.get("recommendation", "Approve Transaction")
    color = rec_obj.get("color", "#28a745")
    details = rec_obj.get("details", "")
    workflow = rec_obj.get("workflow_step", "Standard Queue")

    actions_list = []
    if action in ["Freeze Transaction", "Hold Transaction"]:
        actions_list = ["❄️ Freeze Transaction", "📱 Notify Customer via SMS/Email", "🆔 Require KYC/OTP Verification", "🚨 Escalate to Fraud Operations Team"]
    elif action == "OTP Verification":
        actions_list = ["🔐 Send 2FA/OTP Verification Code", "⌛ Pause Settlement for 15 Minutes", "📊 Monitor Subsequent Velocity"]
    else:
        actions_list = ["✅ Approve Transaction for Instant Settlement", "📜 Record Audit Log"]

    actions_html = "".join([f"<li style='color: #F8FAFC; margin-bottom: 2px;'>{act}</li>" for act in actions_list])

    st.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 2px solid {color}; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; color: {color}; font-weight: 700;">🏛️ Banking Recommendation: {action.upper()}</h3>
                <span class="status-badge" style="background-color: {color}; color: #FFFFFF; font-weight: 700;">{workflow}</span>
            </div>
            <p style="margin: 8px 0 4px 0; color: #F8FAFC; font-size: 1.05rem; font-weight: 600;">{recommendation}</p>
            <p style="margin: 0 0 10px 0; color: #94A3B8; font-size: 0.9rem;">{details}</p>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; margin-top: 8px;">
                <strong style="color: #38BDF8; font-size: 0.9rem;">Recommended Actions:</strong>
                <ul style="margin: 4px 0 0 0; padding-left: 20px; font-size: 0.88rem;">
                    {actions_html}
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_score_breakdown_panel(risk_bd: Dict[str, Any]):
    """Render Risk Score Breakdown Panel showing composite sub-scores."""
    st.markdown("#### ⚖️ Composite Risk Score Breakdown Index")
    
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.metric("ML Model Probability", f"{risk_bd.get('model_probability', 0):.2f}%", f"{risk_bd.get('model_probability_score', 0):.1f} pts (70% Wt)")
    with b2:
        st.metric("Amount Risk Score", f"{risk_bd.get('amount_risk', 0):.1f} pts")
    with b3:
        st.metric("Velocity Risk Score", f"{risk_bd.get('velocity_risk', 0):.1f} pts")
    with b4:
        st.metric("Device Risk Score", f"{risk_bd.get('device_risk', 0):.1f} pts")

    b5, b6, b7, b8 = st.columns(4)
    with b5:
        st.metric("Location Risk Score", f"{risk_bd.get('location_risk', 0):.1f} pts")
    with b6:
        st.metric("Beneficiary Risk Score", f"{risk_bd.get('beneficiary_risk', 0):.1f} pts")
    with b7:
        st.metric("Historical Behaviour", f"{risk_bd.get('historical_behaviour', 0):.1f} pts")
    with b8:
        st.metric("Balance Behaviour", f"{risk_bd.get('balance_behaviour', 0):.1f} pts")


def render_timing_breakdown_panel(timing_bd: Dict[str, Any]):
    """Render microsecond execution stage latency timing metrics."""
    st.markdown("#### ⏱️ Detailed Microsecond Latency Stage Timing")
    t1, t2, t3, t4, t5, t6 = st.columns(6)

    with t1:
        st.metric("Feature Eng.", f"{timing_bd.get('feature_engineering', 0):.2f} ms")
    with t2:
        st.metric("Prediction", f"{timing_bd.get('prediction', 0):.2f} ms")
    with t3:
        st.metric("SHAP Engine", f"{timing_bd.get('shap', 0):.2f} ms")
    with t4:
        st.metric("LIME Engine", f"{timing_bd.get('lime', 0):.2f} ms")
    with t5:
        st.metric("Rendering", f"{timing_bd.get('rendering', 0):.2f} ms")
    with t6:
        st.metric("TOTAL LATENCY", f"{timing_bd.get('total', 0):.2f} ms")

