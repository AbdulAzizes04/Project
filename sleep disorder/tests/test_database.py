"""
Tests for Database Operations and Models
"""
import pytest
from app import create_app
from database.models import db, User, Assessment, Prediction, Explanation, Recommendation

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_user_creation_and_auth(app):
    with app.app_context():
        u = User.query.filter_by(email="test_unique@example.com").first()
        if not u:
            u = User(name="Test Patient", email="test_unique@example.com", role="user")
            u.set_password("securepassword123")
            db.session.add(u)
            db.session.commit()
        
        fetched = User.query.filter_by(email="test_unique@example.com").first()
        assert fetched is not None
        assert fetched.check_password("securepassword123") is True
        assert fetched.check_password("wrongpassword") is False
        assert fetched.role == "user"
