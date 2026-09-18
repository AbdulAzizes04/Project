"""
Pydantic Schemas for the Thyroid Risk Assessment API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "doctor"

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True


# ─── Patient ──────────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    weight: Optional[float] = None
    height: Optional[float] = None
    bmi: Optional[float] = None
    blood_pressure: Optional[str] = None
    pulse_rate: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class PatientOut(PatientCreate):
    id: int
    patient_id: str
    created_at: datetime
    class Config:
        from_attributes = True


# ─── Prediction Input ─────────────────────────────────────────────────────────

class PredictionInput(BaseModel):
    # Patient info
    patient_id: Optional[str] = None
    name: str
    age: int
    gender: str
    weight: float
    height: float
    bmi: float
    blood_pressure: Optional[str] = "120/80"
    pulse_rate: Optional[int] = 72

    # Symptoms (0/1)
    fatigue: int = 0
    weight_gain: int = 0
    weight_loss: int = 0
    hair_loss: int = 0
    constipation: int = 0
    anxiety: int = 0
    depression: int = 0
    sweating: int = 0
    neck_swelling: int = 0
    voice_changes: int = 0
    cold_intolerance: int = 0
    heat_intolerance: int = 0
    difficulty_swallowing: int = 0
    sleep_disturbance: int = 0

    # Hormones
    tsh: float = 2.5
    t3: float = 1.2
    t4: float = 100.0
    ft3: float = 3.5
    ft4: float = 1.2

    # Blood tests
    hemoglobin: float = 13.5
    wbc: float = 7.0
    rbc: float = 4.5
    platelets: float = 250.0
    vitamin_d: float = 30.0
    calcium: float = 9.5

    # Medical history (0/1)
    diabetes: int = 0
    hypertension: int = 0
    family_history: int = 0
    smoking: int = 0
    alcohol: int = 0

    doctor_notes: Optional[str] = None


# ─── Prediction Output ────────────────────────────────────────────────────────

class ModelConfidence(BaseModel):
    rf: float
    xgb: float
    lgbm: float
    svm: float
    ann: float

class PredictionOut(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    predicted_condition: str
    confidence: float
    risk_level: str
    model_confidences: ModelConfidence
    shap_values: Dict[str, float]
    feature_importance: Dict[str, float]
    lime_explanation: List[Dict[str, Any]]
    natural_language_explanation: str
    treatment_suggestions: List[str]
    lifestyle_advice: List[str]
    diet_recommendations: List[str]
    exercise_recommendations: List[str]
    followup_recommendation: str
    referral_suggestion: str
    created_at: datetime
    class Config:
        from_attributes = True


# ─── Appointment ─────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    patient_id: str
    patient_name: str
    doctor_name: str
    appointment_date: str
    appointment_time: str
    reason: Optional[str] = None

class AppointmentOut(AppointmentCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True


# ─── Notification ─────────────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True
