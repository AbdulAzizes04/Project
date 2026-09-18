"""
Sleep Disorder AI - Database Models (SQLAlchemy ORM)
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assessments = db.relationship("Assessment", backref="patient", lazy=True, cascade="all, delete-orphan")

    def __init__(self, name=None, email=None, role="user", password_hash="", **kwargs):
        super().__init__(**kwargs)
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if role is not None:
            self.role = role
        if password_hash:
            self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Assessment(db.Model):
    __tablename__ = "assessments"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    input_data = db.Column(db.Text, nullable=False)  # JSON string
    predicted_class = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    model_name = db.Column(db.String(80), default="RandomForestClassifier")
    
    predictions = db.relationship("Prediction", backref="assessment", lazy=True, cascade="all, delete-orphan")
    explanations = db.relationship("Explanation", backref="assessment", lazy=True, cascade="all, delete-orphan")
    recommendations = db.relationship("Recommendation", backref="assessment", lazy=True, cascade="all, delete-orphan")

    def __init__(self, user_id=None, assessment_date=None, input_data="", predicted_class="", confidence=0.0, model_name="RandomForestClassifier", **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if assessment_date is not None:
            self.assessment_date = assessment_date
        self.input_data = input_data
        self.predicted_class = predicted_class
        self.confidence = confidence
        self.model_name = model_name

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "patient_name": self.patient.name if self.patient else "Anonymous",
            "assessment_date": self.assessment_date.strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_class": self.predicted_class,
            "confidence": round(self.confidence, 2),
            "model_name": self.model_name,
            "probabilities": {p.class_name: round(p.probability, 2) for p in self.predictions},
            "top_features": [e.to_dict() for e in self.explanations]
        }

class Prediction(db.Model):
    __tablename__ = "predictions"
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    probability = db.Column(db.Float, nullable=False)

    def __init__(self, assessment_id=None, class_name="", probability=0.0, **kwargs):
        super().__init__(**kwargs)
        if assessment_id is not None:
            self.assessment_id = assessment_id
        self.class_name = class_name
        self.probability = probability

class Explanation(db.Model):
    __tablename__ = "explanations"
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    shap_value = db.Column(db.Float, nullable=False)
    contribution_type = db.Column(db.String(20), nullable=False)  # 'Positive', 'Negative', 'Neutral'

    def __init__(self, assessment_id=None, feature_name="", shap_value=0.0, contribution_type="Neutral", **kwargs):
        super().__init__(**kwargs)
        if assessment_id is not None:
            self.assessment_id = assessment_id
        self.feature_name = feature_name
        self.shap_value = shap_value
        self.contribution_type = contribution_type

    def to_dict(self):
        return {
            "feature_name": self.feature_name,
            "shap_value": self.shap_value,
            "contribution_type": self.contribution_type
        }

class Recommendation(db.Model):
    __tablename__ = "recommendations"
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, assessment_id=None, recommendation_text="", **kwargs):
        super().__init__(**kwargs)
        if assessment_id is not None:
            self.assessment_id = assessment_id
        self.recommendation_text = recommendation_text
