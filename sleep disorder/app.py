"""
Sleep Disorder AI - Main Application Entry Point
Flask Application Factory & Core Server
"""
import os
from flask import Flask, render_template, session, g
from config import Config
from database.database import init_db, db, User
from routes import auth_bp, user_bp, prediction_bp, chatbot_bp, admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite Database & default admin seed
    init_db(app)

    # Register application blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(admin_bp)

    # Context processor to provide user details to templates
    @app.context_processor
    def inject_user():
        current_user = None
        if "user_id" in session:
            try:
                current_user = db.session.get(User, session["user_id"])
            except Exception:
                current_user = None
        return dict(current_user=current_user)

    # Public Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
