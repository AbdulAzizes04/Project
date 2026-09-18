"""Department management API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import CurrentUser, DbSession, require_role
from app.services.department_service import department_service
from app.schemas.department import DepartmentCreateRequest, DepartmentUpdateRequest
from app.models.complaint import Complaint
from app.models.user import User

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get("")
@router.get("/")
def list_departments(db: DbSession):
    """List all active departments with complaint stats."""
    depts = department_service.get_all_departments(db)
    result = []
    for dept in depts:
        total = db.query(Complaint).filter(Complaint.department_id == dept.id).count()
        resolved = db.query(Complaint).filter(
            Complaint.department_id == dept.id,
            Complaint.status.in_(["RESOLVED", "CLOSED"]),
        ).count()
        staff_count = db.query(User).filter(
            User.department_id == dept.id,
            User.role == "staff",
            User.is_active == True,
        ).count()
        result.append({
            "id": dept.id,
            "name": dept.name,
            "code": dept.code,
            "category_mapping": dept.category_mapping,
            "description": dept.description,
            "head_name": dept.head_name,
            "contact_email": dept.contact_email,
            "contact_phone": dept.contact_phone,
            "is_active": dept.is_active,
            "created_at": dept.created_at,
            "complaint_count": total,
            "resolved_count": resolved,
            "staff_count": staff_count,
        })
    return {"success": True, "departments": result}


@router.post("", dependencies=[Depends(require_role("admin"))], status_code=201)
def create_department(request: DepartmentCreateRequest, db: DbSession):
    """Create a new department (Admin only)."""
    dept = department_service.create_department(request.model_dump(), db)
    return {"success": True, "message": "Department created.", "department_id": dept.id}


@router.get("/{dept_id}")
def get_department(dept_id: str, db: DbSession):
    """Get department detail."""
    dept = department_service.get_department_by_id(dept_id, db)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    staff = department_service.get_department_staff(dept_id, db)
    return {
        "success": True,
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "category_mapping": dept.category_mapping,
        "description": dept.description,
        "head_name": dept.head_name,
        "contact_email": dept.contact_email,
        "contact_phone": dept.contact_phone,
        "is_active": dept.is_active,
        "staff": [{"id": s.id, "full_name": s.full_name, "email": s.email} for s in staff],
    }


@router.put("/{dept_id}", dependencies=[Depends(require_role("admin"))])
def update_department(dept_id: str, request: DepartmentUpdateRequest, db: DbSession):
    """Update department (Admin only)."""
    dept = department_service.update_department(
        dept_id, {k: v for k, v in request.model_dump().items() if v is not None}, db
    )
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    return {"success": True, "message": "Department updated."}
