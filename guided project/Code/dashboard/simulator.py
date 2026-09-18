"""
Payment Transaction Simulator Page for GuidedGuard.

This module provides a fully interactive payment transaction simulator UI with both
Simple Mode (4 core inputs) and Advanced Mode (all parameters), allowing users to submit
payment parameters, trigger real-time ML inference (`predict_single_transaction()`), calculate
composite risk scores (0-100), view dynamic SHAP/LIME visual previews, and export reports.

Responsibility:
- Interactive Streamlit form with Simple vs Advanced toggle.
- Live backend prediction engine orchestration.
- Risk score gauge & probability meter visualization.
- Fresh SHAP & LIME plot previews for active transaction.
- Human-readable narrative text card & risk reasoning.
- Download handlers for JSON/CSV report artifacts.
- Local session audit history log (`st.session_state`).
"""

import sys
import json
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import streamlit as st

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from models.predict import predict_single_transaction, validate_transaction
from dashboard.components import (
    render_header_status_bar,
    render_glass_card,
    render_gauge_chart,
    render_timeline_steps,
    render_banking_recommendation_card,
    render_risk_score_breakdown_panel,
    render_timing_breakdown_panel,
)


def render_simulator_page():
    """
    Render complete interactive Payment Transaction Simulator view with Simple vs Advanced modes.
    """
    # 1. Header Navigation Status Bar
    render_header_status_bar(
        page_title="Payment Transaction Simulator",
        page_description="Simulate digital payment transactions, run real-time scam detection, evaluate risk scores, and view XAI explanations.",
    )

    # Initialize Session History, Presets & Interactive State if absent
    if "simulation_history" not in st.session_state:
        st.session_state["simulation_history"] = []

    def _apply_preset(preset_key: str):
        st.session_state["simulator_preset"] = preset_key
        if preset_key == "scam":
            st.session_state["sim_amount"] = 95000.0
            st.session_state["sim_old_orig"] = 95000.0
            st.session_state["sim_new_orig"] = 0.0
            st.session_state["sim_old_dest"] = 0.0
            st.session_state["sim_new_dest"] = 95000.0
            st.session_state["sim_txn_type"] = "CASH_OUT"
            st.session_state["sim_device"] = "Unknown Proxy"
            st.session_state["sim_loc"] = "Foreign Proxy"
            st.session_state["sim_velocity"] = 12
            st.session_state["sim_new_ben"] = "Yes"
            st.session_state["sim_time_window"] = "Late Night"
            st.session_state["sim_prev_fraud"] = "No"
        elif preset_key == "proxy":
            st.session_state["sim_amount"] = 15000.0
            st.session_state["sim_old_orig"] = 20000.0
            st.session_state["sim_new_orig"] = 5000.0
            st.session_state["sim_old_dest"] = 500.0
            st.session_state["sim_new_dest"] = 15500.0
            st.session_state["sim_txn_type"] = "TRANSFER"
            st.session_state["sim_device"] = "Unknown Proxy"
            st.session_state["sim_loc"] = "High Risk Region"
            st.session_state["sim_velocity"] = 6
            st.session_state["sim_new_ben"] = "Yes"
            st.session_state["sim_time_window"] = "Business Hours"
            st.session_state["sim_prev_fraud"] = "No"
        else:
            st.session_state["sim_amount"] = 2500.0
            st.session_state["sim_old_orig"] = 10000.0
            st.session_state["sim_new_orig"] = 7500.0
            st.session_state["sim_old_dest"] = 1000.0
            st.session_state["sim_new_dest"] = 3500.0
            st.session_state["sim_txn_type"] = "TRANSFER"
            st.session_state["sim_device"] = "Mobile App"
            st.session_state["sim_loc"] = "Domestic Home"
            st.session_state["sim_velocity"] = 2
            st.session_state["sim_new_ben"] = "No"
            st.session_state["sim_time_window"] = "Business Hours"
            st.session_state["sim_prev_fraud"] = "No"

        st.session_state["sim_txn_id"] = f"TXN-{np.random.randint(100000, 999999)}"
        st.session_state["sim_cust_id"] = "C123456789"
        st.session_state["sim_ben_id"] = "M987654321"
        st.session_state["_prev_sim_amount"] = st.session_state["sim_amount"]
        st.session_state["simulator_result"] = None
        st.session_state["simulator_active_payload"] = None

    if "sim_amount" not in st.session_state:
        _apply_preset("legit")

    if "sim_auto_calc" not in st.session_state:
        st.session_state["sim_auto_calc"] = True

    # Callbacks for Real-Time Balance Auto-Calculation
    def _on_amount_change():
        if not st.session_state.get("sim_auto_calc", True):
            return
        amt = float(st.session_state.get("sim_amount", 0.0))
        old_orig = float(st.session_state.get("sim_old_orig", 0.0))
        new_orig = float(st.session_state.get("sim_new_orig", 0.0))
        old_dest = float(st.session_state.get("sim_old_dest", 0.0))
        txn_type = st.session_state.get("sim_txn_type", "TRANSFER")

        # Sender auto-balance logic:
        # If new_orig == 0 (account wipeout attack pattern) or old_orig was previously matching old amount:
        prev_amt = float(st.session_state.get("_prev_sim_amount", amt))
        if new_orig == 0.0 or abs(old_orig - prev_amt) < 0.01:
            # Maintain full account wipeout
            st.session_state["sim_old_orig"] = amt
            st.session_state["sim_new_orig"] = 0.0
        else:
            # If old balance is less than transaction amount, adjust sender old balance
            if old_orig < amt:
                reserve = max(new_orig, 2500.0)
                st.session_state["sim_old_orig"] = amt + reserve
                st.session_state["sim_new_orig"] = reserve
            else:
                if txn_type in ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT"]:
                    st.session_state["sim_new_orig"] = max(0.0, st.session_state["sim_old_orig"] - amt)
                elif txn_type == "CASH_IN":
                    st.session_state["sim_new_orig"] = st.session_state["sim_old_orig"] + amt

        # Receiver auto-balance logic:
        st.session_state["sim_new_dest"] = max(0.0, old_dest + amt)
        st.session_state["_prev_sim_amount"] = amt

    def _on_sender_old_change():
        if not st.session_state.get("sim_auto_calc", True):
            return
        amt = float(st.session_state.get("sim_amount", 0.0))
        old_orig = float(st.session_state.get("sim_old_orig", 0.0))
        txn_type = st.session_state.get("sim_txn_type", "TRANSFER")

        if txn_type in ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT"]:
            st.session_state["sim_new_orig"] = max(0.0, old_orig - amt)
        elif txn_type == "CASH_IN":
            st.session_state["sim_new_orig"] = old_orig + amt

    def _on_receiver_old_change():
        if not st.session_state.get("sim_auto_calc", True):
            return
        amt = float(st.session_state.get("sim_amount", 0.0))
        old_dest = float(st.session_state.get("sim_old_dest", 0.0))
        st.session_state["sim_new_dest"] = max(0.0, old_dest + amt)

    def _on_txn_type_change():
        if not st.session_state.get("sim_auto_calc", True):
            return
        _on_amount_change()

    st.markdown("### 📝 1. Enter Transaction Parameters")

    # Preset Example Loader Buttons
    preset_col1, preset_col2, preset_col3 = st.columns(3)
    with preset_col1:
        if st.button("🟢 Load Normal Salary Transfer Preset", use_container_width=True):
            _apply_preset("legit")
            st.rerun()
    with preset_col2:
        if st.button("🔴 Load High-Risk Account Wipeout Scam Preset", use_container_width=True):
            _apply_preset("scam")
            st.rerun()
    with preset_col3:
        if st.button("🟡 Load Unverified Foreign Proxy Preset", use_container_width=True):
            _apply_preset("proxy")
            st.rerun()

    # Dynamic Auto-Sync Bar & Quick Balancers
    sync_col1, sync_col2, sync_col3, sync_col4 = st.columns([2.3, 1.2, 1.2, 0.9])
    with sync_col1:
        st.checkbox(
            "⚡ Auto-Calculate Balances (Sync Old & New Balances with Amount)",
            key="sim_auto_calc",
            help="When active, entering or changing Transaction Amount or Old Balances dynamically computes and updates the New Balances in real time.",
        )
    with sync_col2:
        if st.button("🧹 Set Wipeout ($0 New)", help="Sets Sender Old = Amount and Sender New = $0 (Simulate full drain attack)", use_container_width=True):
            amt = float(st.session_state["sim_amount"])
            st.session_state["sim_old_orig"] = amt
            st.session_state["sim_new_orig"] = 0.0
            st.session_state["sim_new_dest"] = float(st.session_state["sim_old_dest"]) + amt
            st.rerun()
    with sync_col3:
        if st.button("💼 Set Normal (+25%)", help="Sets Sender Old = 1.25x Amount (Solvent customer with 25% reserve)", use_container_width=True):
            amt = float(st.session_state["sim_amount"])
            st.session_state["sim_old_orig"] = amt * 1.25
            st.session_state["sim_new_orig"] = amt * 0.25
            st.session_state["sim_new_dest"] = float(st.session_state["sim_old_dest"]) + amt
            st.rerun()
    with sync_col4:
        if st.button("🔄 Sync Now", help="Force recalculation of all balances", use_container_width=True):
            _on_amount_change()
            st.rerun()

    # Dynamic Balance Overview Live Feedback
    curr_amt = float(st.session_state.get("sim_amount", 0.0))
    curr_old_orig = float(st.session_state.get("sim_old_orig", 0.0))
    curr_new_orig = float(st.session_state.get("sim_new_orig", 0.0))
    curr_old_dest = float(st.session_state.get("sim_old_dest", 0.0))
    curr_new_dest = float(st.session_state.get("sim_new_dest", 0.0))
    sender_delta = curr_new_orig - curr_old_orig
    receiver_delta = curr_new_dest - curr_old_dest

    st.info(
        f"💳 **Live Synchronized Balance Flow**: "
        f"**Sender**: `${curr_old_orig:,.2f}` ➔ `${curr_new_orig:,.2f}` (`{sender_delta:+,.2f}`) | "
        f"**Receiver**: `${curr_old_dest:,.2f}` ➔ `${curr_new_dest:,.2f}` (`{receiver_delta:+,.2f}`) | "
        f"**Amount**: `${curr_amt:,.2f}`"
    )

    # View Mode Toggle: Simple vs Advanced
    view_mode = st.radio(
        "Select Simulator Form Mode:",
        ["⚡ Simple Mode (4 Essential Inputs)", "⚙️ Advanced Banking Mode (All Parameters)"],
        horizontal=True,
    )

    # ==========================================
    # 2. TRANSACTION INPUT CONTROLS
    # ==========================================
    if "Simple" in view_mode:
        # Simple Mode: Only 4 core essential inputs
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            amount = st.number_input("Transaction Amount ($)", min_value=1.0, step=500.0, key="sim_amount", on_change=_on_amount_change)

        with s2:
            type_options = ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"]
            type_idx = type_options.index(st.session_state.get("sim_txn_type", "TRANSFER")) if st.session_state.get("sim_txn_type") in type_options else 0
            txn_type = st.selectbox("Transaction Type", type_options, index=type_idx, key="sim_txn_type", on_change=_on_txn_type_change)

        with s3:
            old_balance_orig = st.number_input("Sender Old Balance ($)", min_value=0.0, step=500.0, key="sim_old_orig", on_change=_on_sender_old_change)

        with s4:
            device_options = ["Mobile App", "Web Browser", "Unknown Proxy"]
            dev_idx = device_options.index(st.session_state.get("sim_device", "Mobile App")) if st.session_state.get("sim_device") in device_options else 0
            device_type = st.selectbox("Device Type", device_options, index=dev_idx, key="sim_device")

        # Auto-calculated background defaults for Simple Mode
        new_balance_orig = float(st.session_state.get("sim_new_orig", max(0.0, old_balance_orig - amount)))
        old_balance_dest = float(st.session_state.get("sim_old_dest", 1000.0))
        new_balance_dest = float(st.session_state.get("sim_new_dest", old_balance_dest + amount))
        velocity_6h = int(st.session_state.get("sim_velocity", 2))
        location = str(st.session_state.get("sim_loc", "Domestic Home"))
        new_beneficiary = str(st.session_state.get("sim_new_ben", "No"))
        time_window = str(st.session_state.get("sim_time_window", "Business Hours"))
        previous_fraud_flag = str(st.session_state.get("sim_prev_fraud", "No"))
        txn_id = st.session_state.get("sim_txn_id", f"TXN-{np.random.randint(100000, 999999)}")
        customer_id = st.session_state.get("sim_cust_id", "C123456789")
        beneficiary_id = st.session_state.get("sim_ben_id", "M987654321")

    else:
        # Advanced Mode: Full 12-parameter technical inputs
        f1, f2, f3, f4 = st.columns(4)

        with f1:
            txn_id = st.text_input("Transaction ID", key="sim_txn_id")
            customer_id = st.text_input("Customer ID", key="sim_cust_id")
            beneficiary_id = st.text_input("Beneficiary ID", key="sim_ben_id")
            type_options = ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"]
            type_idx = type_options.index(st.session_state.get("sim_txn_type", "TRANSFER")) if st.session_state.get("sim_txn_type") in type_options else 0
            txn_type = st.selectbox("Transaction Type", type_options, index=type_idx, key="sim_txn_type", on_change=_on_txn_type_change)

        with f2:
            amount = st.number_input("Transaction Amount ($)", min_value=1.0, step=500.0, key="sim_amount", on_change=_on_amount_change)
            old_balance_orig = st.number_input("Sender Old Balance ($)", min_value=0.0, step=500.0, key="sim_old_orig", on_change=_on_sender_old_change)
            new_balance_orig = st.number_input("Sender New Balance ($)", min_value=0.0, step=500.0, key="sim_new_orig")
            velocity_6h = st.number_input("Recent Txn Velocity (6h Count)", min_value=0, step=1, key="sim_velocity")

        with f3:
            old_balance_dest = st.number_input("Receiver Old Balance ($)", min_value=0.0, step=500.0, key="sim_old_dest", on_change=_on_receiver_old_change)
            new_balance_dest = st.number_input("Receiver New Balance ($)", min_value=0.0, step=500.0, key="sim_new_dest")
            device_options = ["Mobile App", "Web Browser", "Unknown Proxy"]
            dev_idx = device_options.index(st.session_state.get("sim_device", "Mobile App")) if st.session_state.get("sim_device") in device_options else 0
            device_type = st.selectbox("Device Type", device_options, index=dev_idx, key="sim_device")
            loc_options = ["Domestic Home", "Foreign Proxy", "High Risk Region"]
            loc_idx = loc_options.index(st.session_state.get("sim_loc", "Domestic Home")) if st.session_state.get("sim_loc") in loc_options else 0
            location = st.selectbox("Location Region", loc_options, index=loc_idx, key="sim_loc")

        with f4:
            ben_idx = 0 if st.session_state.get("sim_new_ben", "No") == "No" else 1
            new_beneficiary = st.radio("Is New Beneficiary?", ["No", "Yes"], index=ben_idx, key="sim_new_ben")
            time_opts = ["Business Hours", "Late Night", "Weekend"]
            time_idx = time_opts.index(st.session_state.get("sim_time_window", "Business Hours")) if st.session_state.get("sim_time_window") in time_opts else 0
            time_window = st.selectbox("Time Window", time_opts, index=time_idx, key="sim_time_window")
            fraud_idx = 0 if st.session_state.get("sim_prev_fraud", "No") == "No" else 1
            previous_fraud_flag = st.radio("Previous Fraud History?", ["No", "Yes"], index=fraud_idx, key="sim_prev_fraud")

    # Balance Consistency Informative Advisories
    if txn_type in ["TRANSFER", "CASH_OUT"]:
        expected_new_orig = max(0.0, old_balance_orig - amount)
        if abs(new_balance_orig - expected_new_orig) > 0.01:
            st.warning(f"⚠️ **Sender Balance Advisory**: For {txn_type}, Sender Old Balance (${old_balance_orig:,.2f}) minus Amount (${amount:,.2f}) equals ${expected_new_orig:,.2f}, but current input specifies ${new_balance_orig:,.2f}.")

    if txn_type in ["TRANSFER", "CASH_IN"]:
        expected_new_dest = old_balance_dest + amount
        if abs(new_balance_dest - expected_new_dest) > 0.01:
            st.warning(f"⚠️ **Receiver Balance Advisory**: For {txn_type}, Receiver Old Balance (${old_balance_dest:,.2f}) plus Amount (${amount:,.2f}) equals ${expected_new_dest:,.2f}, but current input specifies ${new_balance_dest:,.2f}.")

    submit_btn = st.button("⚡ Analyze Payment Transaction", type="primary", use_container_width=True)

    # ==========================================
    # 3. LIVE INFERENCE EXECUTION & VALIDATION
    # ==========================================
    txn_payload = {
        "transaction_id": txn_id,
        "customer_id": customer_id,
        "beneficiary_id": beneficiary_id,
        "amount": amount,
        "old_balance_orig": old_balance_orig,
        "new_balance_orig": new_balance_orig,
        "old_balance_dest": old_balance_dest,
        "new_balance_dest": new_balance_dest,
        "transaction_type": txn_type,
        "velocity_6h": velocity_6h,
        "device_type": device_type,
        "location": location,
        "is_new_beneficiary": 1 if new_beneficiary == "Yes" else 0,
        "is_late_night": 1 if time_window == "Late Night" else 0,
        "beneficiary_fraud_history_flag": 1 if previous_fraud_flag == "Yes" else 0,
    }

    if submit_btn:
        # Inline Validation
        is_valid, validation_errors = validate_transaction(txn_payload)
        if not is_valid:
            st.error(f"❌ Transaction Input Validation Failed: {', '.join(validation_errors)}")
            return

        with st.spinner("🔍 Running GuidedGuard Real ML Model & XAI Engine..."):
            result = predict_single_transaction(txn_payload, include_xai=True)
            st.session_state["simulator_result"] = result
            st.session_state["simulator_active_payload"] = txn_payload

        # Append expanded result record to session history
        st.session_state["simulation_history"].append({
            "Transaction_ID": txn_id,
            "Customer_ID": customer_id,
            "Amount ($)": amount,
            "Type": txn_type,
            "Prediction": result.get("prediction", "Legitimate"),
            "Scam_Probability": result.get("scam_probability", 0.0),
            "Risk Score": result.get("risk_score", 0),
            "Risk Level": result.get("risk_level", "LOW"),
            "Recommendation": result.get("banking_recommendation", {}).get("action", "Approve"),
            "Device": device_type,
            "Region": location,
            "Velocity": velocity_6h,
            "Beneficiary Status": "New Beneficiary" if new_beneficiary == "Yes" else "Known Beneficiary",
            "Previous Fraud History": previous_fraud_flag,
            "Model Version": "v1.2.0 (Dual Engine)",
            "Latency (ms)": result.get("latency_ms", 45.0),
            "Timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        })

    result = st.session_state.get("simulator_result")
    if result is not None:
        active_payload = st.session_state.get("simulator_active_payload", txn_payload)
        if (
            active_payload.get("amount") != amount
            or active_payload.get("old_balance_orig") != old_balance_orig
            or active_payload.get("new_balance_orig") != new_balance_orig
            or active_payload.get("old_balance_dest") != old_balance_dest
            or active_payload.get("new_balance_dest") != new_balance_dest
        ):
            st.caption("ℹ️ *Transaction values modified since last run. Click '⚡ Analyze Payment Transaction' to update analysis.*")

        st.markdown("---")
        render_timeline_steps(current_step=6)

        # ==========================================
        # 4. PREDICTION RESULTS & DUAL ENGINE OUTPUT
        # ==========================================
        st.markdown("### 🎯 2. Behavioral Profile & Risk Assessment Results")

        pred_str = result.get("prediction", "Legitimate")
        risk_score = result.get("risk_score", 0)
        risk_level = result.get("risk_level", "LOW")
        scam_prob = result.get("scam_probability", 0.0)
        conf_pct = result.get("confidence_pct", 98.0)
        latency_ms = result.get("latency_ms", 45.0)
        rec_obj = result.get("banking_recommendation", {})
        risk_bd = result.get("risk_score_breakdown", {})
        timing_bd = result.get("latency_breakdown", {})
        devs = result.get("behavioral_deviations", {})

        # Display Banking Action Recommendation Banner
        render_banking_recommendation_card(rec_obj)

        # BEHAVIORAL PROFILE PANEL
        st.markdown("#### 👤 Customer Behavioral Profile vs Observed Transaction")
        bp1, bp2, bp3, bp4 = st.columns(4)
        with bp1:
            st.metric("Historical Typical Amount", f"${devs.get('user_baseline_avg', 2500.0):,.2f}")
            st.metric("Current Submitted Amount", f"${amount:,.2f}")
        with bp2:
            st.metric("Amount Deviation Ratio", f"{devs.get('amount_ratio', 1.0):.1f}x")
            st.metric("Baseline Frequency", "2 txns / day")
        with bp3:
            st.metric("Beneficiary Status", "Newly Added" if result["raw_payload"].get("is_new_beneficiary") else "Established")
            st.metric("Observed Velocity (6h)", f"{result['raw_payload'].get('velocity_6h', 1)} txns")
        with bp4:
            st.metric("Client Device Status", "Recognized" if "Mobile" in str(device_type) else "Proxy / Novel Device")
            st.metric("Temporal Window", "Business Hours" if not result["raw_payload"].get("is_late_night") else "Late Night Anomaly")

        st.markdown("---")

        # MODEL & DUAL ENGINE OUTPUT
        st.markdown("#### ⚙️ Dual Engine Machine Learning & Anomaly Output")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Supervised Model Score", f"{result.get('model_risk_score', 0):.1f} / 100")
        with m_col2:
            st.metric("Anomaly Score (IsoForest)", f"{result.get('anomaly_score', 0):.1f} / 100")
        with m_col3:
            st.metric("Behavioral Deviation", f"{result.get('behavioral_score', 0):.1f} / 100")
        with m_col4:
            st.metric("Final Fused Risk Score", f"{risk_score} / 100", delta=risk_level)

        # Visual Gauge
        res_col1, res_col2 = st.columns([1, 1])
        with res_col1:
            st.markdown(f"**Classification Decision**: `{pred_str}`")
            st.markdown(f"**Calibrated Fraud Probability**: `{scam_prob * 100:.2f}%`")
            st.markdown(f"**Model Confidence**: `{conf_pct:.2f}%`")
            st.markdown(f"**Total Inference Latency**: `{latency_ms:.2f} ms`")
        with res_col2:
            fig_risk = render_gauge_chart("Scam Risk Score Index", float(risk_score))
            st.plotly_chart(fig_risk, use_container_width=True)

        st.markdown("---")

        # 8-Component Breakdown
        render_risk_score_breakdown_panel(risk_bd)
        st.markdown("---")
        render_timing_breakdown_panel(timing_bd)

        st.markdown("---")

        # ==========================================
        # 5. EXPLAINABLE AI: WHY WAS THIS FLAGGED?
        # ==========================================
        st.markdown("### 🔍 3. Explainable AI: Why Was This Risk Score Assigned?")

        # Natural Language Narrative
        narr = result.get("natural_language_explanation", {})
        if narr:
            render_glass_card(
                f"Plain English Explanation ({txn_id})",
                f"**{narr.get('headline', '')}**\n\n"
                + "**Primary Risk Drivers**:\n"
                + "\n".join([f"- {r}" for r in narr.get("primary_reasons", [])])
                + (f"\n\n**Safe Baseline Indicators**:\n" + "\n".join([f"- {p}" for p in narr.get("positive_indicators", [])]) if narr.get("positive_indicators") else "")
            )

        # Counterfactual Recourse Table
        st.markdown("#### 🔄 Actionable Counterfactual Recourse Simulation")
        cfs = result.get("counterfactual_analysis", {}).get("scenarios", [])
        if cfs:
            cf_df = pd.DataFrame([
                {
                    "Actionable Lever": c["lever"],
                    "Current Input": c["current_state"],
                    "Simulated Recourse": c["simulated_state"],
                    "Estimated Fused Risk": f"{c['estimated_risk_score']}/100 ({c['estimated_risk_level']})",
                    "Risk Drop": f"-{c['risk_reduction_points']} pts",
                }
                for c in cfs
            ])
            st.dataframe(cf_df, use_container_width=True)
            st.caption("ℹ️ Counterfactual simulation only. Illustrates decision boundary sensitivity without guaranteeing real-world safety.")

        col_shap_table, col_lime_table = st.columns(2)

        with col_shap_table:
            st.markdown("#### 📊 Top 10 SHAP Feature Contributions")
            top_factors = result.get("top_risk_factors", [])
            if top_factors:
                df_shap = pd.DataFrame([
                    {
                        "Feature Name": f.get("feature_name", f.get("feature")),
                        "Actual Value": f.get("actual_value", "0"),
                        "SHAP Value": f"{f.get('shap_value', f.get('impact', 0)):+.4f}",
                        "Contrib %": f"{f.get('contribution_pct', 0):.2f}%",
                        "Direction": f.get("direction"),
                        "Impact": f.get("impact_level", "Medium"),
                    }
                    for f in top_factors[:10]
                ])
                st.dataframe(df_shap, use_container_width=True)
            else:
                st.info("Extracting top 10 SHAP feature attributions...")

        with col_lime_table:
            st.markdown("#### 🍋 LIME Decision Rules Explanation Table")
            lime_table = result.get("lime_table", [])
            if lime_table:
                df_lime = pd.DataFrame([
                    {
                        "Decision Rule": l.get("decision_rule"),
                        "Weight": f"{l.get('rule_weight', 0):+.4f}",
                        "Effect": l.get("effect"),
                        "Explanation": l.get("explanation"),
                    }
                    for l in lime_table[:10]
                ])
                st.dataframe(df_lime, use_container_width=True)
            else:
                st.info("Extracting local LIME surrogate rules...")

        st.markdown("---")

        # ==========================================
        # 8. FRESH SHAP & LIME VISUAL PREVIEWS
        # ==========================================
        st.markdown("### 🖼️ 5. Fresh SHAP & LIME Visual Explanation Previews")
        xai_col1, xai_col2, xai_col3 = st.columns(3)

        shap_plots = result.get("shap_plots", {})
        lime_plots = result.get("lime_plots", {})

        summary_path = shap_plots.get("summary_plot_png", str(config.OUTPUTS_DIR / "reports" / "xai" / "shap_summary_plot.png"))
        waterfall_path = shap_plots.get("waterfall_plot_png", str(config.OUTPUTS_DIR / "reports" / "xai" / f"shap_waterfall_{txn_id}.png"))
        lime_path = lime_plots.get("lime_plot_png", str(config.OUTPUTS_DIR / "reports" / "xai" / f"lime_explanation_{txn_id}.png"))

        with xai_col1:
            st.markdown("**Global SHAP Summary**")
            if Path(summary_path).exists():
                st.image(str(summary_path), use_container_width=True)
            else:
                st.info("Global SHAP Summary plot generating...")

        with xai_col2:
            st.markdown(f"**Local SHAP Waterfall ({txn_id})**")
            if Path(waterfall_path).exists():
                st.image(str(waterfall_path), use_container_width=True)
            else:
                st.info("Local SHAP Waterfall plot generating...")

        with xai_col3:
            st.markdown(f"**Local LIME Decision Rules ({txn_id})**")
            if Path(lime_path).exists():
                st.image(str(lime_path), use_container_width=True)
            else:
                st.info("Local LIME Decision plot generating...")

        st.markdown("---")

        # ==========================================
        # 9. EXPORT PREDICTION & REPORT DOWNLOADS
        # ==========================================
        st.markdown("### ⬇️ 6. Export Prediction Reports")
        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            pdf_path_str = result.get("pdf_report_path", "")
            if pdf_path_str and Path(pdf_path_str).exists():
                with open(pdf_path_str, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download Official Banking PDF Report",
                        data=pdf_file.read(),
                        file_name=f"GuidedGuard_Banking_Report_{txn_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            else:
                st.info("Generating Banking PDF Report...")

        with exp_col2:
            report_json_str = json.dumps(result, indent=4, default=str)
            st.download_button(
                label="⚙️ Download Complete Prediction JSON Report",
                data=report_json_str,
                file_name=f"prediction_report_{txn_id}.json",
                mime="application/json",
                use_container_width=True,
            )

        with exp_col3:
            single_df = pd.DataFrame([{
                "Transaction_ID": txn_id,
                "Prediction": pred_str,
                "Scam_Probability": scam_prob,
                "Confidence_Pct": conf_pct,
                "Risk_Score": risk_score,
                "Risk_Level": risk_level,
                "Recommendation": rec_obj.get("action", "Approve"),
                "Latency_MS": latency_ms,
                "Timestamp": result.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            }])
            st.download_button(
                label="📊 Download Risk Assessment CSV Summary",
                data=single_df.to_csv(index=False),
                file_name=f"risk_summary_{txn_id}.csv",
                mime="text/csv",
                use_container_width=True,
            )


    # ==========================================
    # 10. SIMULATED PREDICTION SESSION AUDIT HISTORY
    # ==========================================
    if st.session_state["simulation_history"]:
        st.markdown("---")
        st.markdown("### 📜 Session Simulation History (Expanded Audit Logs)")
        hist_df = pd.DataFrame(st.session_state["simulation_history"]).tail(10)
        st.dataframe(hist_df, use_container_width=True)

