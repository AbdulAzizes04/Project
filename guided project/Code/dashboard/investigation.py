"""
Investigation Center Dashboard Page for GuidedGuard.

Serves as the dedicated forensic investigation workbench for bank fraud analysts.
Provides deep multi-parameter case lookup, behavioral baseline auditing,
explainability attributions, counterfactual analysis, and multi-format forensic exports.

Features:
- Search by Transaction ID, Customer ID, Payee, Risk Level, Device
- Complete Case Dossier View
- Behavioral Baseline vs Transaction State Comparison
- Integrated SHAP, LIME, and Counterfactual Recourse
- Multi-format Dossier Exports: PDF, JSON, CSV, and TXT
"""

from typing import List, Dict, Any, Optional
import sys
import json
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import streamlit as st

import config
from models.predict import predict_single_transaction
from dashboard.components import render_header_status_bar, render_glass_card, render_gauge_chart
from utils.pdf_generator import generate_pdf_report


def get_mock_investigation_cases() -> List[Dict[str, Any]]:
    """Generate default forensic investigation cases."""
    return [
        {
            "transaction_id": "TXN-INV-9041",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "MULE-BEN-888",
            "amount": 75000.0,
            "old_balance_orig": 82000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 1,
            "device_type": "Unknown Proxy",
            "location": "Foreign Proxy",
            "velocity_6h": 8,
            "hour": 2,
            "is_late_night": 1,
            "status": "Under Investigation",
            "analyst_notes": "Suspected romance scam; victim executed rapid out-of-hours transfer following coaching.",
        },
        {
            "transaction_id": "TXN-INV-8120",
            "customer_id": "C-MARK-404",
            "beneficiary_id": "CRYPTO-EXCH-99",
            "amount": 42000.0,
            "old_balance_orig": 45000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 1,
            "device_type": "Web Browser",
            "location": "Domestic Home",
            "velocity_6h": 4,
            "hour": 15,
            "is_late_night": 0,
            "status": "Escalated to SOC",
            "analyst_notes": "Investment task scam; sudden lump sum transfer to unverified exchange gateway.",
        },
        {
            "transaction_id": "TXN-INV-7011",
            "customer_id": "C-EMMA-505",
            "beneficiary_id": "M-STORE-DIRECT",
            "amount": 1800.0,
            "old_balance_orig": 12000.0,
            "transaction_type": "PAYMENT",
            "is_new_beneficiary": 0,
            "device_type": "Mobile App",
            "location": "Domestic Home",
            "velocity_6h": 1,
            "hour": 13,
            "is_late_night": 0,
            "status": "Resolved / False Positive",
            "analyst_notes": "Verified genuine consumer purchase via customer contact.",
        },
    ]


def render_investigation_page():
    """
    Render complete forensic Investigation Center view.
    """
    render_header_status_bar(
        page_title="Forensic Investigation Center",
        page_description="Comprehensive case dossier lookup, behavioral forensic inspection, and multi-format evidence reporting.",
    )

    cases = get_mock_investigation_cases()

    # 1. Search & Filter Bar
    st.markdown("### 🔍 Case Dossier Lookup")
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)

    with s_col1:
        txn_query = st.text_input("Transaction ID Search", value="")
    with s_col2:
        cust_query = st.text_input("Customer ID", value="")
    with s_col3:
        status_filter = st.selectbox("Case Status", ["ALL", "Under Investigation", "Escalated to SOC", "Resolved / False Positive"])
    with s_col4:
        device_filter = st.selectbox("Device Category", ["ALL", "Unknown Proxy", "Mobile App", "Web Browser"])

    # Filter Cases
    filtered_cases = []
    for c in cases:
        if txn_query and txn_query.lower() not in c["transaction_id"].lower():
            continue
        if cust_query and cust_query.lower() not in c["customer_id"].lower():
            continue
        if status_filter != "ALL" and c["status"] != status_filter:
            continue
        if device_filter != "ALL" and c["device_type"] != device_filter:
            continue
        filtered_cases.append(c)

    if not filtered_cases:
        st.warning("No matching forensic cases found.")
        return

    # Select Active Case to Inspect
    case_ids = [c["transaction_id"] for c in filtered_cases]
    selected_id = st.selectbox("Select Active Case Dossier to Audit:", case_ids)
    active_case = next(c for c in filtered_cases if c["transaction_id"] == selected_id)

    # 2. Run Real-Time Full Forensic Analysis
    with st.spinner("Compiling Forensic Intelligence Dossier..."):
        result = predict_single_transaction(active_case, include_xai=True)

    st.markdown("---")

    # 3. Case Header & Key Forensic Metrics
    d_col1, d_col2 = st.columns([2, 1])

    with d_col1:
        st.markdown(f"### 📁 Case Dossier: `{selected_id}`")
        st.markdown(f"**Customer ID**: `{active_case['customer_id']}` &nbsp;|&nbsp; **Beneficiary**: `{active_case['beneficiary_id']}`")
        st.markdown(f"**Status**: `{active_case['status']}` &nbsp;|&nbsp; **Amount**: `${active_case['amount']:,.2f}`")
        st.info(f"📝 **Analyst Forensic Notes**: {active_case['analyst_notes']}")

    with d_col2:
        fig_g = render_gauge_chart("Fused Risk Score", float(result["risk_score"]))
        st.plotly_chart(fig_g, use_container_width=True)

    # 4. Behavioral Baseline vs Transaction Deviation Comparison
    st.markdown("### ⚖️ Behavioral Baseline Comparison")
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown("#### 👤 Customer Historical Baseline")
        st.markdown(
            """
            - **Average Spending**: $2,500.00
            - **Standard Spending Volatility**: ±$1,200.00
            - **Normal Operating Hours**: 08:00 – 21:00
            - **Trusted Device**: Personal Mobile Banking App
            - **Domestic Region**: Domestic Home Network
            - **Typical Velocity**: 1 – 2 payments / day
            """
        )

    with b_col2:
        st.markdown("#### 🚨 Active Transaction Observable Signals")
        st.markdown(
            f"""
            - **Submitted Amount**: **${active_case['amount']:,.2f}** ({active_case['amount']/2500:.1f}x baseline)
            - **Execution Hour**: **{active_case['hour']}:00 hrs** ({'Off-hours anomaly' if active_case['is_late_night'] else 'Normal'})
            - **Access Network**: **{active_case['device_type']}** ({active_case['location']})
            - **Payee Status**: **{'Newly added unverified payee' if active_case['is_new_beneficiary'] else 'Known payee'}**
            - **Observed Velocity**: **{active_case['velocity_6h']} payments** in rolling window
            """
        )

    st.markdown("---")

    # 5. Dual Engine Breakdown & Interventions
    st.markdown("### 🧩 Multi-Signal Risk Breakdown")
    comps = result["risk_components"]
    st.bar_chart(pd.DataFrame([{"Component": k.replace("_", " ").title(), "Risk Score": v} for k, v in comps.items()]).set_index("Component"))

    # 6. Counterfactual Recourse
    st.markdown("### 🔄 Counterfactual Recourse Analysis")
    cfs = result.get("counterfactual_analysis", {}).get("scenarios", [])
    if cfs:
        st.dataframe(pd.DataFrame([
            {
                "Lever": c["lever"],
                "Simulated Condition": c["simulated_state"],
                "Estimated Fused Risk": f"{c['estimated_risk_score']}/100 ({c['estimated_risk_level']})",
                "Risk Reduction": f"-{c['risk_reduction_points']} pts",
            }
            for c in cfs
        ]), use_container_width=True)

    st.markdown("---")

    # 7. Multi-Format Evidence Export Center
    st.markdown("### 📤 Export Forensic Case Dossier")
    exp1, exp2, exp3, exp4 = st.columns(4)

    with exp1:
        pdf_p = result.get("pdf_report_path", "")
        if pdf_p and Path(pdf_p).exists():
            with open(pdf_p, "rb") as fp:
                st.download_button(
                    label="📄 Download PDF Dossier",
                    data=fp.read(),
                    file_name=f"GuidedGuard_Forensic_Case_{selected_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.info("Generating PDF...")

    with exp2:
        json_data = json.dumps(result, indent=4, default=str)
        st.download_button(
            label="💾 Download JSON Dossier",
            data=json_data,
            file_name=f"Forensic_Dossier_{selected_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    with exp3:
        # CSV Export
        df_export = pd.DataFrame([{
            "case_id": selected_id,
            "customer_id": active_case["customer_id"],
            "amount": active_case["amount"],
            "fused_risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "supervised_score": result["model_risk_score"],
            "anomaly_score": result["anomaly_score"],
            "behavioral_score": result["behavioral_score"],
            "action": result["intervention"]["action"],
            "notes": active_case["analyst_notes"],
        }])
        st.download_button(
            label="📊 Download CSV Dossier",
            data=df_export.to_csv(index=False),
            file_name=f"Forensic_Dossier_{selected_id}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp4:
        txt_summary = (
            f"GUIDEDGUARD FORENSIC CASE DOSSIER: {selected_id}\n"
            f"Customer: {active_case['customer_id']}\n"
            f"Payee: {active_case['beneficiary_id']}\n"
            f"Amount: ${active_case['amount']:,.2f}\n"
            f"Risk Score: {result['risk_score']}/100 ({result['risk_level']})\n"
            f"Supervised ML Probability: {result['scam_probability']:.4f}\n"
            f"Anomaly Score: {result['anomaly_score']}/100\n"
            f"Recommended Action: {result['intervention']['action']}\n\n"
            f"PRIMARY REASONS:\n" + "\n".join([f"- {r}" for r in result["natural_language_explanation"]["primary_reasons"]])
        )
        st.download_button(
            label="📝 Download TXT Report",
            data=txt_summary,
            file_name=f"Forensic_Dossier_{selected_id}.txt",
            mime="text/plain",
            use_container_width=True,
        )
