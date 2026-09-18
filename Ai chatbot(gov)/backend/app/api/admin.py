"""Admin API routes — dashboard, user management, complaint verification and assignment."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.dependencies import CurrentUser, DbSession, require_role
from app.services.complaint_service import complaint_service
from app.services.notification_service import notification_service
from app.schemas.complaint import VerifyComplaintRequest, AssignComplaintRequest
from app.models.user import User
from app.models.department import Department
from app.models.complaint import Complaint
from app.core.security import hash_password
import uuid

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("/dashboard")
def admin_dashboard(db: DbSession):
    """Get admin dashboard statistics."""
    from app.services.analytics_service import analytics_service
    stats = analytics_service.get_dashboard_stats(db)
    return {"success": True, "stats": stats}


@router.get("/users")
def list_users(
    db: DbSession,
    role: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all users with optional filtering."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%")
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "success": True,
        "total": total,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone,
                "role": u.role,
                "department_id": u.department_id,
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }


@router.put("/users/{user_id}")
def update_user(user_id: str, updates: dict, db: DbSession):
    """Update user details (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    allowed_fields = {"full_name", "phone", "is_active", "department_id", "role"}
    for key, value in updates.items():
        if key in allowed_fields and value is not None:
            setattr(user, key, value)

    db.commit()
    return {"success": True, "message": "User updated."}


@router.post("/staff")
def create_staff_account(data: dict, db: DbSession):
    """Create a new staff account (admin only)."""
    existing = db.query(User).filter(User.email == data.get("email")).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    dept_id = data.get("department_id")
    if dept_id:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found.")

    staff = User(
        id=str(uuid.uuid4()),
        email=data["email"],
        full_name=data["full_name"],
        phone=data.get("phone"),
        password_hash=hash_password(data.get("password", "Staff@123")),
        role="staff",
        department_id=dept_id,
        is_active=True,
    )
    db.add(staff)
    db.commit()

    return {
        "success": True,
        "message": "Staff account created.",
        "staff_id": staff.id,
        "email": staff.email,
        "default_password": "Staff@123 (change on first login)",
    }


@router.get("/staff")
def list_staff(db: DbSession, department_id: Optional[str] = None):
    """List all staff members."""
    query = db.query(User).filter(User.role == "staff")
    if department_id:
        query = query.filter(User.department_id == department_id)
    staff = query.all()
    return {
        "success": True,
        "staff": [
            {
                "id": s.id,
                "full_name": s.full_name,
                "email": s.email,
                "phone": s.phone,
                "department_id": s.department_id,
                "is_active": s.is_active,
            }
            for s in staff
        ],
    }


@router.put("/complaints/{complaint_id}/verify")
@router.post("/complaints/{complaint_id}/verify")
def verify_complaint(
    complaint_id: str,
    request: VerifyComplaintRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Verify a complaint and optionally correct AI predictions."""
    complaint = complaint_service.verify_complaint(
        complaint_id=complaint_id,
        verified_by=current_user.id,
        verified_by_name=current_user.full_name,
        db=db,
        remarks=request.get_remarks(),
        corrected_category=request.get_category(),
        corrected_priority=request.get_priority(),
    )
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    if request.department_id and complaint.department_id != request.department_id:
        complaint.department_id = request.department_id
        db.commit()

    return {"success": True, "message": "Complaint verified.", "status": complaint.status}


@router.put("/complaints/{complaint_id}/assign")
@router.post("/complaints/{complaint_id}/assign")
def assign_complaint(
    complaint_id: str,
    request: AssignComplaintRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Assign a complaint to a department and optionally a staff member."""
    staff_id = request.get_staff_id()
    complaint = complaint_service.assign_complaint(
        complaint_id=complaint_id,
        department_id=request.department_id,
        assigned_by=current_user.id,
        db=db,
        assigned_staff_id=staff_id,
        notes=request.notes,
    )
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    # Notify assigned staff
    if staff_id:
        notification_service.notify_staff_assigned(
            staff_id=staff_id,
            complaint_number=complaint.complaint_number,
            complaint_id=complaint.id,
            db=db,
        )

    # Notify citizen
    citizen = db.query(User).filter(User.id == complaint.citizen_id).first()
    if citizen:
        notification_service.notify_status_changed(
            citizen_id=citizen.id,
            complaint_number=complaint.complaint_number,
            complaint_id=complaint.id,
            new_status="ASSIGNED",
            db=db,
        )

    dept = db.query(Department).filter(Department.id == request.department_id).first()
    return {
        "success": True,
        "message": f"Complaint assigned to {dept.name if dept else 'department'}.",
        "department": dept.name if dept else None,
    }
