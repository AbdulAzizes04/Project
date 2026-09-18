"""
Authentication helpers and role decorators
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
from database.models import db, User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized. Please log in."}), 401
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
            
        user = db.session.get(User, session["user_id"])
        if not user:
            session.clear()
            flash("Session expired or user not found. Please log in again.", "info")
            return redirect(url_for("auth.login"))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized. Admin credentials required."}), 401
            flash("Admin authentication required.", "danger")
            return redirect(url_for("admin.login", next=request.url))
            
        user = db.session.get(User, session["user_id"])
        if not user or user.role != "admin":
            if request.path.startswith("/api/"):
                return jsonify({"error": "Forbidden. Admin privileges required."}), 403
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
