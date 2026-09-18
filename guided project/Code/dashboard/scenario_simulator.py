"""
Scam Scenario Simulator Page for GuidedGuard.

Specifically designed for final-year project viva demonstrations.
Provides 7 one-click predefined digital payment scenarios that illustrate
how behavioural signals, anomaly detection, and supervised ML interact
to detect patterns consistent with scam-guided / APP fraud.

Demonstration Scenarios:
1. Normal Payment (Routine coffee / grocery transfer to known friend)
2. High-Value Payment (Large furniture / appliance purchase, but known device/location)
3. New Beneficiary Transfer (First-time payment to an unfamiliar individual)
4. Rapid Velocity Burst (Repeated successive payments within minutes - coaching pattern)
5. Novel Device Access (Legitimate credentials used from an unknown VPN/proxy device)
6. Unusual Geographic Location (Cross-border foreign proxy connection)
7. Combined High-Risk APP Scam (Urgent high-value transfer + new payee + rapid velocity + proxy)
"""

from typing import Dict, Any
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import config
from models.predict import predict_single_transaction
from dashboard.components import (
    render_header_status_bar,
    render_glass_card,
    render_gauge_chart,
    render_risk_badge,
)

PREDEFINED_SCENARIOS = {
    "1. Normal Everyday Payment": {
        "description": "Routine small-value transfer to a known domestic contact during business hours.",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-01",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "BOB-FRIEND-202",
            "amount": 1250.0,
            "old_balance_orig": 15000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 0,
            "device_type": "Mobile App",
            "location": "Domestic Home",
            "velocity_6h": 1,
            "hour": 14,
            "is_late_night": 0,
        },
        "expected_risk": "LOW",
        "demonstration_focus": "Baseline calibration and approval without friction.",
    },
    "2. High-Value Purchase (Single Anomaly)": {
        "description": "Unusually high amount ($45,000), but initiated from customer's regular device, domestic network, and daytime.",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-02",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "M-APPLE-STORE",
            "amount": 45000.0,
            "old_balance_orig": 80000.0,
            "transaction_type": "PAYMENT",
            "is_new_beneficiary": 0,
            "device_type": "Mobile App",
            "location": "Domestic Home",
            "velocity_6h": 1,
            "hour": 15,
            "is_late_night": 0,
        },
        "expected_risk": "MEDIUM",
        "demonstration_focus": "Amount deviation triggers warning without false-blocking.",
    },
    "3. Newly Added Beneficiary": {
        "description": "Payment sent to a recipient registered 5 minutes ago with zero prior transaction history.",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-03",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "NEW-RECIPIENT-999",
            "amount": 12000.0,
            "old_balance_orig": 30000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 1,
            "device_type": "Mobile App",
            "location": "Domestic Home",
            "velocity_6h": 1,
            "hour": 11,
            "is_late_night": 0,
        },
        "expected_risk": "MEDIUM / HIGH",
        "demonstration_focus": "Payee novelty evaluation and cooling-off prompt.",
    },
    "4. Rapid Velocity Burst": {
        "description": "4th payment in 20 minutes totaling high cumulative outflow (classic fraudster coaching).",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-04",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "CRYPTO-DESK-777",
            "amount": 18000.0,
            "old_balance_orig": 40000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 1,
            "device_type": "Mobile App",
            "location": "Domestic Home",
            "velocity_6h": 9,
            "hour": 16,
            "is_late_night": 0,
        },
        "expected_risk": "HIGH",
        "demonstration_focus": "Velocity risk accumulation across rolling windows.",
    },
    "5. Novel Device Access (VPN / Proxy)": {
        "description": "Legitimate credentials used from an unknown, rooted client or commercial proxy.",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-05",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "VENDOR-303",
            "amount": 8500.0,
            "old_balance_orig": 25000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 0,
            "device_type": "Unknown Proxy",
            "location": "Domestic Home",
            "velocity_6h": 2,
            "hour": 19,
            "is_late_night": 0,
        },
        "expected_risk": "MEDIUM",
        "demonstration_focus": "Client device fingerprint anomaly detection.",
    },
    "6. Geolocation / Cross-Border Anomaly": {
        "description": "Transaction initiated via an overseas IP address outside the user's home country.",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-06",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "VENDOR-303",
            "amount": 7500.0,
            "old_balance_orig": 20000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 0,
            "device_type": "Web Browser",
            "location": "Foreign Proxy",
            "velocity_6h": 1,
            "hour": 22,
            "is_late_night": 0,
        },
        "expected_risk": "MEDIUM",
        "demonstration_focus": "Regional anomaly penalty.",
    },
    "7. Combined High-Risk APP Scam Pattern": {
        "description": "Simultaneous confluence: High amount ($95,000) + New payee + High velocity + Foreign proxy + Late night.",
        "payload": {
            "transaction_id": "DEMO-SCENARIO-07",
            "customer_id": "C-ALICE-101",
            "beneficiary_id": "MULE-ACCOUNT-888",
            "amount": 95000.0,
            "old_balance_orig": 98000.0,
            "transaction_type": "TRANSFER",
            "is_new_beneficiary": 1,
            "device_type": "Unknown Proxy",
            "location": "Foreign Proxy",
            "velocity_6h": 12,
            "hour": 3,
            "is_late_night": 1,
        },
        "expected_risk": "CRITICAL",
        "demonstration_focus": "Complete multi-signal fusion triggering immediate SOC hold and user warning.",
    },
}


def render_scenario_simulator_page():
    """
    Render interactive Scenario Simulator for project evaluation and viva demos.
    """
    render_header_status_bar(
        page_title="Scam Scenario Simulator",
        page_description="Execute pre-configured digital payment scam scenarios to demonstrate multi-signal risk fusion.",
    )

    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;">
            <h4 style="color: #38BDF8; margin: 0 0 0.5rem 0;">🎓 Final-Year Viva Demonstration Suite</h4>
            <p style="color: #94A3B8; margin: 0; font-size: 0.9rem;">
                Select any of the 7 pre-configured payment scenarios below to instantly evaluate behavioral deviations,
                supervised model outputs, unsupervised Isolation Forest anomaly scores, SHAP explanations, and counterfactuals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    scenario_name = st.selectbox("Select Demonstration Scenario:", list(PREDEFINED_SCENARIOS.keys()))
    scenario_info = PREDEFINED_SCENARIOS[scenario_name]

    col_meta1, col_meta2 = st.columns([2, 1])
    with col_meta1:
        st.markdown(f"**Scenario Context**: {scenario_info['description']}")
        st.markdown(f"**Viva Focus**: `{scenario_info['demonstration_focus']}`")
    with col_meta2:
        st.markdown(f"**Expected Risk Classification**: `{scenario_info['expected_risk']}`")

    if st.button(f"⚡ Execute Simulation: {scenario_name}", type="primary", use_container_width=True):
        with st.spinner("Analyzing scenario through GuidedGuard Dual Risk Fusion Engine..."):
            result = predict_single_transaction(scenario_info["payload"], include_xai=True)

        st.markdown("---")
        st.markdown("### 📊 Real-Time Simulation Results")

        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            st.metric("Supervised Model Score", f"{result['model_risk_score']:.1f}/100")
        with r_col2:
            st.metric("Anomaly Score (IsoForest)", f"{result['anomaly_score']:.1f}/100")
        with r_col3:
            st.metric("Behavioral Deviation", f"{result['behavioral_score']:.1f}/100")
        with r_col4:
            st.metric("Fused Risk Score", f"{result['risk_score']}/100")

        # Visual Gauge and Banking Warning
        g_col1, g_col2 = st.columns([1, 1])
        with g_col1:
            fig = render_gauge_chart("Fused Risk Score", float(result["risk_score"]))
            st.plotly_chart(fig, use_container_width=True)

        with g_col2:
            st.markdown("#### 🛡️ Simulated Security Intervention")
            inv = result["intervention"]
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.8); border: 2px solid {inv['badge_color']}; border-radius: 12px; padding: 1.25rem;">
                    <h4 style="color: {inv['badge_color']}; margin: 0 0 0.5rem 0;">{inv['dialog_title']}</h4>
                    <p style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.75rem;">
                        {inv['user_message']}
                    </p>
                    <span style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.8rem; color: #94A3B8;">
                        Cooling-off Hold: {inv['cooling_off_period_mins']} minutes
                    </span> &nbsp;
                    <span style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.8rem; color: #94A3B8;">
                        2FA Prompt: {'YES' if inv['requires_2fa_challenge'] else 'NO'}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 8-Component Breakdown Radar / Bar Chart
        st.markdown("#### 🔍 8-Signal Risk Breakdown")
        comps = result["risk_components"]
        df_comps = pd.DataFrame([
            {"Component": k.replace("_", " ").title(), "Score (0-100)": v}
            for k, v in comps.items()
        ])
        st.bar_chart(df_comps.set_index("Component"), use_container_width=True)

        # Natural Language Narrative
        st.markdown("#### 🗣️ Natural Language Banking Explanation")
        narr = result["natural_language_explanation"]
        render_glass_card(
            narr["headline"],
            "\n".join([f"- {r}" for r in narr["primary_reasons"]])
            + (f"\n\n**Positive Indicators**:\n" + "\n".join([f"- {p}" for p in narr["positive_indicators"]]) if narr["positive_indicators"] else "")
        )

        # Counterfactual Recourse
        st.markdown("#### 🔄 Counterfactual Recourse (Actionable Levers)")
        cfs = result["counterfactual_analysis"]["scenarios"]
        if cfs:
            cf_df = pd.DataFrame([
                {
                    "Actionable Lever": c["lever"],
                    "Current State": c["current_state"],
                    "Simulated Modification": c["simulated_state"],
                    "Simulated Risk": f"{c['estimated_risk_score']}/100 ({c['estimated_risk_level']})",
                    "Risk Drop": f"-{c['risk_reduction_points']} pts",
                }
                for c in cfs
            ])
            st.dataframe(cf_df, use_container_width=True)
        else:
            st.info("No counterfactual modifications required for low-risk transaction.")
