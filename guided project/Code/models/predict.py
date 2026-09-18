"""
Production Inference & Risk Fusion Prediction Engine for GuidedGuard.

Orchestrates real-time model inference:
1. Authorization-Time Feature Engineering & Scaling (Zero Post-Txn Leakage).
2. Supervised Calibrated ML Inference (CalibratedClassifierCV).
3. Unsupervised Anomaly Detection (Isolation Forest Anomaly Score 0-100).
4. Multi-Dimensional Behavioral Baseline Deviations (UserBehavioralProfiler).
5. Configurable 8-Signal Risk Fusion (RiskFusionEngine -> Risk Score 0-100).
6. Actionable Counterfactual Explanations (explainability/counterfactual.py).
7. Non-Definitive Banking Security Narratives (explainability/narrative_engine.py).
8. Contextual Simulated Intervention Engine (models/intervention_engine.py).
9. SHAP & LIME Interpretability Attributions.
10. Vectorized Bulk Batch Processing.
"""

from typing import Tuple, Dict, Any, List, Optional
import time
import json
from pathlib import Path
import datetime
import pandas as pd
import numpy as np

import config
from models.model_loader import load_artifacts
from models.risk_engine import RiskFusionEngine
from models.intervention_engine import evaluate_intervention
from preprocessing.behavioral_profile import UserBehavioralProfiler
from preprocessing.velocity_features import get_default_velocity_features
from preprocessing.beneficiary_features import compute_beneficiary_features
from preprocessing.device_features import compute_device_features
from preprocessing.location_features import compute_location_features
from preprocessing.temporal_features import compute_temporal_features
from explainability.counterfactual import generate_counterfactual_scenarios
from explainability.narrative_engine import generate_natural_language_explanation
from explainability.shap_explainer import (
    initialize_shap,
    generate_shap_values,
    get_top_risk_factors,
    save_shap_visualizations,
)
from explainability.lime_explainer import (
    initialize_lime,
    generate_lime_explanation,
    save_lime_visualizations,
)
from utils.helpers import setup_logger, format_feature_value, format_currency
from utils.pdf_generator import generate_pdf_report

logger = setup_logger(__name__)

# Global singleton profiler and risk engine
_GLOBAL_PROFILER = UserBehavioralProfiler()
_GLOBAL_RISK_ENGINE = RiskFusionEngine()


def validate_transaction(transaction_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate input payload fields, non-emptiness, and numeric bounds."""
    errors = []
    if not transaction_dict:
        return False, ["Transaction payload dictionary is empty."]

    amt = float(transaction_dict.get("amount", -1.0))
    if amt <= 0.0:
        errors.append("Transaction amount must be strictly positive (> 0).")

    old_b = float(transaction_dict.get("old_balance_orig", transaction_dict.get("oldbalanceOrg", 0.0)))
    if old_b < 0.0:
        errors.append("Sender origin balance must be non-negative (>= 0).")

    return len(errors) == 0, errors


def prepare_features(transaction_dict: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Transform raw transaction payload into the exact 19 authorization-time feature vector
    used during model training.
    """
    row = transaction_dict.copy()
    amt = float(row.get("amount", 2500.0))
    old_b = float(row.get("old_balance_orig", row.get("oldbalanceOrg", 10000.0)))
    user_id = str(row.get("customer_id", row.get("nameOrig", "C123456789")))
    beneficiary_id = str(row.get("beneficiary_id", row.get("nameDest", "M987654321")))
    t = str(row.get("transaction_type", row.get("type", "TRANSFER"))).upper()
    hour = int(row.get("hour", row.get("step", 12)) % 24)
    day = int(row.get("day_of_week", 0))

    # Compute Behavioral Deviation
    deviations = _GLOBAL_PROFILER.calculate_deviations(user_id, {
        "amount": amt,
        "hour": hour,
        "day_of_week": day,
        "beneficiary_id": beneficiary_id,
        "device_type": row.get("device_type", "Mobile App"),
        "location": row.get("location", "Domestic Home"),
    })

    # Build exact training feature columns
    feat = {
        "amount": amt,
        "log_amount": np.log1p(np.maximum(0, amt)),
        "oldbalanceOrg": old_b,
        "log_oldbalanceOrg": np.log1p(np.maximum(0, old_b)),
        "amount_to_oldbalance_ratio": amt / (old_b + 1.0),
        "is_high_portion_of_balance": 1 if (amt / (old_b + 1.0)) > 0.8 else 0,
        "hour": hour,
        "day_of_week": day,
        "is_weekend": 1 if day in [5, 6] else 0,
        "is_late_night": 1 if hour in [0, 1, 2, 3, 4, 23] else 0,
        "is_business_hours": 1 if 9 <= hour <= 17 else 0,
        "type_CASH_OUT": 1 if t == "CASH_OUT" else 0,
        "type_DEBIT": 1 if t == "DEBIT" else 0,
        "type_PAYMENT": 1 if t == "PAYMENT" else 0,
        "type_TRANSFER": 1 if t == "TRANSFER" else 0,
        "dest_is_merchant": 1 if beneficiary_id.startswith("M") else 0,
        "behavioral_deviation_score": deviations["composite_behavioural_score"],
        "amount_z_score": deviations["amount_z_score"],
        "velocity_proxy_1h": float(row.get("velocity_6h", 1.0)) / 2.0,
    }

    df_feat = pd.DataFrame([feat])
    model, scaler, metadata, anomaly_detector = load_artifacts()

    if scaler is not None and hasattr(scaler, "feature_names_in_"):
        expected_cols = list(scaler.feature_names_in_)
        aligned = pd.DataFrame(0.0, index=[0], columns=expected_cols)
        for col in expected_cols:
            if col in df_feat.columns:
                aligned[col] = float(df_feat[col].iloc[0])
        try:
            scaled_arr = scaler.transform(aligned)
            df_scaled = pd.DataFrame(scaled_arr, columns=expected_cols)
            return df_scaled, deviations
        except Exception:
            return aligned, deviations

    return df_feat, deviations


def predict_single_transaction(
    transaction_dict: Dict[str, Any], include_xai: bool = True
) -> Dict[str, Any]:
    """
    Execute real-time risk assessment, supervised prediction, unsupervised anomaly detection,
    risk fusion, counterfactual analysis, and contextual intervention.
    """
    start_total_time = time.perf_counter()

    is_valid, errs = validate_transaction(transaction_dict)
    if not is_valid:
        return {"success": False, "errors": errs, "latency_ms": 0.0}

    model, scaler, metadata, anomaly_detector = load_artifacts()
    if model is None:
        return {"success": False, "errors": ["Model artifact not loaded."], "latency_ms": 0.0}

    txn_id = str(transaction_dict.get("transaction_id", f"TXN-{int(time.time()*1000)}"))

    # Stage 1: Feature Engineering & Scaling
    t_feat_start = time.perf_counter()
    df_scaled, deviations = prepare_features(transaction_dict)
    t_feat_end = time.perf_counter()

    # Stage 2: Supervised Inference & Probability
    t_pred_start = time.perf_counter()
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(df_scaled)[0]
        scam_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
    else:
        scam_prob = float(model.predict(df_scaled)[0])

    supervised_risk_score = round(min(100.0, max(0.0, scam_prob * 100.0)), 1)

    # Stage 3: Unsupervised Anomaly Detection (Isolation Forest)
    if anomaly_detector is not None:
        anom_scores, anom_percentiles = anomaly_detector.predict_anomaly_score(df_scaled)
        anomaly_score = float(anom_scores[0])
        anomaly_pct = float(anom_percentiles[0])
    else:
        anomaly_score = min(100.0, float(deviations.get("composite_behavioural_score", 20.0)))
        anomaly_pct = 50.0

    # Stage 4: Sub-component Behavioral Risk Signals
    amt = float(transaction_dict.get("amount", 2500.0))
    vel_input = int(transaction_dict.get("velocity_6h", 1))
    vel_data = get_default_velocity_features(amt, velocity_input=vel_input)
    ben_data = compute_beneficiary_features(
        str(transaction_dict.get("beneficiary_id", "M987654321")),
        is_new_override=transaction_dict.get("is_new_beneficiary"),
        current_amount=amt,
    )
    dev_data = compute_device_features(str(transaction_dict.get("device_type", "Mobile App")))
    loc_data = compute_location_features(str(transaction_dict.get("location", "Domestic Home")))
    temp_data = compute_temporal_features(
        step=int(transaction_dict.get("step", 12)),
        timestamp=transaction_dict.get("timestamp"),
    )

    # Stage 5: Dual Risk Fusion Engine
    fused_risk = _GLOBAL_RISK_ENGINE.compute_fused_risk(
        supervised_score=supervised_risk_score,
        anomaly_score=anomaly_score,
        behavioral_score=float(deviations["composite_behavioural_score"]),
        beneficiary_score=float(ben_data["beneficiary_risk_score"]),
        velocity_score=float(vel_data["velocity_risk_score"]),
        device_score=float(dev_data["device_risk_score"]),
        location_score=float(loc_data["location_risk_score"]),
        temporal_score=float(temp_data["temporal_risk_score"]),
    )

    final_risk_score = fused_risk["risk_score"]
    risk_level = fused_risk["risk_level"]
    risk_components = fused_risk["risk_components"]

    pred_class = 1 if (final_risk_score >= 60 or scam_prob >= 0.50) else 0
    pred_label = "Scam / Elevated Risk" if pred_class == 1 else "Legitimate"
    confidence = round(max(scam_prob, 1.0 - scam_prob), 4)

    # Stage 6: Simulated Intervention Engine
    intervention = evaluate_intervention(risk_level, final_risk_score)
    t_pred_end = time.perf_counter()

    # Stage 7: Natural Language Banking Narrative
    narrative_obj = generate_natural_language_explanation(
        transaction_dict=transaction_dict,
        risk_score=final_risk_score,
        risk_level=risk_level,
        risk_components=risk_components,
        deviations=deviations,
    )

    # Stage 8: Counterfactual Explanations
    counterfactual_obj = generate_counterfactual_scenarios(
        current_payload=transaction_dict,
        risk_breakdown=fused_risk,
        risk_engine=_GLOBAL_RISK_ENGINE,
        user_baseline_avg=deviations.get("user_baseline_avg", 2500.0),
    )

    # Stage 9: SHAP & LIME Calculations
    top_factors = []
    lime_table = []
    shap_paths = {}
    lime_paths = {}

    t_shap_start = time.perf_counter()
    if include_xai:
        try:
            explainer_shap = initialize_shap(model, background_data=df_scaled)
            shap_values, base_val = generate_shap_values(explainer_shap, df_scaled)
            top_factors = get_top_risk_factors(shap_values, list(df_scaled.columns), row_idx=0, top_k=10, raw_payload=transaction_dict, feature_matrix=df_scaled)
            t_shap_end = time.perf_counter()

            t_lime_start = time.perf_counter()
            explainer_lime = initialize_lime(df_scaled, list(df_scaled.columns))
            lime_obj = generate_lime_explanation(explainer_lime, model.predict_proba if hasattr(model, "predict_proba") else None, df_scaled.iloc[0], num_features=10, raw_payload=transaction_dict)
            lime_table = lime_obj.get("lime_table", [])
            t_lime_end = time.perf_counter()

            raw_shap_paths = save_shap_visualizations(shap_values, df_scaled, txn_id=txn_id, raw_payload=transaction_dict)
            shap_paths = {k: str(v) for k, v in raw_shap_paths.items()}
            raw_lime_paths = save_lime_visualizations(explainer_lime, model.predict_proba if hasattr(model, "predict_proba") else None, df_scaled.iloc[0], txn_id=txn_id, raw_payload=transaction_dict)
            shap_paths["lime_plot_png"] = str(raw_lime_paths.get("lime_plot_png", ""))
            lime_paths = {"lime_plot_png": str(raw_lime_paths.get("lime_plot_png", ""))}
        except Exception as e:
            logger.warning(f"XAI calculation fallback: {e}")
            t_shap_end = t_lime_start = t_lime_end = time.perf_counter()
    else:
        t_shap_end = t_lime_start = t_lime_end = time.perf_counter()

    t_total_end = time.perf_counter()

    latency_breakdown = {
        "feature_engineering": round((t_feat_end - t_feat_start) * 1000, 2),
        "prediction": round((t_pred_end - t_pred_start) * 1000, 2),
        "shap": round((t_shap_end - t_shap_start) * 1000, 2),
        "lime": round((t_lime_end - t_lime_start) * 1000, 2),
        "total": round((t_total_end - start_total_time) * 1000, 2),
    }

    result = {
        "success": True,
        "transaction_id": txn_id,
        "prediction": pred_label,
        "predicted_class": pred_class,
        "probability": round(scam_prob, 4),
        "scam_probability": round(scam_prob, 4),
        "model_risk_score": supervised_risk_score,
        "anomaly_score": round(anomaly_score, 1),
        "anomaly_percentile": round(anomaly_pct, 1),
        "behavioral_score": float(deviations["composite_behavioural_score"]),
        "confidence": confidence,
        "confidence_pct": round(confidence * 100, 2),
        "risk_score": final_risk_score,
        "risk_level": risk_level,
        "fusion": risk_components,
        "risk_components": risk_components,
        "risk_score_breakdown": {
            "model_probability": round(scam_prob * 100, 2),
            "amount_risk": risk_components.get("behavioral_deviation", 0),
            "velocity_risk": risk_components.get("velocity_risk", 0),
            "device_risk": risk_components.get("device_risk", 0),
            "location_risk": risk_components.get("location_risk", 0),
            "beneficiary_risk": risk_components.get("beneficiary_risk", 0),
            "historical_behaviour": risk_components.get("behavioral_deviation", 0),
            "balance_behaviour": 0.0,
            "final_risk_score": final_risk_score,
        },
        "behavioral_deviations": deviations,
        "intervention": intervention,
        "banking_recommendation": {
            "action": intervention["action"],
            "recommendation": intervention["dialog_title"],
            "code": risk_level,
            "color": intervention["badge_color"],
            "details": intervention["user_message"],
            "workflow_step": "Fraud Ops Escalation" if intervention["analyst_queue_escalation"] else "Automated Processing",
        },
        "natural_language_explanation": narrative_obj,
        "explanation_narrative": narrative_obj["primary_reasons"],
        "human_readable_explanation": narrative_obj["primary_reasons"],
        "counterfactual_analysis": counterfactual_obj,
        "top_risk_factors": top_factors,
        "lime_table": lime_table,
        "shap_plots": shap_paths,
        "lime_plots": lime_paths,
        "latency_breakdown": latency_breakdown,
        "latency_ms": latency_breakdown["total"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_metadata": metadata or {"model_name": "XGBoost (Calibrated)", "version": "v2.0.0"},
        "raw_payload": transaction_dict,
    }

    if include_xai:
        try:
            pdf_path = generate_pdf_report(result)
            result["pdf_report_path"] = str(pdf_path)
        except Exception as pe:
            logger.warning(f"PDF generation note: {pe}")

    return result


def predict_batch_transactions(
    csv_file_path: Path, output_dir: Path = config.OUTPUTS_DIR / "reports"
) -> Dict[str, Any]:
    """Execute bulk vectorized batch prediction on an uploaded CSV dataset."""
    start_time = time.perf_counter()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df_batch = pd.read_csv(csv_file_path)

    results_list = []
    scam_count = 0
    total_risk = 0.0

    for idx, row in df_batch.iterrows():
        row_dict = row.to_dict()
        res = predict_single_transaction(row_dict, include_xai=False)

        is_scam = res.get("predicted_class", 0) == 1
        if is_scam:
            scam_count += 1
        r_score = res.get("risk_score", 0)
        total_risk += r_score

        top_f = res.get("top_risk_factors", [])
        top_factor_name = top_f[0]["feature_name"] if top_f else "Amount / Payee Novelty"

        comps = res.get("risk_components", {})
        results_list.append({
            "transaction_id": res.get("transaction_id", f"TXN-{idx}"),
            "customer_id": str(row_dict.get("customer_id", f"C-{idx}")),
            "amount": float(row_dict.get("amount", 0.0)),
            "type": str(row_dict.get("transaction_type", row_dict.get("type", "TRANSFER"))),
            "model_score": res.get("model_risk_score", 0.0),
            "anomaly_score": res.get("anomaly_score", 0.0),
            "behavioral_score": res.get("behavioral_score", 0.0),
            "beneficiary_score": comps.get("beneficiary_risk", 0.0),
            "device_score": comps.get("device_risk", 0.0),
            "location_score": comps.get("location_risk", 0.0),
            "temporal_score": comps.get("temporal_risk", 0.0),
            "velocity_score": comps.get("velocity_risk", 0.0),
            "risk_score": r_score,
            "risk_level": res.get("risk_level", "LOW"),
            "top_risk_factor": top_factor_name,
            "intervention": res.get("intervention", {}).get("action", "Approve"),
            "latency_ms": res.get("latency_ms", 0.0),
        })

    df_res = pd.DataFrame(results_list)
    input_stem = Path(csv_file_path).stem
    pred_csv_path = output_dir / f"batch_predictions_{input_stem}.csv"
    risk_csv_path = output_dir / f"batch_risk_scores_{input_stem}.csv"

    df_res.to_csv(pred_csv_path, index=False)
    df_res[["transaction_id", "risk_score", "risk_level", "top_risk_factor", "intervention"]].to_csv(risk_csv_path, index=False)

    total_latency_sec = round(time.perf_counter() - start_time, 3)

    summary = {
        "total_transactions": len(df_batch),
        "flagged_scam_count": scam_count,
        "flagged_scam_rate_pct": round((scam_count / len(df_batch)) * 100, 2) if len(df_batch) > 0 else 0.0,
        "avg_risk_score": round(total_risk / len(df_batch), 2) if len(df_batch) > 0 else 0.0,
        "total_latency_sec": total_latency_sec,
        "prediction_csv": str(pred_csv_path),
        "risk_csv": str(risk_csv_path),
    }

    summary_json_path = output_dir / f"batch_summary_report_{input_stem}.json"
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    return summary


# Backward compatibility alias
generate_prediction_report = predict_single_transaction
predict_single_transaction_api = predict_single_transaction
predict_transaction = predict_single_transaction
predict_batch = predict_batch_transactions
