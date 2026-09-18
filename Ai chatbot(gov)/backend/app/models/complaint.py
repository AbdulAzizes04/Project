"""
Complaint and related models:
- Complaint: core complaint record
- ComplaintStatusHistory: audit trail of status changes
- ComplaintAssignment: tracks department/staff assignments
- Attachment: file uploads per complaint
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, JSON
from app.core.database import Base


COMPLAINT_STATUSES = [
    "SUBMITTED",
    "AI_ANALYZED",
    "VERIFIED",
    "ASSIGNED",
    "NOTED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED",
    "REJECTED",
]

PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]

CATEGORIES = [
    "Water Supply",
    "Roads",
    "Sanitation",
    "Electricity",
    "Street Lighting",
    "Drainage",
]


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_number = Column(String(50), unique=True, nullable=False, index=True)
    citizen_id = Column(String(36), nullable=False, index=True)

    # Raw complaint content
    description = Column(Text, nullable=False)
    location = Column(String(500), nullable=True)
    duration = Column(String(255), nullable=True)
    severity = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Full chatbot conversation stored as JSON
    raw_chat_history = Column(JSON, nullable=True, default=list)

    # Status workflow
    status = Column(String(50), nullable=False, default="SUBMITTED", index=True)
    is_verified = Column(Boolean, default=False)

    # Final category and priority (may be admin-corrected)
    category = Column(String(100), nullable=True, index=True)
    priority = Column(String(50), nullable=True, index=True)

    # Assignment
    department_id = Column(String(36), nullable=True, index=True)
    assigned_staff_id = Column(String(36), nullable=True)

    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def ticket_number(self):
        return self.complaint_number

    @ticket_number.setter
    def ticket_number(self, val):
        self.complaint_number = val

    @property
    def title(self):
        if not self.description:
            return f"Grievance {self.complaint_number}"
        first_line = self.description.split("\n")[0].strip()
        return (first_line[:90] + "...") if len(first_line) > 90 else first_line

    def __init__(self, **kwargs):
        # Support title and ticket_number kwargs gracefully
        if "ticket_number" in kwargs and "complaint_number" not in kwargs:
            kwargs["complaint_number"] = kwargs.pop("ticket_number")
        if "title" in kwargs:
            title_val = kwargs.pop("title")
            if not kwargs.get("description"):
                kwargs["description"] = title_val
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Complaint {self.complaint_number} status={self.status}>"


class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(String(36), nullable=True)  # User ID
    changed_by_name = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ComplaintAssignment(Base):
    __tablename__ = "complaint_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), nullable=False, index=True)
    department_id = Column(String(36), nullable=True)
    department_name = Column(String(255), nullable=True)
    assigned_staff_id = Column(String(36), nullable=True)
    assigned_staff_name = Column(String(255), nullable=True)
    assigned_by = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), nullable=False, index=True)
    uploaded_by = Column(String(36), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
