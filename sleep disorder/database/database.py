# Database package
from database.models import db, User, Assessment, Prediction, Explanation, Recommendation

def init_db(app):
    """Initializes SQLAlchemy database tables and default admin account."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Seed default admin if not exists
        admin = User.query.filter_by(email="admin@sleepai.org").first()
        if not admin:
            admin = User(
                name="Clinical Administrator",
                email="admin@sleepai.org",
                role="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            
        # Seed demo patient user if not exists
        demo_user = User.query.filter_by(email="demo@sleepai.org").first()
        if not demo_user:
            demo_user = User(
                name="John Doe",
                email="demo@sleepai.org",
                role="user"
            )
            demo_user.set_password("demo123")
            db.session.add(demo_user)
            
        db.session.commit()
