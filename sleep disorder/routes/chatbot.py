"""
AI Chatbot Assistant Blueprint
"""
import json
from flask import Blueprint, render_template, request, session, jsonify
from database.models import db, Assessment, User
from services.gemini_service import GeminiService
from routes.auth_helpers import login_required

chatbot_bp = Blueprint("chatbot", __name__)
gemini_service = GeminiService()

@chatbot_bp.route("/chatbot")
@login_required
def chatbot_view():
    user_id = session["user_id"]
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    latest_assessment = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.assessment_date.desc()).first()
    return render_template("chatbot.html", user=user, latest_assessment=latest_assessment)

@chatbot_bp.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400
        
    user_id = session["user_id"]
    # Retrieve user's latest assessment context if available
    latest_assessment = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.assessment_date.desc()).first()
    context = None
    if latest_assessment:
        input_dict = json.loads(latest_assessment.input_data) if isinstance(latest_assessment.input_data, str) else latest_assessment.input_data
        context = {
            "predicted_class": latest_assessment.predicted_class,
            "confidence": latest_assessment.confidence,
            "top_features": [e.to_dict() for e in latest_assessment.explanations],
            "Age": input_dict.get("Age"),
            "Sleep Duration": input_dict.get("Sleep Duration"),
            "Stress Level": input_dict.get("Stress Level")
        }
        
    response_text = gemini_service.chat(user_message, assessment_context=context)
    
    return jsonify({
        "response": response_text,
        "context_used": bool(context)
    }), 200
