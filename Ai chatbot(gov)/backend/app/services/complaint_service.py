"""
Complaint CRUD Service.
Handles complaint creation, retrieval, updates, and status workflow.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from loguru import logger

import os
from app.models.complaint import Complaint, ComplaintStatusHistory, ComplaintAssignment, Attachment
from app.models.prediction import ComplaintPrediction, ComplaintEmbedding
from app.models.user import User
from app.models.department import Department

VALID_STATUS_TRANSITIONS = {
    "SUBMITTED": ["AI_ANALYZED", "VERIFIED", "ASSIGNED", "NOTED", "IN_PROGRESS", "REJECTED"],
    "AI_ANALYZED": ["VERIFIED", "ASSIGNED", "NOTED", "IN_PROGRESS", "REJECTED"],
    "VERIFIED": ["ASSIGNED", "NOTED", "IN_PROGRESS", "RESOLVED", "REJECTED"],
    "ASSIGNED": ["NOTED", "IN_PROGRESS", "RESOLVED", "REJECTED"],
    "NOTED": ["IN_PROGRESS", "RESOLVED", "ASSIGNED", "REJECTED"],
    "IN_PROGRESS": ["RESOLVED", "NOTED", "ASSIGNED", "REJECTED"],
    "RESOLVED": ["CLOSED", "IN_PROGRESS", "NOTED"],
    "CLOSED": ["IN_PROGRESS"],
    "REJECTED": ["SUBMITTED", "VERIFIED"],
}


def generate_complaint_number() -> str:
    """Generate a unique complaint ID in format GRV-YYYY-XXXXXX."""
    year = datetime.now(timezone.utc).year
    unique = str(uuid.uuid4().int)[:6].zfill(6)
    return f"GRV-{year}-{unique}"


class ComplaintService:

    def create_complaint(
        self,
        citizen_id: str,
        description: str,
        location: Optional[str],
        duration: Optional[str],
        severity: Optional[str],
        raw_chat_history: Optional[list],
        analysis: Optional[dict],
        db: Session,
        image_url: Optional[str] = None,
    ) -> Complaint:
        """
        Create a complaint with AI predictions and generate embedding.
        Runs the full save pipeline: complaint → prediction → embedding → history.
        """
        complaint_number = generate_complaint_number()

        # Determine category and priority from analysis
        category = None
        priority = None
        if analysis:
            category = analysis.get("classification", {}).get("category")
            priority = analysis.get("priority", {}).get("priority")

        complaint = Complaint(
            id=str(uuid.uuid4()),
            complaint_number=complaint_number,
            citizen_id=citizen_id,
            description=description,
            location=location,
            duration=duration,
            severity=severity,
            image_url=image_url,
            raw_chat_history=raw_chat_history or [],
            status="SUBMITTED",
            category=category,
            priority=priority,
            is_verified=False,
        )
        db.add(complaint)
        db.flush()  # Get ID without committing

        # Store attachment record if photo attached
        if image_url:
            attachment = Attachment(
                id=str(uuid.uuid4()),
                complaint_id=complaint.id,
                uploaded_by=citizen_id,
                filename=os.path.basename(image_url),
                original_filename=os.path.basename(image_url),
                file_path=image_url,
                file_type="image",
            )
            db.add(attachment)

        # Save AI predictions
        if analysis:
            self._save_prediction(complaint.id, analysis, db)

        # Store status history
        self._add_status_history(
            complaint_id=complaint.id,
            old_status=None,
            new_status="SUBMITTED",
            changed_by=citizen_id,
            changed_by_name=None,
            remarks="Complaint submitted by citizen",
            db=db,
        )

        db.commit()
        db.refresh(complaint)

        # Store sentence embedding (after commit, so complaint_id exists)
        try:
            from app.services.duplicate_service import duplicate_service
            full_text = f"{description} {location or ''} {duration or ''}"
            duplicate_service.store_embedding(complaint.id, full_text, db)
        except Exception as e:
            logger.warning(f"Could not store embedding: {e}")

        # Update status to AI_ANALYZED if analysis was done
        if analysis:
            self.update_status(
                complaint_id=complaint.id,
                new_status="AI_ANALYZED",
                changed_by=citizen_id,
                remarks="AI analysis completed automatically",
                db=db,
            )

        return complaint

    def _save_prediction(self, complaint_id: str, analysis: dict, db: Session):
        """Save AI prediction record."""
        classification = analysis.get("classification", {})
        priority_result = analysis.get("priority", {})
        duplicate = analysis.get("duplicate", {})

        prediction = ComplaintPrediction(
            id=str(uuid.uuid4()),
            complaint_id=complaint_id,
            predicted_category=classification.get("category"),
            category_confidence=classification.get("confidence"),
            predicted_priority=priority_result.get("priority"),
            priority_confidence=priority_result.get("confidence"),
            is_duplicate=duplicate.get("is_duplicate", False),
            duplicate_similarity=duplicate.get("similarity"),
            duplicate_complaint_id=duplicate.get("matched_complaint_id"),
            duplicate_complaint_number=duplicate.get("matched_complaint_number"),
            recommended_department_id=analysis.get("recommended_department_id"),
            recommended_department_name=analysis.get("recommended_department_name"),
            low_confidence_flag=classification.get("low_confidence", False),
            raw_analysis=analysis,
        )
        db.add(prediction)

    def _add_status_history(
        self, complaint_id: str, old_status: Optional[str], new_status: str,
        changed_by: Optional[str], changed_by_name: Optional[str],
        remarks: Optional[str], db: Session
    ):
        history = ComplaintStatusHistory(
            id=str(uuid.uuid4()),
            complaint_id=complaint_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_name=changed_by_name,
            remarks=remarks,
        )
        db.add(history)

    def update_status(
        self,
        complaint_id: str,
        new_status: str,
        changed_by: str,
        remarks: Optional[str],
        db: Session,
        changed_by_name: Optional[str] = None,
    ) -> Optional[Complaint]:
        """Update complaint status with validation and history tracking."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return None

        old_status = complaint.status
        valid_next = VALID_STATUS_TRANSITIONS.get(old_status, [])

        if new_status not in valid_next:
            raise ValueError(
                f"Invalid status transition: {old_status} → {new_status}. "
                f"Allowed: {valid_next}"
            )

        complaint.status = new_status
        complaint.updated_at = datetime.now(timezone.utc)

        if new_status == "RESOLVED":
            complaint.resolved_at = datetime.now(timezone.utc)
        elif new_status == "CLOSED":
            complaint.closed_at = datetime.now(timezone.utc)

        self._add_status_history(
            complaint_id=complaint_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_name=changed_by_name,
            remarks=remarks,
            db=db,
        )
        db.commit()
        db.refresh(complaint)
        return complaint

    def assign_complaint(
        self,
        complaint_id: str,
        department_id: str,
        assigned_by: str,
        db: Session,
        assigned_staff_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Complaint]:
        """Assign complaint to department and optionally to a staff member."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return None

        dept = db.query(Department).filter(Department.id == department_id).first()
        dept_name = dept.name if dept else None

        staff_name = None
        if assigned_staff_id:
            staff = db.query(User).filter(User.id == assigned_staff_id).first()
            staff_name = staff.full_name if staff else None

        complaint.department_id = department_id
        complaint.assigned_staff_id = assigned_staff_id
        complaint.updated_at = datetime.now(timezone.utc)

        # Record assignment
        assignment = ComplaintAssignment(
            id=str(uuid.uuid4()),
            complaint_id=complaint_id,
            department_id=department_id,
            department_name=dept_name,
            assigned_staff_id=assigned_staff_id,
            assigned_staff_name=staff_name,
            assigned_by=assigned_by,
            notes=notes,
        )
        db.add(assignment)

        # Advance status
        if complaint.status in ("VERIFIED", "AI_ANALYZED", "SUBMITTED"):
            self.update_status(
                complaint_id=complaint_id,
                new_status="ASSIGNED",
                changed_by=assigned_by,
                remarks=f"Assigned to {dept_name or 'department'}",
                db=db,
                changed_by_name=None,
            )
        else:
            db.commit()

        db.refresh(complaint)
        return complaint

    def get_complaint_detail(self, complaint_id: str, db: Session) -> Optional[dict]:
        """Get full complaint details with related data."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return None

        citizen = db.query(User).filter(User.id == complaint.citizen_id).first()
        dept = None
        if complaint.department_id:
            dept = db.query(Department).filter(Department.id == complaint.department_id).first()

        prediction = db.query(ComplaintPrediction).filter(
            ComplaintPrediction.complaint_id == complaint_id
        ).first()

        history = db.query(ComplaintStatusHistory).filter(
            ComplaintStatusHistory.complaint_id == complaint_id
        ).order_by(ComplaintStatusHistory.created_at.asc()).all()

        return {
            "complaint": complaint,
            "citizen": citizen,
            "department": dept,
            "prediction": prediction,
            "status_history": history,
        }

    def list_complaints(
        self,
        db: Session,
        citizen_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        department_id: Optional[str] = None,
        assigned_staff_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Complaint], int]:
        """Paginated, filterable complaint listing."""
        query = db.query(Complaint)

        if citizen_id:
            query = query.filter(Complaint.citizen_id == citizen_id)
        if status:
            query = query.filter(Complaint.status == status.upper())
        if category:
            query = query.filter(Complaint.category == category)
        if priority:
            query = query.filter(Complaint.priority == priority.upper())
        if department_id:
            query = query.filter(Complaint.department_id == department_id)
        if assigned_staff_id:
            query = query.filter(Complaint.assigned_staff_id == assigned_staff_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Complaint.description.ilike(search_term) |
                Complaint.complaint_number.ilike(search_term) |
                Complaint.location.ilike(search_term)
            )

        total = query.count()
        complaints = (
            query.order_by(Complaint.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return complaints, total

    def verify_complaint(
        self,
        complaint_id: str,
        verified_by: str,
        verified_by_name: str,
        db: Session,
        remarks: Optional[str] = None,
        corrected_category: Optional[str] = None,
        corrected_priority: Optional[str] = None,
    ) -> Optional[Complaint]:
        """Admin verifies a complaint, optionally correcting AI predictions."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return None

        complaint.is_verified = True
        if corrected_category:
            complaint.category = corrected_category
            # Store correction for future retraining
            prediction = db.query(ComplaintPrediction).filter(
                ComplaintPrediction.complaint_id == complaint_id
            ).first()
            if prediction:
                prediction.admin_corrected_category = corrected_category

        if corrected_priority:
            complaint.priority = corrected_priority
            prediction = db.query(ComplaintPrediction).filter(
                ComplaintPrediction.complaint_id == complaint_id
            ).first()
            if prediction:
                prediction.admin_corrected_priority = corrected_priority

        complaint.updated_at = datetime.now(timezone.utc)
        db.commit()

        # Update status
        if complaint.status in ("SUBMITTED", "AI_ANALYZED"):
            self.update_status(
                complaint_id=complaint_id,
                new_status="VERIFIED",
                changed_by=verified_by,
                changed_by_name=verified_by_name,
                remarks=remarks or "Complaint verified by admin",
                db=db,
            )
        else:
            db.commit()

        db.refresh(complaint)
        return complaint


complaint_service = ComplaintService()
