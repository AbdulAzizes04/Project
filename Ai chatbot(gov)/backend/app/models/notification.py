"""Notification model — in-app notifications for citizens, staff, and admins."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    # Types: complaint_submitted | complaint_verified | complaint_assigned |
    #        status_changed | complaint_resolved | new_complaint | critical_complaint
    notification_type = Column(String(50), nullable=False, default="general")
    is_read = Column(Boolean, default=False, nullable=False)
    reference_id = Column(String(36), nullable=True)  # complaint_id
    reference_number = Column(String(50), nullable=True)  # complaint_number
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<Notification id={self.id} user={self.user_id} read={self.is_read}>"
