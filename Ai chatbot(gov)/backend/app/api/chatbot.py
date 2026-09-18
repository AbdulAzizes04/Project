"""Chatbot API routes — conversation management."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.core.dependencies import CurrentUser, DbSession
from app.services import chatbot_service as cs

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])


class StartSessionResponse(BaseModel):
    success: bool
    session_id: str
    session: dict


class MessageRequest(BaseModel):
    session_id: str
    message: str
    image_url: Optional[str] = None


class AnalyzeRequest(BaseModel):
    session_id: str


class SubmitRequest(BaseModel):
    session_id: str


@router.post("/start", response_model=StartSessionResponse)
def start_session(current_user: CurrentUser, db: DbSession):
    """Initialize a new chatbot conversation session."""
    session = cs.create_session(citizen_id=current_user.id)
    return StartSessionResponse(
        success=True,
        session_id=session["session_id"],
        session=session,
    )


@router.post("/message")
def send_message(request: MessageRequest, current_user: CurrentUser, db: DbSession):
    """Send a message to the chatbot and get a response."""
    session = cs.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please start a new conversation.")

    if session["citizen_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this session.")

    updated_session = cs.process_message(request.session_id, request.message, db, image_url=request.image_url)

    if "error" in updated_session:
        raise HTTPException(status_code=400, detail=updated_session["error"])

    return {
        "success": True,
        "session": updated_session,
        "state": updated_session.get("state"),
        "analysis": updated_session.get("analysis"),
        "latest_message": updated_session["messages"][-1] if updated_session["messages"] else None,
    }


@router.post("/analyze")
def analyze_complaint(request: AnalyzeRequest, current_user: CurrentUser, db: DbSession):
    """
    Run the full AI pipeline on the collected session data.
    Returns classification, priority, duplicate detection, and department recommendation.
    """
    session = cs.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session["citizen_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    data = session.get("data", {})
    if not data.get("description"):
        raise HTTPException(
            status_code=400,
            detail="No complaint description found in session.",
        )

    updated_session = cs.run_ai_analysis(request.session_id, db)

    if "error" in updated_session:
        raise HTTPException(status_code=400, detail=updated_session["error"])

    return {
        "success": True,
        "session": updated_session,
        "analysis": updated_session.get("analysis"),
    }


@router.post("/submit")
def submit_complaint(request: SubmitRequest, current_user: CurrentUser, db: DbSession):
    """Submit a complaint from an analyzed chatbot session."""
    session = cs.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session["citizen_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    data = session.get("data", {})
    analysis = session.get("analysis")

    if not data.get("description"):
        raise HTTPException(status_code=400, detail="No complaint description found.")

    # Create the complaint
    from app.services.complaint_service import complaint_service
    from app.services.notification_service import notification_service

    complaint = complaint_service.create_complaint(
        citizen_id=current_user.id,
        description=data["description"],
        location=data.get("location"),
        duration=data.get("duration"),
        severity=data.get("severity"),
        raw_chat_history=session.get("messages", []),
        analysis=analysis,
        image_url=data.get("image_url"),
        db=db,
    )

    # Notify citizen
    notification_service.notify_complaint_submitted(
        citizen_id=current_user.id,
        complaint_number=complaint.complaint_number,
        complaint_id=complaint.id,
        db=db,
    )

    # Notify all admins about new complaint
    from app.models.user import User
    admins = db.query(User).filter(User.role == "admin", User.is_active == True).all()
    for admin in admins:
        notification_service.notify_admin_new_complaint(
            admin_id=admin.id,
            complaint_number=complaint.complaint_number,
            complaint_id=complaint.id,
            category=complaint.category or "Unknown",
            db=db,
        )

    # Mark session as complete
    if request.session_id in cs._sessions:
        cs._sessions[request.session_id]["state"] = cs.STATE_COMPLETE

    dept_name = analysis.get("recommended_department_name") if analysis else "General Municipal Redressal"

    return {
        "success": True,
        "message": "Grievance successfully submitted and routed to Administration.",
        "complaint_id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "ticket_number": complaint.complaint_number,
        "status": complaint.status,
        "category": complaint.category,
        "priority": complaint.priority,
        "image_url": complaint.image_url,
        "department_name": dept_name,
        "routing_stage": "ADMINISTRATIVE_VERIFICATION",
    }


@router.get("/session/{session_id}")
def get_session(session_id: str, current_user: CurrentUser):
    """Get the current state of a chatbot session."""
    session = cs.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session["citizen_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")
    return {"success": True, "session": session}
