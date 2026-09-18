# Models package — import all models so SQLAlchemy can discover them
from app.models.user import User
from app.models.department import Department
from app.models.complaint import Complaint, ComplaintStatusHistory, ComplaintAssignment, Attachment
from app.models.prediction import ComplaintPrediction, ComplaintEmbedding, ModelEvaluation
from app.models.notification import Notification
from app.models.audit import AuditLog

__all__ = [
    "User",
    "Department",
    "Complaint",
    "ComplaintStatusHistory",
    "ComplaintAssignment",
    "Attachment",
    "ComplaintPrediction",
    "ComplaintEmbedding",
    "ModelEvaluation",
    "Notification",
    "AuditLog",
]
