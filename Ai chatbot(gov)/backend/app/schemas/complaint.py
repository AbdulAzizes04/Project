"""Pydantic schemas for complaints — request/response validation."""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ComplaintCreateRequest(BaseModel):
    """Used when submitting a complaint directly or from chatbot session."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    landmark: Optional[str] = None
    pincode: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    image_url: Optional[str] = None
    raw_chat_history: Optional[List[dict]] = None
    session_id: Optional[str] = None


class ComplaintUpdateRequest(BaseModel):
    """Admin/staff updates to complaint fields."""
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    department_id: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    remarks: Optional[str] = None


class AssignComplaintRequest(BaseModel):
    department_id: str
    assigned_staff_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    notes: Optional[str] = None

    def get_staff_id(self) -> Optional[str]:
        return self.assigned_staff_id or self.assigned_to_id


class VerifyComplaintRequest(BaseModel):
    remarks: Optional[str] = None
    notes: Optional[str] = None
    corrected_category: Optional[str] = None
    verified_category: Optional[str] = None
    corrected_priority: Optional[str] = None
    verified_priority: Optional[str] = None
    department_id: Optional[str] = None

    def get_remarks(self) -> Optional[str]:
        return self.remarks or self.notes

    def get_category(self) -> Optional[str]:
        return self.corrected_category or self.verified_category

    def get_priority(self) -> Optional[str]:
        return self.corrected_priority or self.verified_priority


class StatusUpdateRequest(BaseModel):
    new_status: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

    def get_status(self) -> str:
        val = self.new_status or self.status
        if not val:
            raise ValueError("new_status or status must be provided")
        return val


class ResolveComplaintRequest(BaseModel):
    resolution_notes: str
    remarks: Optional[str] = None


# Response schemas
class StatusHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    old_status: Optional[str]
    new_status: str
    changed_by_name: Optional[str]
    remarks: Optional[str]
    created_at: datetime


class PredictionInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    predicted_category: Optional[str]
    category_confidence: Optional[float]
    predicted_priority: Optional[str]
    priority_confidence: Optional[float]
    is_duplicate: Optional[bool]
    duplicate_similarity: Optional[float]
    duplicate_complaint_id: Optional[str]
    duplicate_complaint_number: Optional[str]
    recommended_department_name: Optional[str]
    low_confidence_flag: Optional[bool]
    admin_corrected_category: Optional[str]
    admin_corrected_priority: Optional[str]
    model_version: Optional[str]
    created_at: Optional[datetime]


class CitizenInfo(BaseModel):
    id: str
    full_name: str
    email: str
    phone: Optional[str]


class DepartmentInfo(BaseModel):
    id: str
    name: str
    code: str
    contact_email: Optional[str]
    contact_phone: Optional[str]


class ComplaintListItem(BaseModel):
    """Compact complaint info for list/table views."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_number: str
    citizen_id: str
    description: str
    location: Optional[str]
    severity: Optional[str]
    status: str
    category: Optional[str]
    priority: Optional[str]
    department_id: Optional[str]
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    # Joined fields (populated by service)
    citizen_name: Optional[str] = None
    citizen_email: Optional[str] = None
    department_name: Optional[str] = None
    ai_confidence: Optional[float] = None
    image_url: Optional[str] = None


class ComplaintDetailResponse(BaseModel):
    """Full complaint with all related data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_number: str
    citizen_id: str
    description: str
    location: Optional[str]
    duration: Optional[str]
    severity: Optional[str]
    image_url: Optional[str] = None
    status: str
    category: Optional[str]
    priority: Optional[str]
    department_id: Optional[str]
    assigned_staff_id: Optional[str]
    is_verified: bool
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    raw_chat_history: Optional[List[Any]] = None

    # Populated by service
    citizen: Optional[CitizenInfo] = None
    department: Optional[DepartmentInfo] = None
    prediction: Optional[PredictionInfo] = None
    status_history: Optional[List[StatusHistoryItem]] = []


class ComplaintResponse(BaseModel):
    success: bool = True
    message: str
    complaint: ComplaintDetailResponse


class ComplaintListResponse(BaseModel):
    success: bool = True
    total: int
    page: int
    page_size: int
    complaints: List[ComplaintListItem]
