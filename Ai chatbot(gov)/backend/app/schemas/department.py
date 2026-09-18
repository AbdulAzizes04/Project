"""Pydantic schemas for departments."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class DepartmentCreateRequest(BaseModel):
    name: str
    code: str
    category_mapping: str
    description: Optional[str] = None
    head_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class DepartmentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    head_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    category_mapping: str
    description: Optional[str]
    head_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    is_active: bool
    created_at: datetime

    # Populated by service
    complaint_count: Optional[int] = 0
    staff_count: Optional[int] = 0
    resolved_count: Optional[int] = 0


class DepartmentListResponse(BaseModel):
    success: bool = True
    departments: List[DepartmentResponse]
