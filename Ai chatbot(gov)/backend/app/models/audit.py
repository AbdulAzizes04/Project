"""Audit log model — immutable record of all significant system actions."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<AuditLog action={self.action} user={self.user_id}>"
