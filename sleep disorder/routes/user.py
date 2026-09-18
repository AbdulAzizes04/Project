"""
User Dashboard & Assessment History Blueprint
"""
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import io
from database.models import db, Assessment, User
from routes.auth_helpers import login_required
from services.report_service import ReportService

user_bp = Blueprint("user", __name__)

@user_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.assessment_date.desc()).all()
    
    total_assessments = len(assessments)
    latest_assessment = assessments[0] if assessments else None
    
    latest_result = latest_assessment.predicted_class if latest_assessment else "No Assessments Yet"
    latest_confidence = latest_assessment.confidence if latest_assessment else 0.0
    latest_date = latest_assessment.assessment_date.strftime("%b %d, %Y") if latest_assessment else "N/A"
    
    if latest_result == "None":
        current_risk = "Optimal / Low Risk"
        risk_color = "success"
    elif latest_result == "Insomnia":
        current_risk = "Moderate Risk (Insomnia)"
        risk_color = "warning"
    elif latest_result == "Sleep Apnea":
        current_risk = "Elevated Risk (Sleep Apnea)"
        risk_color = "danger"
    else:
        current_risk = "Not Screened"
        risk_color = "secondary"
        
    return render_template(
        "dashboard.html",
        user=user,
        total_assessments=total_assessments,
        latest_assessment=latest_assessment,
        latest_result=latest_result,
        latest_confidence=latest_confidence,
        latest_date=latest_date,
        current_risk=current_risk,
        risk_color=risk_color,
        recent_assessments=assessments[:5]
    )

@user_bp.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.assessment_date.desc()).all()
    return render_template("history.html", user=user, assessments=assessments)

@user_bp.route("/assessment/<int:id>")
@login_required
def view_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != session["user_id"] and session.get("user_role") != "admin":
        flash("Access unauthorized.", "danger")
        return redirect(url_for("user.dashboard"))
        
    input_data = json.loads(assessment.input_data)
    probabilities = {p.class_name: round(p.probability, 1) for p in assessment.predictions}
    
    return render_template(
        "result.html",
        assessment=assessment,
        input_data=input_data,
        probabilities=probabilities
    )

@user_bp.route("/assessment/<int:id>/download")
@login_required
def download_pdf(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != session["user_id"] and session.get("user_role") != "admin":
        flash("Access unauthorized.", "danger")
        return redirect(url_for("user.dashboard"))
        
    user = db.session.get(User, assessment.user_id)
    pdf_bytes = ReportService.generate_assessment_pdf(assessment, user)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"SleepAI_Assessment_Report_{assessment.id}.pdf"
    )

# ==================== JSON REST APIs ====================

@user_bp.route("/api/history", methods=["GET"])
@login_required
def api_history():
    user_id = session["user_id"]
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.assessment_date.desc()).all()
    return jsonify({
        "total": len(assessments),
        "assessments": [a.to_dict() for a in assessments]
    }), 200

@user_bp.route("/api/assessment/<int:id>", methods=["GET"])
@login_required
def api_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != session["user_id"] and session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(assessment.to_dict()), 200
