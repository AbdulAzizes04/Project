"""
Authentication Blueprint - User login, registration, logout, profile
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.models import db, User
from routes.auth_helpers import login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("user.dashboard"))
        
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")
            
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("An account with this email already exists.", "warning")
            return render_template("register.html")
            
        user = User(name=name, email=email, role="user")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_role"] = user.role
        flash("Registration successful! Welcome to SleepAI.", "success")
        return redirect(url_for("user.dashboard"))
        
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("user.dashboard"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            if user.role == "admin":
                return redirect(next_page or url_for("admin.dashboard"))
            return redirect(next_page or url_for("user.dashboard"))
            
        flash("Invalid email or password. Please try again.", "danger")
        
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out securely.", "info")
    return redirect(url_for("index"))

@auth_bp.route("/profile")
@login_required
def profile():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    return render_template("profile.html", user=user)

# ==================== JSON REST APIs ====================

@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered"}), 409
        
    user = User(name=name, email=email, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
        
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role
    
    return jsonify({
        "message": "Login successful",
        "user": user.to_dict()
    }), 200
