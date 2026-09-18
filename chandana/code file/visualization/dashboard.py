import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from visualization.kpi import compute_kpis_from_df
from visualization.chart_selector import recommend_and_create_chart
from utils.dataframe_converter import convert_df_to_csv, convert_df_to_excel, convert_df_to_pdf

def render_kpi_cards(df: pd.DataFrame):
    """Renders modern glassmorphism KPI cards."""
    kpis = compute_kpis_from_df(df)
    if not kpis:
        return

    cols = st.columns(len(kpis))
    for i, kpi in enumerate(kpis):
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
                    text-align: center;
                    margin-bottom: 12px;
                ">
                    <p style="color: #94A3B8; font-size: 13px; margin: 0 0 4px 0; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{kpi['label']}</p>
                    <h3 style="color: #38BDF8; font-size: 24px; margin: 0 0 4px 0; font-weight: 700;">{kpi['value']}</h3>
                    <span style="color: #64748B; font-size: 11px;">{kpi['subtitle']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_visualization_section(df: pd.DataFrame):
    """Renders auto-recommended Plotly chart."""
    fig, chart_type = recommend_and_create_chart(df)
    if fig is not None:
        st.markdown(f"#### 📊 Interactive Visualization ({chart_type})")
        st.plotly_chart(fig, use_container_width=True)

def render_export_buttons(df: pd.DataFrame, query: str = ""):
    """Renders CSV, Excel, and PDF export buttons."""
    st.markdown("#### 📥 Export Query Results")
    col1, col2, col3 = st.columns(3)

    csv_data = convert_df_to_csv(df)
    excel_data = convert_df_to_excel(df)
    pdf_data = convert_df_to_pdf(df, query=query)

    with col1:
        st.download_button(
            label="📄 Export to CSV",
            data=csv_data,
            file_name="sql_result.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="📊 Export to Excel",
            data=excel_data,
            file_name="sql_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col3:
        st.download_button(
            label="📕 Export to PDF",
            data=pdf_data,
            file_name="sql_result_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

def render_styled_dataframe(df: pd.DataFrame):
    """
    Renders styled Streamlit Dataframe with:
    - Index column hidden (hide_index=True) to save horizontal space
    - Compact, balanced column width configuration
    - Currency and number formatting for metrics
    """
    if df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    col_configs = {}
    for i, col in enumerate(df.columns):
        if pd.api.types.is_numeric_dtype(df[col]):
            if any(kw in col.lower() for kw in ['sales', 'profit', 'revenue', 'price', 'cost', 'amount']):
                col_configs[col] = st.column_config.NumberColumn(format="$%.2f")
            elif pd.api.types.is_integer_dtype(df[col]):
                col_configs[col] = st.column_config.NumberColumn(format="%d")
            else:
                col_configs[col] = st.column_config.NumberColumn(format="%.2f")
        else:
            col_configs[col] = st.column_config.Column(width="medium" if i == 0 else "auto")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=col_configs
    )

