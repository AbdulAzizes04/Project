"""
Chronological Transaction Timeline Dashboard Page for GuidedGuard.

Presents an interactive chronological timeline of customer transaction activity.
Social engineering scams (APP fraud) frequently manifest as sudden shifts in
activity along the customer timeline:
- Routine baseline transactions
- Sudden registration of a novel payee
- Rapid high-value outflows in quick succession
- Escalating risk scores

Provides multi-parameter filtering:
- Customer ID
- Risk Level (LOW, MEDIUM, HIGH, CRITICAL)
- Beneficiary ID
- Date / Time Range
"""

from typing import List, Dict, Any
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import config
from dashboard.components import render_header_status_bar, render_glass_card, render_risk_badge


def generate_sample_customer_timeline() -> pd.DataFrame:
    """
    Generate realistic chronological transaction sequence showing sudden scam pattern escalation.
    """
    base_time = datetime.datetime.now() - datetime.timedelta(days=2)
    
    events = [
        {"time": base_time + datetime.timedelta(hours=9, minutes=15), "customer": "C-ALICE-101", "payee": "M-GROCERY-01", "amount": 1200.0, "risk_score": 12, "risk_level": "LOW", "event": "Routine Grocery Transfer"},
        {"time": base_time + datetime.timedelta(hours=14, minutes=30), "customer": "C-ALICE-101", "payee": "M-COFFEE-04", "amount": 450.0, "risk_score": 8, "risk_level": "LOW", "event": "Routine Cafe Payment"},
        {"time": base_time + datetime.timedelta(days=1, hours=10, minutes=5), "customer": "C-ALICE-101", "payee": "BOB-FRIEND-202", "amount": 2500.0, "risk_score": 14, "risk_level": "LOW", "event": "Peer-to-Peer Transfer"},
        {"time": base_time + datetime.timedelta(days=1, hours=13, minutes=14), "customer": "C-ALICE-101", "payee": "MULE-BEN-888", "amount": 0.0, "risk_score": 35, "risk_level": "MEDIUM", "event": "New Beneficiary Added (Mule Account)"},
        {"time": base_time + datetime.timedelta(days=1, hours=13, minutes=16), "customer": "C-ALICE-101", "payee": "MULE-BEN-888", "amount": 75000.0, "risk_score": 78, "risk_level": "HIGH", "event": "Urgent Large Transfer via Proxy"},
        {"time": base_time + datetime.timedelta(days=1, hours=13, minutes=21), "customer": "C-ALICE-101", "payee": "MULE-BEN-888", "amount": 20000.0, "risk_score": 92, "risk_level": "CRITICAL", "event": "Follow-up Rapid Drain Transfer"},
        {"time": base_time + datetime.timedelta(days=1, hours=13, minutes=24), "customer": "C-ALICE-101", "payee": "MULE-BEN-888", "amount": 15000.0, "risk_score": 95, "risk_level": "CRITICAL", "event": "Follow-up Rapid Drain Transfer (Blocked)"},
    ]

    df = pd.DataFrame(events)
    df["time_str"] = df["time"].dt.strftime("%Y-%m-%d %H:%M")
    return df


def render_timeline_page():
    """
    Render chronological customer journey timeline view.
    """
    render_header_status_bar(
        page_title="Chronological Transaction Timeline",
        page_description="Trace sequential customer account activity and visualize the onset of scam-guided behavioral escalation.",
    )

    df_timeline = generate_sample_customer_timeline()

    # Incorporate any simulated transactions from active session state
    sim_history = st.session_state.get("simulation_history", [])
    if sim_history:
        extra_rows = []
        for s in sim_history:
            extra_rows.append({
                "time": datetime.datetime.now(),
                "customer": s.get("Customer_ID", "C-ALICE-101"),
                "payee": s.get("Beneficiary_ID", "SIMULATED-PAYEE"),
                "amount": float(s.get("Amount ($)", 5000.0)),
                "risk_score": int(s.get("Risk Score", 45)),
                "risk_level": str(s.get("Risk Level", "MEDIUM")),
                "event": f"Active Simulation ({s.get('Prediction', 'Analyzed')})",
                "time_str": str(s.get("Timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))),
            })
        if extra_rows:
            df_timeline = pd.concat([df_timeline, pd.DataFrame(extra_rows)], ignore_index=True)

    # 1. Timeline Filters
    st.markdown("### 🔍 Filter Timeline")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        customers = sorted(list(df_timeline["customer"].unique()))
        sel_cust = st.selectbox("Customer ID", ["ALL"] + customers)

    with f_col2:
        levels = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        sel_level = st.selectbox("Risk Level", levels)

    with f_col3:
        payees = sorted(list(df_timeline["payee"].unique()))
        sel_payee = st.selectbox("Beneficiary ID", ["ALL"] + payees)

    filtered_df = df_timeline.copy()
    if sel_cust != "ALL":
        filtered_df = filtered_df[filtered_df["customer"] == sel_cust]
    if sel_level != "ALL":
        filtered_df = filtered_df[filtered_df["risk_level"] == sel_level]
    if sel_payee != "ALL":
        filtered_df = filtered_df[filtered_df["payee"] == sel_payee]

    # 2. Plotly Interactive Scatter Timeline Chart
    st.markdown("### 📈 Chronological Risk Score Trajectory")

    color_map = {"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#F97316", "CRITICAL": "#EF4444"}

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_df["time_str"],
        y=filtered_df["risk_score"],
        mode="lines+markers",
        line=dict(color="#6366F1", width=2, dash="dot"),
        marker=dict(
            size=filtered_df["amount"].apply(lambda a: max(10, min(35, int(a / 3000)))),
            color=[color_map.get(lvl, "#6366F1") for lvl in filtered_df["risk_level"]],
            showscale=False,
            line=dict(width=2, color="#FFFFFF"),
        ),
        text=[f"Event: {r['event']}<br>Amount: ${r['amount']:,.2f}<br>Score: {r['risk_score']}" for _, r in filtered_df.iterrows()],
        hoverinfo="text",
        name="Risk Evolution",
    ))

    # Add threshold reference bands
    fig.add_hline(y=30, line_dash="dash", line_color="#10B981", annotation_text="Low Threshold (30)")
    fig.add_hline(y=60, line_dash="dash", line_color="#F59E0B", annotation_text="Medium Threshold (60)")
    fig.add_hline(y=80, line_dash="dash", line_color="#EF4444", annotation_text="Critical Threshold (80)")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(color="#E2E8F0"),
        height=380,
        margin=dict(l=40, r=40, t=30, b=40),
        yaxis=dict(title="Fused Risk Score (0-100)", range=[0, 105]),
        xaxis=dict(title="Chronological Timeline"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # 3. Interactive Chronological Event Cards
    st.markdown("### 📜 Event Sequence Details")

    for _, row in filtered_df.iterrows():
        lvl = row["risk_level"]
        c_hex = color_map.get(lvl, "#94A3B8")
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.6); border-left: 5px solid {c_hex}; border-radius: 8px; padding: 0.9rem 1.25rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-family: monospace;">⏱️ {row['time_str']}</span>
                    <span style="background: {c_hex}22; color: {c_hex}; border: 1px solid {c_hex}; padding: 0.2rem 0.6rem; border-radius: 9999px; font-weight: 600; font-size: 0.75rem;">
                        {lvl} ({row['risk_score']}/100)
                    </span>
                </div>
                <h5 style="color: #F8FAFC; margin: 0.35rem 0;">{row['event']}</h5>
                <div style="color: #94A3B8; font-size: 0.85rem;">
                    Customer: <span style="color: #38BDF8;">{row['customer']}</span> &nbsp;|&nbsp;
                    Payee: <span style="color: #38BDF8;">{row['payee']}</span> &nbsp;|&nbsp;
                    Amount: <span style="color: #F8FAFC; font-weight: 600;">${row['amount']:,.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
