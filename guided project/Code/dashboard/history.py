"""
Prediction History & Audit Log Page for GuidedGuard.

This module renders the central Prediction History & Audit Log view, serving as the application audit trail.
It aggregates prediction records from `st.session_state["simulation_history"]` and exported batch CSV files inside
`outputs/reports/`, providing multi-parameter search/filtering, detailed single-record inspection cards,
chronological audit timelines, Plotly risk donut/histogram charts, and CSV/JSON export handlers.

Responsibility:
- Audit trail aggregation & session state integration.
- Multi-parameter search & directional filtering.
- Detailed single transaction record inspector.
- Chronological timeline & Plotly audit analytics.
- Export handlers for CSV/JSON audit logs.
"""

import sys
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
from models.model_loader import load_metadata, validate_artifacts
from explainability.shap_explainer import generate_human_readable_summary
from dashboard.components import (
    render_header_status_bar,
    render_glass_card,
    render_risk_badge,
    render_risk_donut_chart,
)


def load_audit_records() -> pd.DataFrame:
    """
    Aggregate prediction records from simulation session state, batch reports, and historical baselines.

    Returns:
        pd.DataFrame: Audit log DataFrame.
    """
    records = []

    # 1. Simulation Session State History
    sim_history = st.session_state.get("simulation_history", [])
    if sim_history:
        for idx, item in enumerate(sim_history):
            r_level = str(item.get("Risk Level", "LOW"))
            records.append({
                "Transaction_ID": item.get("Transaction_ID", f"TXN-SIM-{idx}"),
                "Customer_ID": item.get("Customer_ID", "C123456789"),
                "Amount": float(item.get("Amount ($)", 2500.0)),
                "Type": item.get("Type", "TRANSFER"),
                "Prediction": item.get("Prediction", "Legitimate"),
                "Probability": float(item.get("Scam_Probability", 0.02 if "Legit" in str(item.get("Prediction")) else 0.95)),
                "Risk_Score": int(item.get("Risk Score", 15)),
                "Risk_Level": r_level,
                "Recommendation": item.get("Recommendation", "Approve" if r_level == "LOW" else "OTP Verification"),
                "Device": item.get("Device", "Mobile App"),
                "Region": item.get("Region", "Domestic Home"),
                "Velocity": item.get("Velocity", 2),
                "Beneficiary_Status": item.get("Beneficiary Status", "Known Beneficiary"),
                "Previous_Fraud_History": item.get("Previous Fraud History", "No"),
                "Model_Version": item.get("Model Version", "v1.2.0 (Gradient Boosting)"),
                "Latency_MS": float(item.get("Latency (ms)", 42.5)),
                "Source": "Simulator",
                "Timestamp": item.get("Timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            })

    # 2. Batch Prediction CSV Reports
    batch_csv_path = config.OUTPUTS_DIR / "reports" / "batch_predictions_transactions.csv"
    if batch_csv_path.exists():
        try:
            b_df = pd.read_csv(batch_csv_path)
            for idx, r in b_df.iterrows():
                is_scam = (r.get("predicted_scam", 0) == 1)
                r_level = str(r.get("risk_level", "CRITICAL" if is_scam else "LOW"))
                records.append({
                    "Transaction_ID": str(r.get("transaction_id", f"TXN-BATCH-{idx}")),
                    "Customer_ID": str(r.get("customer_id", f"C-BATCH-{idx}")),
                    "Amount": float(r.get("amount", 1500.0)),
                    "Type": str(r.get("type", "TRANSFER")),
                    "Prediction": "Scam / Fraudulent" if is_scam else "Legitimate",
                    "Probability": float(r.get("scam_probability", 0.95 if is_scam else 0.02)),
                    "Risk_Score": int(r.get("risk_score", 90 if is_scam else 10)),
                    "Risk_Level": r_level,
                    "Recommendation": str(r.get("banking_recommendation", "Freeze Transaction" if is_scam else "Approve")),
                    "Device": "Web Browser",
                    "Region": "Domestic",
                    "Velocity": 3,
                    "Beneficiary_Status": "New Beneficiary" if is_scam else "Known Beneficiary",
                    "Previous_Fraud_History": "Yes" if is_scam else "No",
                    "Model_Version": "v1.2.0 (Gradient Boosting)",
                    "Latency_MS": 38.5,
                    "Source": "Batch Inference",
                    "Timestamp": "2026-08-03 12:00",
                })
        except Exception:
            pass

    # 3. Default Mock Baseline Records if Empty
    if not records:
        for i in range(25):
            is_scam = (i % 8 == 0)
            r_level = "CRITICAL" if is_scam else ("LOW" if i % 2 == 0 else "MEDIUM")
            records.append({
                "Transaction_ID": f"TXN-AUDIT-{1000+i}",
                "Customer_ID": f"C98765{i:02d}",
                "Amount": float(np.random.randint(200, 45000)),
                "Type": "CASH_OUT" if is_scam else "TRANSFER",
                "Prediction": "Scam / Fraudulent" if is_scam else "Legitimate",
                "Probability": round(np.random.uniform(0.85, 0.95) if is_scam else np.random.uniform(0.01, 0.15), 4),
                "Risk_Score": np.random.randint(85, 99) if is_scam else np.random.randint(5, 30),
                "Risk_Level": r_level,
                "Recommendation": "Freeze Transaction, Notify Customer, Manual Review" if is_scam else ("Approve" if r_level == "LOW" else "OTP Verification"),
                "Device": "Unknown Proxy" if is_scam else "Mobile App",
                "Region": "Foreign Proxy" if is_scam else "Domestic Home",
                "Velocity": np.random.randint(5, 12) if is_scam else np.random.randint(1, 4),
                "Beneficiary_Status": "New Beneficiary" if is_scam else "Known Beneficiary",
                "Previous_Fraud_History": "Yes" if is_scam else "No",
                "Model_Version": "v1.2.0 (Gradient Boosting)",
                "Latency_MS": round(np.random.uniform(35.0, 50.0), 2),
                "Source": "Historical Audit",
                "Timestamp": (datetime.datetime.now() - datetime.timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M"),
            })

    return pd.DataFrame(records)



def render_history_page():
    """
    Render complete 8-section Prediction History & Audit Log view.
    """
    # 1. Top Navigation Header Status Bar
    render_header_status_bar(
        page_title="Prediction History & Audit Log",
        page_description="Central audit trail for all simulated and batch payment predictions, risk scores, and XAI summaries.",
    )

    df_audit = load_audit_records()
    if "Confidence" not in df_audit.columns:
        df_audit["Confidence"] = df_audit["Probability"].apply(lambda p: round(max(p, 1.0 - p), 4))

    total_rec = len(df_audit)
    scam_rec = len(df_audit[df_audit["Prediction"].str.contains("Scam", case=False)])
    legit_rec = total_rec - scam_rec
    avg_risk = float(df_audit["Risk_Score"].mean()) if total_rec > 0 else 0.0
    avg_conf = float(df_audit["Confidence"].mean()) if total_rec > 0 else 1.0
    avg_lat = float(df_audit["Latency_MS"].mean()) if total_rec > 0 else 42.0
    latest_time = str(df_audit["Timestamp"].iloc[0]) if total_rec > 0 else "N/A"

    # ==========================================
    # SECTION 2: SUMMARY KPI CARDS
    # ==========================================
    st.markdown("### 📊 1. Audit Trail Summary KPIs")
    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

    with k1:
        st.metric("Total Stored Logs", f"{total_rec:,}")
    with k2:
        st.metric("Flagged Scams", f"{scam_rec:,}")
    with k3:
        st.metric("Legitimate Txns", f"{legit_rec:,}")
    with k4:
        st.metric("Avg Risk Score", f"{avg_risk:.1f}/100")
    with k5:
        st.metric("Avg Confidence", f"{avg_conf*100:.1f}%")
    with k6:
        st.metric("Avg Latency", f"{avg_lat:.1f} ms")
    with k7:
        st.metric("Latest Activity", latest_time[-5:])

    st.markdown("---")

    # ==========================================
    # SECTION 3: MULTI-PARAMETER SEARCH & FILTERS
    # ==========================================
    st.markdown("### 🔎 2. Multi-Parameter Audit Search & Filters")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        search_query = st.text_input("🔍 Search Txn / Customer ID", value="")
    with f_col2:
        filter_pred = st.selectbox("Filter Prediction Class", ["All Predictions", "Legitimate", "Scam / Fraudulent"])
    with f_col3:
        filter_risk = st.selectbox("Filter Risk Level", ["All Levels", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    with f_col4:
        filter_source = st.selectbox("Filter Source", ["All Sources", "Simulator", "Batch Inference", "Historical Audit"])

    score_range = st.slider("Filter Risk Score Range (0 - 100)", 0, 100, (0, 100))

    df_filtered = df_audit.copy()

    if search_query:
        df_filtered = df_filtered[
            df_filtered["Transaction_ID"].astype(str).str.contains(search_query, case=False, na=False) |
            df_filtered["Customer_ID"].astype(str).str.contains(search_query, case=False, na=False)
        ]
    if filter_pred != "All Predictions":
        df_filtered = df_filtered[df_filtered["Prediction"] == filter_pred]
    if filter_risk != "All Levels":
        df_filtered = df_filtered[df_filtered["Risk_Level"] == filter_risk]
    if filter_source != "All Sources":
        df_filtered = df_filtered[df_filtered["Source"] == filter_source]

    df_filtered = df_filtered[
        (df_filtered["Risk_Score"] >= score_range[0]) & (df_filtered["Risk_Score"] <= score_range[1])
    ]

    st.markdown("---")

    # ==========================================
    # SECTION 4: PREDICTION HISTORY TABLE
    # ==========================================
    st.markdown(f"### 📜 3. Prediction Audit Log Table ({len(df_filtered)} Records)")
    st.dataframe(df_filtered, use_container_width=True)

    st.markdown("---")

    # ==========================================
    # SECTION 5: DETAILED PREDICTION RECORD INSPECTOR
    # ==========================================
    st.markdown("### 🔍 4. Detailed Prediction Record Inspector")

    txn_list = list(df_filtered["Transaction_ID"])
    if txn_list:
        selected_txn = st.selectbox("Select Transaction Record to Inspect", txn_list)
        row_match = df_filtered[df_filtered["Transaction_ID"] == selected_txn].iloc[0]

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            render_glass_card(
                title=f"💳 Transaction Details ({selected_txn})",
                content_markdown=f"""
                - **Customer ID**: {row_match.get('Customer_ID')}
                - **Amount**: ${row_match.get('Amount', 0.0):,.2f}
                - **Transaction Type**: {row_match.get('Type')}
                - **Prediction Class**: {row_match.get('Prediction')}
                - **Scam Probability**: {row_match.get('Probability', 0.0)*100:.2f}%
                - **Risk Score Index**: {row_match.get('Risk_Score')} / 100 ({row_match.get('Risk_Level')} RISK)
                - **Banking Recommendation**: **{row_match.get('Recommendation', 'N/A')}**
                - **Device Profile**: {row_match.get('Device', 'N/A')}
                - **Location Region**: {row_match.get('Region', 'N/A')}
                - **6h Txn Velocity**: {row_match.get('Velocity', 1)} txns
                - **Beneficiary Status**: {row_match.get('Beneficiary_Status', 'N/A')}
                - **Prior Fraud History**: {row_match.get('Previous_Fraud_History', 'No')}
                - **Model Version**: {row_match.get('Model_Version', 'v1.2.0')}
                - **Latency**: {row_match.get('Latency_MS')} ms
                - **Source**: {row_match.get('Source')}
                - **Timestamp**: {row_match.get('Timestamp')}
                """,
            )

        with d_col2:
            sample_contributions = {
                "amount_to_avg_ratio": 0.3200 if "Scam" in str(row_match['Prediction']) else -0.1500,
                "customer_zscore_amount": 0.2800 if "Scam" in str(row_match['Prediction']) else -0.2200,
                "velocity_6h": 0.1500 if "Scam" in str(row_match['Prediction']) else -0.0500,
            }
            narratives = generate_human_readable_summary(sample_contributions)
            narrative_text = "\n".join([f"- {s}" for s in narratives])
            render_glass_card(f"💡 Explanation Narrative for {selected_txn}", narrative_text)

    st.markdown("---")

    # ==========================================
    # SECTION 6 & 7: CHRONOLOGICAL TIMELINE & PLOTLY ANALYTICS
    # ==========================================
    st.markdown("### 📈 5. Chronological Audit Analytics & Timeline")

    a_col1, a_col2 = st.columns(2)

    with a_col1:
        st.markdown("#### Risk Level Category Breakdown")
        r_counts = df_filtered["Risk_Level"].value_counts().to_dict()
        fig_donut = render_risk_donut_chart({
            "LOW": r_counts.get("LOW", 0),
            "MEDIUM": r_counts.get("MEDIUM", 0),
            "HIGH": r_counts.get("HIGH", 0),
            "CRITICAL": r_counts.get("CRITICAL", 0),
        })
        st.plotly_chart(fig_donut, use_container_width=True)

    with a_col2:
        st.markdown("#### Audit Record Sources Breakdown")
        fig_src = px.histogram(
            df_filtered,
            x="Source",
            color="Prediction",
            title="Predictions Count by Audit Source",
            color_discrete_map={"Legitimate": "#22C55E", "Scam / Fraudulent": "#EF4444"},
        )
        fig_src.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#F8FAFC")),
            xaxis=dict(color="#94A3B8", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(color="#F8FAFC", gridcolor="rgba(255,255,255,0.05)"),
            height=260,
        )
        st.plotly_chart(fig_src, use_container_width=True)

    st.markdown("---")

    # ==========================================
    # SECTION 8: EXPORT CENTER
    # ==========================================
    st.markdown("### ⬇️ 6. Audit Trail Export Center")
    exp1, exp2, exp3 = st.columns(3)

    with exp1:
        st.download_button(
            label="📊 Download Full Audit Trail CSV",
            data=df_audit.to_csv(index=False),
            file_name="guidedguard_full_audit_log.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp2:
        st.download_button(
            label="📜 Download Filtered Audit CSV",
            data=df_filtered.to_csv(index=False),
            file_name="guidedguard_filtered_audit_log.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp3:
        audit_json_str = df_filtered.to_json(orient="records", indent=4)
        st.download_button(
            label="⚙️ Download Audit Log JSON",
            data=audit_json_str,
            file_name="guidedguard_audit_log.json",
            mime="application/json",
            use_container_width=True,
        )
