"""Pydantic schemas for notifications."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    reference_id: Optional[str]
    reference_number: Optional[str]
    created_at: datetime


class NotificationListResponse(BaseModel):
    success: bool = True
    unread_count: int
    notifications: List[NotificationResponse]
