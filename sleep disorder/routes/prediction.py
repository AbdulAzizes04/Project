"""
Prediction & Explainability Blueprint
"""
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.models import db, Assessment, User
from services.prediction_service import PredictionService
from routes.auth_helpers import login_required

prediction_bp = Blueprint("prediction", __name__)
prediction_service = PredictionService()

@prediction_bp.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    if request.method == "POST":
        form_data = request.form.to_dict()
        is_valid, errors = prediction_service.validate_input(form_data)
        
        if not is_valid:
            for field, err in errors.items():
                flash(f"{field}: {err}", "danger")
            return render_template("assessment.html", form_data=form_data)
            
        user_id = session["user_id"]
        try:
            result = prediction_service.process_assessment(user_id, form_data)
            flash("Assessment analyzed successfully!", "success")
            return redirect(url_for("prediction.result", id=result["assessment_id"]))
        except Exception as e:
            flash(f"Error during screening analysis: {str(e)}", "danger")
            return render_template("assessment.html", form_data=form_data)
            
    return render_template("assessment.html", form_data={})

@prediction_bp.route("/result/<int:id>")
@login_required
def result(id):
    assessment = Assessment.query.get_or_404(id)
    # Check permissions
    if assessment.user_id != session["user_id"] and session.get("user_role") != "admin":
        flash("Access unauthorized for this assessment.", "danger")
        return redirect(url_for("user.dashboard"))
        
    input_data = json.loads(assessment.input_data)
    probabilities = {p.class_name: round(p.probability, 1) for p in assessment.predictions}
    
    return render_template(
        "result.html",
        assessment=assessment,
        input_data=input_data,
        probabilities=probabilities
    )

@prediction_bp.route("/explanation/<int:id>")
@login_required
def explanation(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != session["user_id"] and session.get("user_role") != "admin":
        flash("Access unauthorized for this assessment.", "danger")
        return redirect(url_for("user.dashboard"))
        
    input_data = json.loads(assessment.input_data)
    
    # Re-generate SHAP plot for visual display
    proc_df = prediction_service.predictor.format_input(input_data)
    X_proc = prediction_service.predictor.preprocessor.transform(proc_df)
    target_idx = {"None": 0, "Insomnia": 1, "Sleep Apnea": 2}.get(assessment.predicted_class, 0)
    shap_data = prediction_service.predictor.explainer.explain_instance(X_proc, target_idx)
    
    return render_template(
        "explanation.html",
        assessment=assessment,
        input_data=input_data,
        shap_data=shap_data
    )

@prediction_bp.route("/recommendations/<int:id>")
@login_required
def recommendations(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != session["user_id"] and session.get("user_role") != "admin":
        flash("Access unauthorized.", "danger")
        return redirect(url_for("user.dashboard"))
        
    input_data = json.loads(assessment.input_data)
    rec_text = assessment.recommendations[0].recommendation_text if assessment.recommendations else "No recommendations recorded."
    
    return render_template(
        "recommendations.html",
        assessment=assessment,
        input_data=input_data,
        recommendation_text=rec_text
    )

# ==================== JSON REST APIs ====================

@prediction_bp.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json() or {}
    
    # Check if user session exists or user_id provided in body
    user_id = session.get("user_id") or data.get("user_id")
    if not user_id:
        user = User.query.filter_by(role="user").first()
        user_id = user.id if user else 1
        
    is_valid, errors = prediction_service.validate_input(data)
    if not is_valid:
        return jsonify({"error": "Validation failed", "details": errors}), 400
        
    try:
        result = prediction_service.process_assessment(user_id, data)
        return jsonify({
            "status": "success",
            "assessment_id": result["assessment_id"],
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"],
            "risk_level": result["risk_level"],
            "model_used": result["model_used"],
            "top_shap_factors": result["explanation"]["top_features"],
            "recommendations": result["recommendations_text"],
            "disclaimer": "This system is intended for educational and preliminary screening purposes only and does not constitute a medical diagnosis."
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prediction_bp.route("/api/explanation/<int:id>", methods=["GET"])
def api_explanation(id):
    assessment = Assessment.query.get_or_404(id)
    explanations = [e.to_dict() for e in assessment.explanations]
    return jsonify({
        "assessment_id": assessment.id,
        "predicted_class": assessment.predicted_class,
        "model_name": assessment.model_name,
        "explanations": explanations
    }), 200

@prediction_bp.route("/api/recommendations", methods=["POST"])
def api_recommendations():
    data = request.get_json() or {}
    assessment_id = data.get("assessment_id")
    if assessment_id:
        assessment = db.session.get(Assessment, assessment_id)
        if assessment and assessment.recommendations:
            return jsonify({
                "assessment_id": assessment_id,
                "recommendation_text": assessment.recommendations[0].recommendation_text
            }), 200
            
    # Direct recommendation from payload
    try:
        pred_result = prediction_service.predictor.predict(data, generate_shap=True)
        recs = prediction_service.gemini_service.generate_recommendations(pred_result)
        return jsonify({
            "predicted_class": pred_result["predicted_class"],
            "confidence": pred_result["confidence"],
            "recommendation_text": recs
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prediction_bp.route("/api/gemini/status", methods=["GET"])
def api_gemini_status():
    status_info = prediction_service.gemini_service.get_status()
    return jsonify(status_info), 200
