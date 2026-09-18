"""Notification Service — creates in-app notifications for users."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from loguru import logger


class NotificationService:

    def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "general",
        reference_id: Optional[str] = None,
        reference_number: Optional[str] = None,
        db: Session = None,
    ) -> Optional[Notification]:
        if not db:
            return None
        try:
            notif = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False,
                reference_id=reference_id,
                reference_number=reference_number,
            )
            db.add(notif)
            db.commit()
            return notif
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            db.rollback()
            return None

    def notify_complaint_submitted(self, citizen_id: str, complaint_number: str,
                                    complaint_id: str, db: Session):
        self.create_notification(
            user_id=citizen_id,
            title="Complaint Submitted",
            message=f"Your complaint {complaint_number} has been submitted successfully.",
            notification_type="complaint_submitted",
            reference_id=complaint_id,
            reference_number=complaint_number,
            db=db,
        )

    def notify_status_changed(
        self,
        citizen_id: str,
        complaint_number: str,
        complaint_id: str,
        new_status: str,
        db: Session,
        remarks: Optional[str] = None,
        staff_name: Optional[str] = None,
    ):
        status_upper = new_status.upper()
        if status_upper == "NOTED":
            title = "Work Order Noted & Acknowledged"
            msg = f"Field Officer {staff_name or 'assigned staff'} has noted your complaint {complaint_number}."
            if remarks:
                msg += f" Note: \"{remarks}\""
        elif status_upper == "IN_PROGRESS":
            title = "Field Work In Progress"
            msg = f"Field Officer {staff_name or 'assigned staff'} started work on your grievance {complaint_number}."
            if remarks:
                msg += f" Progress update: \"{remarks}\""
        elif status_upper in ("RESOLVED", "SORTED"):
            title = "Grievance Sorted & Resolved"
            msg = f"Your grievance {complaint_number} has been sorted and marked resolved by {staff_name or 'the municipal team'}."
            if remarks:
                msg += f" Resolution notes: \"{remarks}\""
        else:
            status_labels = {
                "AI_ANALYZED": "analyzed by AI",
                "VERIFIED": "verified by admin",
                "ASSIGNED": "assigned to department field officers",
                "CLOSED": "closed",
                "REJECTED": "rejected",
            }
            label = status_labels.get(status_upper, status_upper.lower())
            title = "Complaint Status Updated"
            msg = f"Your complaint {complaint_number} has been {label}."
            if remarks:
                msg += f" Remarks: \"{remarks}\""

        self.create_notification(
            user_id=citizen_id,
            title=title,
            message=msg,
            notification_type="status_changed",
            reference_id=complaint_id,
            reference_number=complaint_number,
            db=db,
        )

    def notify_admin_new_complaint(self, admin_id: str, complaint_number: str,
                                    complaint_id: str, category: str, db: Session):
        self.create_notification(
            user_id=admin_id,
            title="New Complaint Received",
            message=f"New {category} complaint {complaint_number} submitted.",
            notification_type="new_complaint",
            reference_id=complaint_id,
            reference_number=complaint_number,
            db=db,
        )

    def notify_staff_assigned(self, staff_id: str, complaint_number: str,
                               complaint_id: str, db: Session):
        self.create_notification(
            user_id=staff_id,
            title="Complaint Assigned to You",
            message=f"Complaint {complaint_number} has been assigned to you for resolution.",
            notification_type="assignment",
            reference_id=complaint_id,
            reference_number=complaint_number,
            db=db,
        )

    def get_user_notifications(self, user_id: str, db: Session, limit: int = 50) -> dict:
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )
        unread_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).count()
        return {"notifications": notifications, "unread_count": unread_count}

    def mark_read(self, notification_id: str, user_id: str, db: Session) -> bool:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()
        if notif:
            notif.is_read = True
            db.commit()
            return True
        return False

    def mark_all_read(self, user_id: str, db: Session):
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).update({"is_read": True})
        db.commit()


notification_service = NotificationService()
