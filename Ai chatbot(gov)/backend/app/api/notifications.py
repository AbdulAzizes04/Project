"""Notification API routes."""
from fastapi import APIRouter, Depends
from app.core.dependencies import CurrentUser, DbSession
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
@router.get("/")
def get_notifications(current_user: CurrentUser, db: DbSession):
    """Get all notifications for the current user."""
    result = notification_service.get_user_notifications(current_user.id, db)
    return {
        "success": True,
        "unread_count": result["unread_count"],
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "notification_type": n.notification_type,
                "is_read": n.is_read,
                "reference_id": n.reference_id,
                "reference_number": n.reference_number,
                "created_at": n.created_at,
            }
            for n in result["notifications"]
        ],
    }


@router.put("/{notification_id}/read")
def mark_read(notification_id: str, current_user: CurrentUser, db: DbSession):
    success = notification_service.mark_read(notification_id, current_user.id, db)
    return {"success": success}


@router.put("/read-all")
def mark_all_read(current_user: CurrentUser, db: DbSession):
    notification_service.mark_all_read(current_user.id, db)
    return {"success": True, "message": "All notifications marked as read."}
