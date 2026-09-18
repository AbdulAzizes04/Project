import streamlit as st
import os
import pandas as pd
import io

# Page configuration
st.set_page_config(
    page_title="AI SQL Assistant - Autonomous Data Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS stylesheet
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Imports from modular packages
from utils.logger import logger
from utils.csv_reader import load_csv_data
from utils.excel_reader import load_excel_data, get_excel_sheets
from database.create_database import ingest_dataframe_to_sqlite
from database.sqlite_db import db_manager
from ai.schema_reader import get_table_metadata, generate_suggested_questions
from ai.sql_generator import generate_sql_query
from ai.sql_validator import validate_sql_query
from ai.explanation import generate_plain_english_explanation
from sql.executor import execute_sql_query
from sql.formatter import format_sql_query
from sql.optimizer import analyze_sql_optimization
from visualization.dashboard import render_kpi_cards, render_visualization_section, render_export_buttons, render_styled_dataframe

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_table" not in st.session_state:
    st.session_state.active_table = None
if "active_columns" not in st.session_state:
    st.session_state.active_columns = []
if "active_df" not in st.session_state:
    st.session_state.active_df = None

# Sidebar - Dataset Upload & Configuration
with st.sidebar:
    # Read API Key quietly from environment if present, without displaying input controls
    provider_key = "gemini"
    api_key_input = os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    st.markdown("## 📁 Dataset Ingestion")
    
    # Pre-loaded Preset Datasets
    data_source = st.radio(
        "Choose Data Input",
        options=["Upload File (CSV / XLSX)", "Use Preset Sample Dataset"]
    )
    
    df = None
    table_name = "dataset"

    if data_source == "Use Preset Sample Dataset":
        preset_choice = st.selectbox(
            "Select Sample Dataset",
            options=["E-Commerce Orders (CSV)", "Store Sales Performance (Excel)"]
        )
        if preset_choice == "E-Commerce Orders (CSV)":
            sample_path = os.path.join(os.path.dirname(__file__), "uploads", "sample.csv")
            if os.path.exists(sample_path):
                df, table_name = load_csv_data(sample_path)
                table_name = "sample_ecommerce_orders"
        else:
            sample_path = os.path.join(os.path.dirname(__file__), "uploads", "sales.xlsx")
            if os.path.exists(sample_path):
                df, table_name = load_excel_data(sample_path)
                table_name = "sample_store_sales"

    else:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel dataset",
            type=["csv", "xlsx", "xls"],
            help="Files will be parsed automatically and stored in SQLite database."
        )

        if uploaded_file is not None:
            filename = uploaded_file.name.lower()
            try:
                if filename.endswith(".csv"):
                    df, table_name = load_csv_data(uploaded_file)
                else:
                    sheets = get_excel_sheets(uploaded_file)
                    selected_sheet = st.selectbox("Select Excel Sheet", options=sheets) if len(sheets) > 1 else 0
                    df, table_name = load_excel_data(uploaded_file, sheet_name=selected_sheet)
            except Exception as e:
                st.error(f"Error loading file: {e}")

    # Process and ingest into SQLite
    if df is not None:
        table_name, columns, dtypes = ingest_dataframe_to_sqlite(df, table_name=table_name)
        if st.session_state.active_table != table_name:
            st.session_state.messages = []  # Clear previous chat history for new dataset
        st.session_state.active_table = table_name
        st.session_state.active_columns = columns
        st.session_state.active_df = df
        st.success(f"✓ Ingested `{len(df):,}` rows into table `{table_name}`")

    # Active Database Inspector
    if st.session_state.active_table:
        st.markdown("---")
        st.markdown("### 🔍 Database Schema Inspector")
        meta = get_table_metadata(st.session_state.active_table)
        st.info(f"**Table:** `{meta['table_name']}`\n\n**Rows:** {meta['row_count']:,} | **Columns:** {meta['column_count']}")
        
        with st.expander("View Columns & Data Types"):
            for col, dt in meta['dtypes'].items():
                st.text(f"• {col}: {dt}")

# Main Header Banner
st.markdown(
    """
    <div class="main-header">
        <h1 style="margin: 0; color: #F8FAFC; font-size: 28px; font-weight: 700;">
            ⚡ AI SQL Assistant & Analytics Dashboard
        </h1>
        <p style="margin: 6px 0 0 0; color: #94A3B8; font-size: 14px;">
            Ask questions in Plain English -> Auto-generate SQL -> Instant Plotly Visualizations & Exportable Reports.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if not st.session_state.active_table:
    st.info("👈 Please select a preset sample dataset or upload a CSV/Excel file in the sidebar to get started.")
    st.stop()

# Dynamic Suggested Questions from active table schema
preset_questions = generate_suggested_questions(st.session_state.active_table)

st.markdown("##### 💡 Suggested Questions for this Dataset:")
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    if st.button(preset_questions[0], use_container_width=True):
        st.session_state.current_prompt = preset_questions[0]
with col_p2:
    if st.button(preset_questions[1], use_container_width=True):
        st.session_state.current_prompt = preset_questions[1]
with col_p3:
    if st.button(preset_questions[2], use_container_width=True):
        st.session_state.current_prompt = preset_questions[2]

# Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message:
            st.code(message["sql"], language="sql")
        if "df" in message and isinstance(message["df"], pd.DataFrame):
            render_styled_dataframe(message["df"])

# Prompt Input
user_input = st.chat_input("Ask any question about your dataset (e.g. 'Show top 5 categories by sales')...")

# Override with preset click if clicked
if "current_prompt" in st.session_state and st.session_state.current_prompt:
    user_input = st.session_state.current_prompt
    st.session_state.current_prompt = None

if user_input:
    # 1. Add User message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Assistant Response Container
    with st.chat_message("assistant"):
        with st.spinner("Analyzing dataset, crafting SQL, and building dashboard..."):
            try:
                # Generate SQL
                raw_sql, gen_meta = generate_sql_query(
                    question=user_input,
                    table_name=st.session_state.active_table,
                    provider=provider_key,
                    api_key=api_key_input
                )
                formatted_sql = format_sql_query(raw_sql)

                # Validate SQL
                is_valid, val_msg = validate_sql_query(formatted_sql)
                if not is_valid:
                    st.error(f"❌ SQL Security / Validation Error: {val_msg}")
                    st.stop()

                # Execute SQL
                result_df, exec_meta = execute_sql_query(formatted_sql)

                # Plain English Explanation
                explanation = generate_plain_english_explanation(
                    question=user_input,
                    sql_query=formatted_sql,
                    df=result_df,
                    provider=provider_key,
                    api_key=api_key_input
                )

                # Render Results
                st.markdown(f"### 💡 Business Insights & Summary")
                st.markdown(explanation)
                st.caption(f"Engine: {gen_meta} | Execution Time: {exec_meta['execution_time_seconds']}s")

                st.markdown("### 📜 Generated SQL Query")
                st.code(formatted_sql, language="sql")

                # Optimization Check
                tips = analyze_sql_optimization(formatted_sql)
                if tips:
                    with st.expander("⚡ SQL Optimization Insights"):
                        for tip in tips:
                            st.text(f"• {tip}")

                # Modern KPI Cards
                st.markdown("### 📊 Key Performance Indicators (KPIs)")
                render_kpi_cards(result_df)

                # Plotly Visualization
                render_visualization_section(result_df)

                # Results Data Table
                st.markdown("### 📋 Query Results Data")
                render_styled_dataframe(result_df)

                # Export Buttons
                render_export_buttons(result_df, query=formatted_sql)

                # Save assistant output in chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": explanation,
                    "sql": formatted_sql,
                    "df": result_df
                })

            except Exception as e:
                logger.error(f"Error handling query: {e}")
                st.error(f"An error occurred while processing your request: {e}")
