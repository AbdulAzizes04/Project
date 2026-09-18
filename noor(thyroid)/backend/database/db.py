from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./thyroid.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="doctor")  # admin | doctor
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    weight = Column(Float)
    height = Column(Float)
    bmi = Column(Float)
    blood_pressure = Column(String)
    pulse_rate = Column(Integer)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    patient_name = Column(String)
    # Input features stored as JSON
    input_data = Column(JSON)
    # Prediction results
    predicted_condition = Column(String)
    confidence = Column(Float)
    risk_level = Column(String)
    rf_confidence = Column(Float)
    xgb_confidence = Column(Float)
    lgbm_confidence = Column(Float)
    svm_confidence = Column(Float)
    ann_confidence = Column(Float)
    # XAI
    shap_values = Column(JSON)
    lime_explanation = Column(JSON)
    feature_importance = Column(JSON)
    natural_language_explanation = Column(Text)
    # Recommendations
    treatment_suggestions = Column(JSON)
    lifestyle_advice = Column(JSON)
    diet_recommendations = Column(JSON)
    exercise_recommendations = Column(JSON)
    followup_recommendation = Column(Text)
    referral_suggestion = Column(Text)
    # Report
    report_path = Column(String)
    doctor_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    patient_name = Column(String)
    doctor_name = Column(String)
    appointment_date = Column(String)
    appointment_time = Column(String)
    reason = Column(Text)
    status = Column(String, default="scheduled")  # scheduled | completed | cancelled
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(Text)
    type = Column(String, default="info")  # info | warning | danger | success
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── DB Init ──────────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
