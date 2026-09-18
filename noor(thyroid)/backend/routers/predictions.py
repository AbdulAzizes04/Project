"""
Predictions Router — Full prediction pipeline
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db, Prediction, Notification
from schemas import PredictionInput, PredictionOut
from services.ml_service import ml_service
from services.shap_service import compute_shap_values, get_feature_importance, generate_natural_language_explanation
from services.lime_service import compute_lime_explanation

router = APIRouter()

RECOMMENDATIONS = {
    "Hypothyroidism": {
        "treatment": [
            "Levothyroxine (synthetic T4) therapy as prescribed by endocrinologist",
            "Regular TSH monitoring every 6–12 weeks during dose adjustment",
            "Annual thyroid function tests once stable",
        ],
        "lifestyle": [
            "Maintain regular sleep schedule (7–9 hours)",
            "Manage stress through mindfulness or yoga",
            "Avoid excess iodine supplementation without medical advice",
        ],
        "diet": [
            "Adequate selenium intake (Brazil nuts, sunflower seeds)",
            "Avoid raw goitrogenic foods in excess (broccoli, cabbage, soy)",
            "Maintain adequate iodine through iodized salt",
            "Iron-rich foods to support energy levels",
        ],
        "exercise": [
            "Low-impact aerobic exercise: 30 min walking, 5×/week",
            "Gentle yoga and stretching for fatigue management",
            "Gradually increase intensity as energy improves",
        ],
        "followup": "Follow-up in 6–8 weeks after starting or adjusting levothyroxine. Annual monitoring when stable.",
        "referral": "Refer to Endocrinologist for hormone management. Nutritionist for dietary support."
    },
    "Hyperthyroidism": {
        "treatment": [
            "Anti-thyroid medications (Methimazole or PTU) as prescribed",
            "Beta-blockers (Propranolol) to control symptoms like palpitations",
            "Radioactive iodine therapy or thyroidectomy if medication fails",
        ],
        "lifestyle": [
            "Avoid caffeine and stimulants that worsen palpitations",
            "Practice stress-reduction techniques (meditation, deep breathing)",
            "Use sunscreen — hyperthyroid patients may have photosensitivity",
        ],
        "diet": [
            "Avoid excess iodine (seafood, iodized salt) during treatment",
            "High-calorie, nutrient-dense foods to compensate for rapid metabolism",
            "Calcium and Vitamin D supplementation to prevent bone loss",
        ],
        "exercise": [
            "Moderate low-intensity exercise only — avoid strenuous activity",
            "Swimming or gentle cycling when symptom-controlled",
            "Avoid exercise in heat — patient may overheat easily",
        ],
        "followup": "Follow-up in 4–6 weeks to assess medication response. Thyroid function tests every 4 weeks initially.",
        "referral": "Urgent referral to Endocrinologist. Ophthalmologist if Graves' disease suspected."
    },
    "Thyroid Nodules": {
        "treatment": [
            "Ultrasound-guided fine needle aspiration (FNA) biopsy if nodule >1cm",
            "Thyroid hormone suppression therapy in selected cases",
            "Surgical resection if malignancy suspected or nodule is large",
        ],
        "lifestyle": [
            "Avoid radiation exposure to neck area",
            "Regular self-examination of neck for changes",
            "Notify doctor immediately if nodule grows or causes symptoms",
        ],
        "diet": [
            "Adequate selenium and zinc for thyroid health",
            "Anti-inflammatory diet rich in fruits and vegetables",
            "Limit processed foods and refined sugars",
        ],
        "exercise": [
            "Regular moderate exercise to boost immunity",
            "30–45 min aerobic exercise 4–5×/week",
            "Avoid heavy neck straining exercises if nodule is large",
        ],
        "followup": "Repeat ultrasound in 6–12 months. Annual monitoring for stable benign nodules.",
        "referral": "Refer to ENT or Thyroid Surgeon for biopsy. Oncologist if malignancy confirmed."
    },
    "Healthy": {
        "treatment": [
            "No pharmacological treatment required at this time",
            "Maintain current healthy lifestyle",
        ],
        "lifestyle": [
            "Annual thyroid function screening, especially if family history present",
            "Avoid unnecessary radiation exposure",
            "Manage stress effectively",
        ],
        "diet": [
            "Balanced diet with adequate iodine through iodized salt",
            "Include selenium-rich foods (eggs, tuna, sunflower seeds)",
            "Stay well hydrated",
        ],
        "exercise": [
            "150 min moderate aerobic activity per week",
            "Strength training 2×/week",
            "Regular yoga or stretching",
        ],
        "followup": "Routine annual health checkup. Thyroid function test every 3–5 years or if symptoms develop.",
        "referral": "No referral needed at this time. General Practitioner for routine care."
    }
}


@router.post("/", response_model=dict)
async def run_prediction(req: PredictionInput, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Run ensemble ML prediction with SHAP and LIME."""
    # Generate patient_id if not provided
    patient_id = req.patient_id or f"PAT-{str(uuid.uuid4())[:8].upper()}"

    # ML Prediction
    input_dict = req.dict()
    ml_result = ml_service.predict(input_dict)
    condition = ml_result["predicted_condition"]
    confidence = ml_result["confidence"]
    risk_level = ml_result["risk_level"]
    X_scaled = ml_result["X_scaled"]
    X_raw = ml_result["X_raw"]
    mc = ml_result["model_confidences"]

    # SHAP values
    shap_vals = {}
    feature_imp = {}
    if ml_service.models_loaded and "rf" in ml_service.models:
        try:
            shap_vals = compute_shap_values(ml_service.models["rf"], X_scaled, "rf")
            feature_imp = get_feature_importance(ml_service.models["rf"], "rf")
        except Exception as e:
            print(f"[SHAP] {e}")

    if not shap_vals:
        # Fallback: use heuristic
        from services.shap_service import _mock_shap
        shap_vals = _mock_shap(X_scaled)
        feature_imp = shap_vals

    # LIME explanation
    lime_exp = []
    if ml_service.models_loaded and "rf" in ml_service.models:
        try:
            lime_exp = compute_lime_explanation(ml_service.models["rf"], X_scaled, X_raw)
        except Exception as e:
            print(f"[LIME] {e}")

    if not lime_exp:
        from services.lime_service import _mock_lime
        lime_exp = _mock_lime(X_raw)

    # Natural language explanation
    nl_exp = generate_natural_language_explanation(condition, confidence, shap_vals, input_dict)

    # Recommendations
    recs = RECOMMENDATIONS.get(condition, RECOMMENDATIONS["Healthy"])

    # Save to DB
    pred = Prediction(
        patient_id=patient_id,
        patient_name=req.name,
        input_data=input_dict,
        predicted_condition=condition,
        confidence=confidence,
        risk_level=risk_level,
        rf_confidence=mc.get("rf", 0),
        xgb_confidence=mc.get("xgb", 0),
        lgbm_confidence=mc.get("lgbm", 0),
        svm_confidence=mc.get("svm", 0),
        ann_confidence=mc.get("ann", 0),
        shap_values=shap_vals,
        lime_explanation=lime_exp,
        feature_importance=feature_imp,
        natural_language_explanation=nl_exp,
        treatment_suggestions=recs["treatment"],
        lifestyle_advice=recs["lifestyle"],
        diet_recommendations=recs["diet"],
        exercise_recommendations=recs["exercise"],
        followup_recommendation=recs["followup"],
        referral_suggestion=recs["referral"],
        doctor_notes=req.doctor_notes,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    # Add notification for high risk
    if risk_level == "High":
        notif = Notification(
            title=f"⚠️ High Risk Alert: {req.name}",
            message=f"Patient {req.name} ({patient_id}) has been classified as HIGH RISK for {condition} with {confidence:.1f}% confidence.",
            type="danger"
        )
        db.add(notif)
        db.commit()

    return {
        "id": pred.id,
        "patient_id": patient_id,
        "patient_name": req.name,
        "predicted_condition": condition,
        "confidence": confidence,
        "risk_level": risk_level,
        "model_confidences": mc,
        "shap_values": shap_vals,
        "feature_importance": dict(list(feature_imp.items())[:15]),
        "lime_explanation": lime_exp,
        "natural_language_explanation": nl_exp,
        "treatment_suggestions": recs["treatment"],
        "lifestyle_advice": recs["lifestyle"],
        "diet_recommendations": recs["diet"],
        "exercise_recommendations": recs["exercise"],
        "followup_recommendation": recs["followup"],
        "referral_suggestion": recs["referral"],
        "created_at": pred.created_at.isoformat(),
    }


@router.get("/")
async def list_predictions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return [_serialize(p) for p in preds]


@router.get("/stats")
async def prediction_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total = db.query(Prediction).count()
    high_risk = db.query(Prediction).filter(Prediction.risk_level == "High").count()
    today = db.query(Prediction).filter(
        func.date(Prediction.created_at) == datetime.utcnow().date()
    ).count()
    by_condition = db.query(
        Prediction.predicted_condition, func.count(Prediction.id)
    ).group_by(Prediction.predicted_condition).all()
    return {
        "total": total,
        "high_risk": high_risk,
        "today": today,
        "by_condition": {k: v for k, v in by_condition}
    }


@router.get("/{pred_id}")
async def get_prediction(pred_id: int, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.id == pred_id).first()
    if not pred:
        raise HTTPException(404, "Prediction not found")
    return _serialize(pred)


@router.delete("/{pred_id}")
async def delete_prediction(pred_id: int, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.id == pred_id).first()
    if not pred:
        raise HTTPException(404, "Prediction not found")
    db.delete(pred)
    db.commit()
    return {"detail": "Deleted"}


def _serialize(p: Prediction):
    return {
        "id": p.id,
        "patient_id": p.patient_id,
        "patient_name": p.patient_name,
        "predicted_condition": p.predicted_condition,
        "confidence": p.confidence,
        "risk_level": p.risk_level,
        "model_confidences": {
            "rf": p.rf_confidence, "xgb": p.xgb_confidence,
            "lgbm": p.lgbm_confidence, "svm": p.svm_confidence, "ann": p.ann_confidence
        },
        "shap_values": p.shap_values or {},
        "feature_importance": p.feature_importance or {},
        "lime_explanation": p.lime_explanation or [],
        "natural_language_explanation": p.natural_language_explanation or "",
        "treatment_suggestions": p.treatment_suggestions or [],
        "lifestyle_advice": p.lifestyle_advice or [],
        "diet_recommendations": p.diet_recommendations or [],
        "exercise_recommendations": p.exercise_recommendations or [],
        "followup_recommendation": p.followup_recommendation or "",
        "referral_suggestion": p.referral_suggestion or "",
        "doctor_notes": p.doctor_notes or "",
        "report_path": p.report_path or "",
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "input_data": p.input_data or {},
    }
