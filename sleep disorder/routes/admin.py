"""
Administrator Analytics Blueprint
"""
import os
import json
from collections import Counter
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.models import db, User, Assessment, Prediction
from routes.auth_helpers import admin_required
from config import Config

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session and session.get("user_role") == "admin":
        return redirect(url_for("admin.dashboard"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()
        if user and user.role == "admin" and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            flash("Welcome to the Admin Control Panel.", "success")
            return redirect(url_for("admin.dashboard"))
            
        flash("Invalid administrator credentials.", "danger")
        
    return render_template("admin/login.html")

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.filter_by(role="user").count()
    total_assessments = Assessment.query.count()
    assessments = Assessment.query.order_by(Assessment.assessment_date.desc()).all()
    
    # Class distribution
    disorder_counts = Counter([a.predicted_class for a in assessments])
    most_common = disorder_counts.most_common(1)
    top_disorder = most_common[0][0] if most_common else "N/A"
    
    # Read model metrics
    metrics = {}
    if os.path.exists(Config.METRICS_PATH):
        with open(Config.METRICS_PATH, "r") as f:
            metrics = json.load(f)
            
    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_assessments=total_assessments,
        top_disorder=top_disorder,
        disorder_counts=dict(disorder_counts),
        recent_assessments=assessments[:10],
        metrics=metrics
    )

@admin_bp.route("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)

@admin_bp.route("/model-performance")
@admin_required
def model_performance():
    metrics = {}
    if os.path.exists(Config.METRICS_PATH):
        with open(Config.METRICS_PATH, "r") as f:
            metrics = json.load(f)
    return render_template("admin/model_performance.html", metrics=metrics)

# ==================== JSON REST APIs ====================

@admin_bp.route("/api/statistics", methods=["GET"])
@admin_required
def api_statistics():
    total_users = User.query.filter_by(role="user").count()
    total_assessments = Assessment.query.count()
    assessments = Assessment.query.all()
    counts = Counter([a.predicted_class for a in assessments])
    
    return jsonify({
        "total_users": total_users,
        "total_assessments": total_assessments,
        "class_distribution": dict(counts)
    }), 200

@admin_bp.route("/api/model-performance", methods=["GET"])
def api_model_performance():
    if os.path.exists(Config.METRICS_PATH):
        with open(Config.METRICS_PATH, "r") as f:
            metrics = json.load(f)
        return jsonify(metrics), 200
    return jsonify({"error": "Metrics not found"}), 404
