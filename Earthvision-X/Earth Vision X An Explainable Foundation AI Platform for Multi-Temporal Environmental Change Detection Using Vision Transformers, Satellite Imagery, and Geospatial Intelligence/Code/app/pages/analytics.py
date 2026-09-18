"""
Area Analytics & Statistical Quantification Page for EARTH VISION-X.
Implements Section 20:
- Total AOI Area, Changed Area, Unchanged Area, Change Percentage
- Category-level breakdown (pixels, km², %, confidence)
- Interactive Plotly distribution diagrams
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.components.header import render_header, render_metric_card

def render_analytics_page(pipeline):
    """Renders Area Analytics & Statistics Page."""
    render_header(
        title="Spatial Area Analytics & Land Dynamics",
        subtitle="Quantitative Land-Cover Area Quantification, Flux Ratios, and Categorical Distributions",
        active_model="Geospatial Quantification",
        status_label="Analytics Active"
    )

    if "current_analysis" not in st.session_state:
        st.session_state["current_analysis"] = pipeline.run_pipeline()

    res = st.session_state["current_analysis"]
    area_m = res["area_metrics"]

    # Top KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Total AOI Area", f"{area_m['total_area_km2']:.2f} km²", f"{area_m['total_pixels']:,} Pixels (10m)", "cyan")
    with k2:
        render_metric_card("Changed Area", f"{area_m['changed_area_km2']:.2f} km²", f"{area_m['change_percentage']:.2f}% of Total AOI", "crimson")
    with k3:
        render_metric_card("Unchanged Area", f"{area_m['unchanged_area_km2']:.2f} km²", f"{100 - area_m['change_percentage']:.2f}% Stable", "emerald")
    with k4:
        render_metric_card("Primary Transformation", area_m["primary_change"], f"{area_m['confidence_percentage']:.1f}% Confidence", "amber")

    st.markdown("---")

    # Interactive Plots
    c_pie, c_bar = st.columns(2, gap="medium")

    df_cats = pd.DataFrame(area_m["category_breakdown"])

    with c_pie:
        st.markdown("##### 🥧 Land Cover Transformation Distribution")
        fig_pie = px.pie(
            df_cats,
            names="category",
            values="affected_area_km2",
            color="category",
            color_discrete_sequence=["#1E293B", "#EF4444", "#F97316", "#3B82F6", "#10B981"],
            hole=0.4
        )
        fig_pie.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=320
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c_bar:
        st.markdown("##### 📊 Affected Area by Category (km²)")
        fig_bar = px.bar(
            df_cats[df_cats["category"] != "No Change"],
            x="category",
            y="affected_area_km2",
            color="category",
            color_discrete_sequence=["#EF4444", "#F97316", "#3B82F6", "#10B981"],
            text="affected_area_km2"
        )
        fig_bar.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            height=320
        )
        fig_bar.update_traces(texttemplate='%{text:.2f} km²', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Detailed Table from Section 20
    st.markdown("### 📋 Quantitative Spatial Area Breakdown Table")
    df_disp = df_cats.copy()
    df_disp.columns = ["Category", "Affected Pixels", "Affected Area (km²)", "Ratio (%)", "Confidence (%)"]
    st.dataframe(df_disp.set_index("Category"), use_container_width=True)
