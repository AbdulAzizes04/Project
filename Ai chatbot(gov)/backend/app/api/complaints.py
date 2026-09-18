import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from app.core.dependencies import CurrentUser, DbSession, require_role
from app.services.complaint_service import complaint_service
from app.services.notification_service import notification_service
from app.schemas.complaint import (
    ComplaintCreateRequest, ComplaintListItem, ComplaintDetailResponse, ComplaintListResponse,
    StatusUpdateRequest, ResolveComplaintRequest,
)
from app.models.complaint import Complaint
from app.models.user import User
from app.models.department import Department
from app.models.prediction import ComplaintPrediction

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])
citizen_router = APIRouter(prefix="/api/citizen", tags=["Citizen"])


def _build_list_item(complaint: Complaint, db) -> dict:
    """Build a complaint list item with joined citizen/department data."""
    citizen = db.query(User).filter(User.id == complaint.citizen_id).first()
    dept = None
    if complaint.department_id:
        dept = db.query(Department).filter(Department.id == complaint.department_id).first()
    pred = db.query(ComplaintPrediction).filter(
        ComplaintPrediction.complaint_id == complaint.id
    ).first()

    assigned_staff = None
    if complaint.assigned_staff_id:
        assigned_staff = db.query(User).filter(User.id == complaint.assigned_staff_id).first()

    return {
        "id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "ticket_number": complaint.ticket_number,
        "title": complaint.title,
        "citizen_id": complaint.citizen_id,
        "description": complaint.description[:200] if complaint.description else "",
        "location": complaint.location,
        "duration": complaint.duration,
        "severity": complaint.severity,
        "image_url": complaint.image_url,
        "status": complaint.status.lower(),
        "category": complaint.category,
        "priority": complaint.priority,
        "department_id": complaint.department_id,
        "assigned_staff_id": complaint.assigned_staff_id,
        "assigned_to_id": complaint.assigned_staff_id,
        "assigned_to": {
            "id": assigned_staff.id,
            "full_name": assigned_staff.full_name,
            "email": assigned_staff.email,
        } if assigned_staff else None,
        "is_verified": complaint.is_verified,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "citizen_name": citizen.full_name if citizen else None,
        "citizen_email": citizen.email if citizen else None,
        "department_name": dept.name if dept else None,
        "ai_confidence": pred.category_confidence if pred else None,
    }


# ─── Public & Citizen Routes on /api/complaints ────────────────────────────────

@router.post("/upload")
async def upload_attachment(
    file: UploadFile = File(...),
):
    """Upload a picture / photo attachment for a complaint."""
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files (JPG, PNG, WebP) are allowed.",
        )

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    from app.core.config import settings
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{unique_filename}"
    return {
        "success": True,
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_url": file_url,
        "file_path": file_url,
        "file_size": len(contents),
        "file_type": file.content_type,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_complaint_endpoint(
    request: ComplaintCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Create a new complaint directly or via assistant."""
    desc = request.description or request.title or "Citizen Grievance"
    loc = request.location or ""
    if request.landmark:
        loc = f"{loc}, Near {request.landmark}".strip(", ")
    if request.pincode:
        loc = f"{loc} - {request.pincode}".strip(" - ")

    cat = request.category
    prio = request.priority

    if not cat:
        from app.services.classification_service import classification_service
        c_res = classification_service.classify(desc)
        cat = c_res.get("category", "Water Supply")
    if not prio:
        from app.services.priority_service import priority_service
        p_res = priority_service.predict_priority(desc, cat, request.severity, request.duration)
        prio = p_res.get("priority", "Medium")

    analysis = {
        "classification": {"category": cat, "confidence": 0.95},
        "priority": {"priority": prio, "confidence": 0.90},
    }

    complaint = complaint_service.create_complaint(
        citizen_id=current_user.id,
        description=desc,
        location=loc,
        duration=request.duration,
        severity=request.severity,
        raw_chat_history=request.raw_chat_history,
        analysis=analysis,
        image_url=request.image_url,
        db=db,
    )

    return {
        "success": True,
        "id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "ticket_number": complaint.ticket_number,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "priority": complaint.priority,
        "image_url": complaint.image_url,
        "status": complaint.status.lower(),
        "created_at": complaint.created_at,
    }


@router.get("/my")
def get_my_complaints(current_user: CurrentUser, db: DbSession):
    """Get all complaints for the currently authenticated user."""
    complaints, total = complaint_service.list_complaints(
        db=db, citizen_id=current_user.id, page=1, page_size=100
    )
    return [_build_list_item(c, db) for c in complaints]


@router.get("/track/{ticket_number}")
def track_complaint(ticket_number: str, db: DbSession):
    """Track a complaint publicly by its ticket number."""
    complaint = db.query(Complaint).filter(
        (Complaint.complaint_number == ticket_number) | (Complaint.id == ticket_number)
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found with this ticket number.")
    detail = complaint_service.get_complaint_detail(complaint.id, db)
    return {
        "success": True,
        "id": complaint.id,
        "ticket_number": complaint.complaint_number,
        "complaint_number": complaint.complaint_number,
        "title": complaint.title,
        "description": complaint.description,
        "location": complaint.location,
        "image_url": complaint.image_url,
        "status": complaint.status.lower(),
        "category": complaint.category,
        "priority": complaint.priority,
        "department": {
            "name": detail["department"].name if detail.get("department") else "Municipal Department",
            "code": detail["department"].code if detail.get("department") else "GOV",
        } if detail.get("department") else None,
        "status_history": [
            {
                "id": h.id,
                "old_status": h.old_status,
                "new_status": h.new_status,
                "remarks": h.remarks,
                "actor_name": h.changed_by_name,
                "created_at": h.created_at,
            }
            for h in detail.get("status_history", [])
        ],
        "created_at": complaint.created_at,
    }


# ─── Citizen Routes ────────────────────────────────────────────────────────────

@citizen_router.get("/complaints")
def citizen_list_complaints(
    current_user: CurrentUser,
    db: DbSession,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    """List all complaints for the currently authenticated citizen."""
    complaints, total = complaint_service.list_complaints(
        db=db,
        citizen_id=current_user.id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return {
        "success": True,
        "total": total,
        "page": page,
        "page_size": page_size,
        "complaints": [_build_list_item(c, db) for c in complaints],
    }


@citizen_router.get("/complaints/{complaint_id}")
def citizen_get_complaint(
    complaint_id: str,
    current_user: CurrentUser,
    db: DbSession,
):
    """Get details of a specific complaint (citizen must own it)."""
    detail = complaint_service.get_complaint_detail(complaint_id, db)
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    complaint = detail["complaint"]
    if complaint.citizen_id != current_user.id and current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Access denied.")

    return {
        "success": True,
        "id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "citizen_id": complaint.citizen_id,
        "description": complaint.description,
        "location": complaint.location,
        "duration": complaint.duration,
        "severity": complaint.severity,
        "image_url": complaint.image_url,
        "status": complaint.status,
        "category": complaint.category,
        "priority": complaint.priority,
        "department_id": complaint.department_id,
        "is_verified": complaint.is_verified,
        "resolution_notes": complaint.resolution_notes,
        "resolved_at": complaint.resolved_at,
        "closed_at": complaint.closed_at,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "raw_chat_history": complaint.raw_chat_history,
        "citizen": {
            "id": detail["citizen"].id,
            "full_name": detail["citizen"].full_name,
            "email": detail["citizen"].email,
            "phone": detail["citizen"].phone,
        } if detail["citizen"] else None,
        "department": {
            "id": detail["department"].id,
            "name": detail["department"].name,
            "code": detail["department"].code,
            "contact_email": detail["department"].contact_email,
            "contact_phone": detail["department"].contact_phone,
        } if detail["department"] else None,
        "prediction": _serialize_prediction(detail["prediction"]),
        "status_history": [
            {
                "id": h.id,
                "old_status": h.old_status,
                "new_status": h.new_status,
                "changed_by_name": h.changed_by_name,
                "remarks": h.remarks,
                "created_at": h.created_at,
            }
            for h in detail["status_history"]
        ],
    }


def _serialize_prediction(pred) -> Optional[dict]:
    if not pred:
        return None
    return {
        "predicted_category": pred.predicted_category,
        "category_confidence": pred.category_confidence,
        "predicted_priority": pred.predicted_priority,
        "priority_confidence": pred.priority_confidence,
        "is_duplicate": pred.is_duplicate,
        "duplicate_similarity": pred.duplicate_similarity,
        "duplicate_complaint_id": pred.duplicate_complaint_id,
        "duplicate_complaint_number": pred.duplicate_complaint_number,
        "recommended_department_name": pred.recommended_department_name,
        "low_confidence_flag": pred.low_confidence_flag,
        "admin_corrected_category": pred.admin_corrected_category,
        "admin_corrected_priority": pred.admin_corrected_priority,
        "model_version": pred.model_version,
        "created_at": pred.created_at,
    }


# ─── Admin/Staff Complaint Routes ──────────────────────────────────────────────

@router.get("", dependencies=[Depends(require_role("admin", "staff"))])
@router.get("/", dependencies=[Depends(require_role("admin", "staff"))])
def list_all_complaints(
    current_user: CurrentUser,
    db: DbSession,
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    priority: Optional[str] = None,
    department_id: Optional[str] = None,
    assigned_to_id: Optional[str] = None,
    assigned_staff_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all complaints with filtering (Admin/Staff only)."""
    # Staff see only their department's complaints
    filter_dept = department_id
    if current_user.role == "staff" and current_user.department_id:
        filter_dept = current_user.department_id

    staff_filter = assigned_staff_id or assigned_to_id

    complaints, total = complaint_service.list_complaints(
        db=db,
        status=status_filter,
        category=category,
        priority=priority,
        department_id=filter_dept,
        assigned_staff_id=staff_filter,
        search=search,
        page=page,
        page_size=page_size,
    )
    return {
        "success": True,
        "total": total,
        "page": page,
        "page_size": page_size,
        "complaints": [_build_list_item(c, db) for c in complaints],
    }


@router.get("/{complaint_id}", dependencies=[Depends(require_role("admin", "staff"))])
def get_complaint_detail(complaint_id: str, db: DbSession):
    """Get full complaint detail (Admin/Staff only)."""
    detail = complaint_service.get_complaint_detail(complaint_id, db)
    if not detail:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    complaint = detail["complaint"]
    return {
        "success": True,
        "id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "citizen_id": complaint.citizen_id,
        "description": complaint.description,
        "location": complaint.location,
        "duration": complaint.duration,
        "severity": complaint.severity,
        "image_url": complaint.image_url,
        "status": complaint.status,
        "category": complaint.category,
        "priority": complaint.priority,
        "department_id": complaint.department_id,
        "assigned_staff_id": complaint.assigned_staff_id,
        "is_verified": complaint.is_verified,
        "resolution_notes": complaint.resolution_notes,
        "resolved_at": complaint.resolved_at,
        "closed_at": complaint.closed_at,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "raw_chat_history": complaint.raw_chat_history,
        "citizen": {
            "id": detail["citizen"].id,
            "full_name": detail["citizen"].full_name,
            "email": detail["citizen"].email,
            "phone": detail["citizen"].phone,
        } if detail["citizen"] else None,
        "department": {
            "id": detail["department"].id,
            "name": detail["department"].name,
            "code": detail["department"].code,
            "contact_email": detail["department"].contact_email,
            "contact_phone": detail["department"].contact_phone,
        } if detail["department"] else None,
        "prediction": _serialize_prediction(detail["prediction"]),
        "status_history": [
            {
                "id": h.id,
                "old_status": h.old_status,
                "new_status": h.new_status,
                "changed_by_name": h.changed_by_name,
                "remarks": h.remarks,
                "created_at": h.created_at,
            }
            for h in detail["status_history"]
        ],
    }


@router.put("/{complaint_id}/status", dependencies=[Depends(require_role("admin", "staff"))])
@router.patch("/{complaint_id}/status", dependencies=[Depends(require_role("admin", "staff"))])
def update_status(
    complaint_id: str,
    request: StatusUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update complaint status (Admin/Staff only)."""
    try:
        complaint = complaint_service.update_status(
            complaint_id=complaint_id,
            new_status=request.get_status().upper(),
            changed_by=current_user.id,
            changed_by_name=current_user.full_name,
            remarks=request.remarks,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    # Notify citizen
    citizen = db.query(User).filter(User.id == complaint.citizen_id).first()
    if citizen:
        notification_service.notify_status_changed(
            citizen_id=citizen.id,
            complaint_number=complaint.complaint_number,
            complaint_id=complaint.id,
            new_status=complaint.status,
            db=db,
            remarks=request.remarks,
            staff_name=current_user.full_name,
        )

    return {"success": True, "message": "Status updated.", "status": complaint.status.lower()}


@router.put("/{complaint_id}/resolve", dependencies=[Depends(require_role("admin", "staff"))])
def resolve_complaint(
    complaint_id: str,
    request: ResolveComplaintRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Mark a complaint as resolved with notes."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    complaint.resolution_notes = request.resolution_notes
    db.commit()

    try:
        complaint = complaint_service.update_status(
            complaint_id=complaint_id,
            new_status="RESOLVED",
            changed_by=current_user.id,
            changed_by_name=current_user.full_name,
            remarks=request.remarks or request.resolution_notes or "Complaint resolved.",
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Notify citizen
    citizen = db.query(User).filter(User.id == complaint.citizen_id).first()
    if citizen:
        notification_service.notify_status_changed(
            citizen_id=citizen.id,
            complaint_number=complaint.complaint_number,
            complaint_id=complaint.id,
            new_status="RESOLVED",
            db=db,
            remarks=request.remarks or request.resolution_notes,
            staff_name=current_user.full_name,
        )

    return {"success": True, "message": "Complaint resolved.", "status": complaint.status}
