"""
Conversational Chatbot Service.
State machine that guides citizens through complaint registration:
1. What happened? (Detailed issue description)
2. Where? (Specific location, street, ward, landmark)
3. From when? (Duration / time frame)
4. Picture / Photo Evidence (Optional attachment upload)
5. AI Diagnostics & Report Generation (Classification, Priority, SLA, Dept)
6. Administrative Routing (Citizen ➔ Admin / TPO ➔ Department ➔ Field Staff)
"""
import uuid
from typing import Optional
from datetime import datetime, timezone
from loguru import logger


# ─── Conversation States ───────────────────────────────────────────────────────
STATE_GREETING = "GREETING"
STATE_COLLECT_DESCRIPTION = "COLLECT_DESCRIPTION"
STATE_COLLECT_LOCATION = "COLLECT_LOCATION"
STATE_COLLECT_DURATION = "COLLECT_DURATION"
STATE_COLLECT_PHOTO = "COLLECT_PHOTO"
STATE_ANALYZING = "ANALYZING"
STATE_SUMMARY = "SUMMARY"
STATE_COMPLETE = "COMPLETE"

# In-memory session store
_sessions: dict = {}

QUICK_REPLIES_CATEGORY = [
    "💧 Water Supply & Leakage",
    "🛣️ Road Damage & Potholes",
    "🗑️ Garbage & Waste Cleanup",
    "⚡ Electricity Outage / Sparks",
    "💡 Streetlight Not Working",
    "🌊 Drainage / Sewage Overflow",
]

QUICK_REPLIES_DURATION = [
    "Since today morning",
    "Since 2 to 3 days",
    "For about 1 week",
    "More than 2 weeks",
]

QUICK_REPLIES_PHOTO = [
    "📷 Upload Photo",
    "⏩ Skip / No Photo",
]


def create_session(citizen_id: str) -> dict:
    """Initialize a new chatbot session."""
    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "citizen_id": citizen_id,
        "state": STATE_GREETING,
        "messages": [],
        "data": {
            "description": None,
            "location": None,
            "duration": None,
            "severity": "Medium",
            "image_url": None,
        },
        "analysis": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _sessions[session_id] = session

    # Step 1: Initial greeting and prompt asking "What happened?"
    bot_msg = {
        "role": "bot",
        "content": (
            "👋 **Welcome to LokSeva AI Grievance Intake Portal.**\n\n"
            "I will assist you in creating an official grievance report and routing it through administrative verification to the responsible municipal department.\n\n"
            "📋 **Step 1 of 4: What happened?**\n"
            "Please describe the problem or issue you are experiencing in detail (e.g., *a major water pipeline burst leaking onto the road*, *huge pothole causing traffic accidents*, *sewage overflow*):"
        ),
        "quick_replies": QUICK_REPLIES_CATEGORY,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    session["messages"].append(bot_msg)
    session["state"] = STATE_COLLECT_DESCRIPTION

    return session


def get_session(session_id: str) -> Optional[dict]:
    return _sessions.get(session_id)


def process_message(session_id: str, user_message: str, db=None, image_url: Optional[str] = None) -> dict:
    """
    Process a user message and advance the conversation state through:
    What happened -> Where -> From when -> Picture -> Report generation.
    """
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found. Please start a new conversation."}

    user_text = user_message.strip()

    # If an image_url is attached directly to the message
    if image_url:
        session["data"]["image_url"] = image_url

    # Add user message to history
    session["messages"].append({
        "role": "user",
        "content": user_text,
        "image_url": image_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    state = session["state"]
    data = session["data"]
    bot_response = None
    quick_replies = None

    # ─── State Machine ────────────────────────────────────────────────────────

    if state == STATE_COLLECT_DESCRIPTION:
        data["description"] = user_text

        # Try to infer severity or duration from description if present
        from app.ml.preprocessing.text_preprocessor import extract_duration, infer_severity
        dur = extract_duration(user_text)
        if dur:
            data["duration"] = dur
        data["severity"] = infer_severity(user_text)

        # Transition to Step 2: Where
        session["state"] = STATE_COLLECT_LOCATION
        bot_response = (
            f"✅ Issue recorded: **\"{data['description']}\"**\n\n"
            f"📍 **Step 2 of 4: Where did it happen?**\n"
            f"Please enter the exact location, street address, ward number, or nearby landmark (e.g., *Proddatur Main Bazaar, near Gandhi Statue, Ward 12*):"
        )

    elif state == STATE_COLLECT_LOCATION:
        data["location"] = user_text

        # If duration was not auto-extracted, ask for duration
        if not data.get("duration"):
            session["state"] = STATE_COLLECT_DURATION
            bot_response = (
                f"📍 Location noted: **{data['location']}**\n\n"
                f"⏱️ **Step 3 of 4: From when has this issue been occurring?**\n"
                f"How long have you been facing this problem? (e.g., *Since today morning*, *Since 3 days*, *For about 1 week*):"
            )
            quick_replies = QUICK_REPLIES_DURATION
        else:
            # Skip to Step 4: Photo
            session["state"] = STATE_COLLECT_PHOTO
            bot_response = (
                f"📍 Location: **{data['location']}**\n"
                f"⏱️ Duration: **{data['duration']}**\n\n"
                f"📸 **Step 4 of 4: Would you like to share a picture of the issue?**\n"
                f"Attaching a photo helps municipal officials verify the grievance on-site and resolve it faster.\n\n"
                f"Click **📷 Attach Photo** to upload a picture, or select **Skip Photo** to generate the report now."
            )
            quick_replies = QUICK_REPLIES_PHOTO

    elif state == STATE_COLLECT_DURATION:
        data["duration"] = user_text

        # Transition to Step 4: Photo
        session["state"] = STATE_COLLECT_PHOTO
        bot_response = (
            f"⏱️ Duration noted: **{data['duration']}**\n\n"
            f"📸 **Step 4 of 4: Would you like to share a picture of the issue?**\n"
            f"Attaching a photo helps municipal officials verify the grievance on-site and resolve it faster.\n\n"
            f"Click **📷 Attach Photo** to upload a picture, or select **Skip Photo** to generate the report now."
        )
        quick_replies = QUICK_REPLIES_PHOTO

    elif state == STATE_COLLECT_PHOTO:
        # User uploaded photo or typed skip / attach
        lower_msg = user_text.lower()
        if "skip" in lower_msg or "no photo" in lower_msg or "none" in lower_msg:
            # Proceed without photo
            pass
        elif image_url:
            data["image_url"] = image_url
        elif user_text.startswith("/uploads/") or user_text.startswith("http"):
            data["image_url"] = user_text

        # Advance to AI Analysis and Report Generation
        session["state"] = STATE_ANALYZING
        bot_response = (
            "✨ **All grievance details gathered!**\n\n"
            "🤖 **Running LokSeva AI Diagnostics...**\n"
            "• Classifying civic sector & recommended department\n"
            "• Predicting priority level & SLA resolution window\n"
            "• Scanning for duplicate complaints in this locality\n"
            "• Compiling formal Grievance Report for administrative review..."
        )

    elif state in (STATE_ANALYZING, STATE_SUMMARY):
        # Allow user to update or confirm
        if "submit" in user_text.lower() or "confirm" in user_text.lower():
            bot_response = "Please click the **Confirm & Submit Grievance** button below to register your report."
        else:
            bot_response = (
                "Your grievance report has been generated. "
                "You can review the AI details below and click **Confirm & Submit Grievance** to submit it to the Administration."
            )

    elif state == STATE_COMPLETE:
        bot_response = (
            "This complaint has already been submitted and routed to the Administration! "
            "You can track its resolution status anytime using your ticket number."
        )

    else:
        session["state"] = STATE_COLLECT_DESCRIPTION
        bot_response = "Let's begin again. What problem are you facing?"
        quick_replies = QUICK_REPLIES_CATEGORY

    # Append bot response to message history
    if bot_response:
        msg = {
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if quick_replies:
            msg["quick_replies"] = quick_replies
        session["messages"].append(msg)

    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Automatically trigger AI analysis if state reached STATE_ANALYZING and db session is provided
    if session["state"] == STATE_ANALYZING and db:
        run_ai_analysis(session_id, db)

    return session


def run_ai_analysis(session_id: str, db) -> dict:
    """
    Run full AI pipeline on collected session data.
    Returns analysis results and advances state to STATE_SUMMARY.
    """
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}

    data = session["data"]
    description = data.get("description", "")
    location = data.get("location", "")
    severity = data.get("severity", "Medium")
    duration = data.get("duration", "Recent")

    full_text = f"{description}. Location: {location}. Duration: {duration}. Severity: {severity}"

    # 1. Classification
    from app.services.classification_service import classification_service
    classification = classification_service.classify(description)

    # 2. Priority
    from app.services.priority_service import priority_service
    priority = priority_service.predict_priority(
        text=description,
        category=classification["category"],
        severity=severity,
        duration=duration,
    )

    # 3. Duplicate detection
    from app.services.duplicate_service import duplicate_service
    duplicate = duplicate_service.check_duplicate(
        new_text=full_text,
        db=db,
        location=location,
    )

    # 4. Department recommendation (DB-driven)
    from app.services.department_service import department_service
    dept_id, dept_name = department_service.recommend_department(
        classification["category"], db
    )

    # Dynamic SLA resolution mapping
    sla_map = {
        "CRITICAL": 12,
        "HIGH": 48,
        "MEDIUM": 96,
        "LOW": 168,
    }
    prio_key = str(priority.get("priority", "MEDIUM")).upper()
    sla_hours = sla_map.get(prio_key, 72)

    overall_confidence = (
        classification["confidence"] * 0.6 + priority["confidence"] * 0.4
    )

    analysis = {
        "classification": {
            "category": classification["category"],
            "confidence": round(classification["confidence"], 4),
            "all_scores": classification.get("all_scores", {}),
            "low_confidence": classification.get("low_confidence", False),
        },
        "priority": {
            "priority": priority["priority"],
            "confidence": round(priority["confidence"], 4),
            "sla_hours": sla_hours,
            "all_scores": priority.get("all_scores", {}),
            "rule_based_fallback": priority.get("rule_based_fallback", False),
        },
        "duplicate": duplicate,
        "recommended_department_id": dept_id,
        "recommended_department_name": dept_name or "General Civic Redressal",
        "overall_confidence": round(overall_confidence, 4),
    }

    session["analysis"] = analysis
    session["state"] = STATE_SUMMARY

    # Structured summary message
    cat = classification["category"]
    pri = priority["priority"]
    conf = round(classification["confidence"] * 100, 1)
    dup_text = "⚠️ Similar complaint exists in this ward" if duplicate["is_duplicate"] else "✅ Unique complaint (No duplicates)"
    has_photo = "Attached" if data.get("image_url") else "None"

    summary_msg = {
        "role": "bot",
        "content": (
            f"📋 **FORMAL GRIEVANCE REPORT PREPARED**\n\n"
            f"• **What Happened:** {data.get('description')}\n"
            f"• **Location:** {data.get('location')}\n"
            f"• **From When:** {data.get('duration')}\n"
            f"• **Photo Evidence:** {has_photo}\n"
            f"• **AI Category:** {cat} ({conf}% confidence)\n"
            f"• **AI Priority:** {pri} (Target SLA: {sla_hours} hours)\n"
            f"• **Assigned Routing:** Citizen ➔ **Administrative Officer (TPO)** ➔ **{dept_name}** ➔ Field Staff\n"
            f"• **Duplicate Scan:** {dup_text}\n\n"
            f"Please review the report card below and click **Confirm & Submit Grievance** to route this to the Municipal Administration for verification and dispatch."
        ),
        "type": "report_ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    session["messages"].append(summary_msg)
    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    return session
