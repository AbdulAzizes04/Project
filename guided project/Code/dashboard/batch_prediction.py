"""
Batch Prediction Page for GuidedGuard.

This module renders the Batch Payment Scam Detection page, allowing users to upload CSV transaction files,
validate dataset schema integrity, trigger bulk fraud inference (`predict_batch_transactions()`), render Plotly
visual risk charts, filter batch result tables, and download output prediction CSVs, risk score CSVs, and JSON summaries.

Responsibility:
- CSV file upload & dataset preview.
- Dataset schema validation report.
- Backend batch prediction engine orchestration.
- Plotly donut, histogram, scatter, and bar analytics.
- Interactive filtering and download center handlers.
"""

from typing import Tuple, Dict, Any, List, Optional
import sys
import tempfile
import json
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from models.predict import predict_batch_transactions
from dashboard.components import (
    render_header_status_bar,
    render_glass_card,
    render_risk_donut_chart,
)


def validate_csv_schema(df: pd.DataFrame) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validate uploaded batch CSV column names, required fields, and dtypes.

    Parameters:
        df (pd.DataFrame): Uploaded CSV DataFrame.

    Returns:
        Tuple[bool, List[str], Dict[str, Any]]: (is_valid, list_of_errors, validation_summary)
    """
    errors = []
    if df.empty:
        return False, ["Uploaded CSV file is empty."], {}

    col_names_lower = [str(c).lower() for c in df.columns]

    has_amount = any("amount" in c for c in col_names_lower)
    if not has_amount:
        errors.append("Missing required transaction amount column (e.g. 'amount').")

    num_rows, num_cols = df.shape
    null_count = int(df.isnull().sum().sum())
    dup_ids = int(df["transaction_id"].duplicated().sum()) if "transaction_id" in df.columns else 0

    summary = {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "null_count": null_count,
        "duplicate_ids": dup_ids,
        "memory_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
    }

    is_valid = len(errors) == 0
    return is_valid, errors, summary


def render_batch_prediction_page():
    """
    Render complete interactive Batch Prediction view.
    """
    # 1. Top Navigation Header Status Bar
    render_header_status_bar(
        page_title="Batch Payment Scam Detection",
        page_description="Upload CSV transaction files for automated bulk fraud detection, risk scoring, and report exports.",
    )

    st.markdown("### 📁 1. Upload Transaction CSV Dataset")

    col_up, col_sample = st.columns([3, 1])

    with col_sample:
        st.markdown("**Sample Template**")
        sample_csv_path = config.TRANSACTIONS_CSV
        if sample_csv_path.exists():
            with open(sample_csv_path, "rb") as fp:
                st.download_button(
                    label="⬇️ Download Sample CSV Template",
                    data=fp.read(),
                    file_name="sample_batch_transactions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    with col_up:
        uploaded_file = st.file_uploader("Choose a CSV file containing payment transactions", type=["csv"])

    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            is_valid, validation_errors, summary_info = validate_csv_schema(df_uploaded)

            # Display File Preview Metrics
            st.markdown("#### 🔍 Uploaded Dataset Overview")
            p1, p2, p3, p4 = st.columns(4)
            with p1:
                st.metric("Total Rows", f"{summary_info.get('num_rows', 0):,}")
            with p2:
                st.metric("Total Columns", f"{summary_info.get('num_cols', 0)}")
            with p3:
                st.metric("Missing Values", f"{summary_info.get('null_count', 0)}")
            with p4:
                st.metric("Memory Usage", f"{summary_info.get('memory_kb', 0)} KB")

            if not is_valid:
                st.error(f"❌ Dataset Validation Failed: {', '.join(validation_errors)}")
                return

            st.success("✅ Dataset schema validated successfully. Ready for batch inference.")

            st.markdown("#### Dataset Preview (First 5 Rows)")
            st.dataframe(df_uploaded.head(5), use_container_width=True)

            st.markdown("---")

            # ==========================================
            # 2. BATCH INFERENCE EXECUTION
            # ==========================================
            st.markdown("### 🚀 2. Execute Batch Fraud Analysis")

            if st.button("⚡ Run Batch Fraud Analysis", type="primary", use_container_width=True):
                # Save uploaded file to temp path
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                    df_uploaded.to_csv(tmp_file.name, index=False)
                    temp_csv_path = Path(tmp_file.name)

                progress_bar = st.progress(0)
                st.info("🔍 Running GuidedGuard Batch Inference Engine...")

                # Update progress bar
                for pct in range(1, 101, 20):
                    progress_bar.progress(pct)

                # Call backend predict_batch_transactions
                batch_result = predict_batch_transactions(temp_csv_path, output_dir=config.OUTPUTS_DIR / "reports")

                progress_bar.progress(100)
                st.success(f"🎉 Batch inference complete in {batch_result.get('total_latency_sec', 0.5)}s!")

                st.markdown("---")

                # ==========================================
                # 3. SUMMARY STATISTICS & KPI CARDS
                # ==========================================
                st.markdown("### 📊 3. Batch Summary Statistics")

                total_txns = batch_result.get("total_transactions", len(df_uploaded))
                flagged_scams = batch_result.get("flagged_scam_count", 0)
                legit_cnt = total_txns - flagged_scams
                scam_rate = batch_result.get("flagged_scam_rate_pct", 0.0)
                avg_risk = batch_result.get("avg_risk_score", 0.0)

                b1, b2, b3, b4, b5 = st.columns(5)
                with b1:
                    st.metric("Total Analyzed", f"{total_txns:,}")
                with b2:
                    st.metric("Flagged Scams", f"{flagged_scams:,}", delta=f"{scam_rate}% Rate", delta_color="inverse")
                with b3:
                    st.metric("Legitimate Txns", f"{legit_cnt:,}")
                with b4:
                    st.metric("Avg Risk Score", f"{avg_risk:.1f}/100")
                with b5:
                    st.metric("Total Time", f"{batch_result.get('total_latency_sec', 0.5)} s")

                st.markdown("---")

                # Load generated output CSV for interactive analytics
                out_pred_csv = Path(batch_result.get("prediction_csv", ""))
                if out_pred_csv.exists():
                    df_out = pd.read_csv(out_pred_csv)

                    # ==========================================
                    # 4. VISUAL ANALYTICS (PLOTLY)
                    # ==========================================
                    st.markdown("### 📈 4. Batch Visual Analytics")
                    vis_col1, vis_col2 = st.columns(2)

                    with vis_col1:
                        st.markdown("#### Risk Level Category Breakdown")
                        r_counts = df_out["risk_level"].value_counts().to_dict()
                        fig_donut = render_risk_donut_chart({
                            "LOW": r_counts.get("LOW", 0),
                            "MEDIUM": r_counts.get("MEDIUM", 0),
                            "HIGH": r_counts.get("HIGH", 0),
                            "CRITICAL": r_counts.get("CRITICAL", 0),
                        })
                        st.plotly_chart(fig_donut, use_container_width=True)

                    with vis_col2:
                        st.markdown("#### Risk Score Distribution Histogram")
                        fig_hist = px.histogram(
                            df_out,
                            x="risk_score",
                            color="risk_level",
                            title="Batch Risk Score Frequency",
                            color_discrete_map={"LOW": "#22C55E", "MEDIUM": "#FACC15", "HIGH": "#FB923C", "CRITICAL": "#EF4444"},
                        )
                        fig_hist.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            legend=dict(font=dict(color="#F8FAFC")),
                            xaxis=dict(color="#94A3B8", gridcolor="rgba(255,255,255,0.05)"),
                            yaxis=dict(color="#F8FAFC", gridcolor="rgba(255,255,255,0.05)"),
                            height=260,
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)

                    st.markdown("---")

                    # ==========================================
                    # 5. INTERACTIVE FILTERS & RESULT TABLE
                    # ==========================================
                    st.markdown("### 🔎 5. Interactive Batch Result Table")
                    f_c1, f_c2 = st.columns(2)

                    with f_c1:
                        search_txn = st.text_input("🔍 Search Transaction ID", value="")
                    with f_c2:
                        filter_level = st.selectbox("Filter Risk Level", ["All Levels", "LOW", "MEDIUM", "HIGH", "CRITICAL"])

                    df_res_filt = df_out.copy()

                    if search_txn and "transaction_id" in df_res_filt.columns:
                        df_res_filt = df_res_filt[df_res_filt["transaction_id"].astype(str).str.contains(search_txn, case=False, na=False)]
                    if filter_level != "All Levels":
                        df_res_filt = df_res_filt[df_res_filt["risk_level"] == filter_level]

                    st.dataframe(df_res_filt, use_container_width=True)

                    st.markdown("---")

                    # ==========================================
                    # 6. DOWNLOAD CENTER
                    # ==========================================
                    st.markdown("### ⬇️ 6. Download Batch Reports")
                    dl1, dl2, dl3 = st.columns(3)

                    with dl1:
                        st.download_button(
                            label="📄 Download Batch Predictions CSV",
                            data=df_out.to_csv(index=False),
                            file_name=out_pred_csv.name,
                            mime="text/csv",
                            use_container_width=True,
                        )
                    with dl2:
                        risk_csv_path = Path(batch_result.get("risk_csv", ""))
                        if risk_csv_path.exists():
                            with open(risk_csv_path, "rb") as fp:
                                st.download_button("📊 Download Risk Scores CSV", data=fp.read(), file_name=risk_csv_path.name, mime="text/csv", use_container_width=True)
                    with dl3:
                        summary_json_str = json.dumps(batch_result, indent=4)
                        st.download_button("⚙️ Download Batch Summary JSON", data=summary_json_str, file_name="batch_summary_report.json", mime="application/json", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error processing uploaded CSV file: {e}")
    else:
        render_glass_card(
            title="📁 Batch Inference Instructions",
            content_markdown="""
            - Upload a CSV file containing payment transactions to run automated batch scam detection.
            - Required authorization fields: Transaction Amount (`amount`), Origin Balance Before (`old_balance_orig` or `oldbalanceOrg`), Transaction Type (`type`), Step / Hour (`step`).
            - Optional fields: Customer ID (`nameOrig`), Recipient ID (`nameDest`), Device/Location proxies.
            - Note: Post-transaction balances (`newbalanceOrig`, `newbalanceDest`) are excluded to eliminate target leakage.
            - Output files (Predictions CSV, Risk Scores CSV, Summary JSON) will be exported automatically to `outputs/reports/`.
            """,
        )
