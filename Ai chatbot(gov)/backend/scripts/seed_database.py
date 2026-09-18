"""
Database Seed Script.
Creates initial data for development and demo purposes.

Creates:
  - 1 Admin user
  - 6 Departments (one per complaint category)
  - 2 Staff users (one per department pair)
  - 5 Citizen accounts
  - 20 Sample complaints with AI predictions

Usage:
    cd backend
    python scripts/seed_database.py
"""
import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, create_tables
from app.core.security import hash_password
from app.models.user import User
from app.models.department import Department
from app.models.complaint import Complaint, ComplaintStatusHistory, ComplaintAssignment
from app.models.prediction import ComplaintPrediction, ModelEvaluation
from app.models.notification import Notification

random.seed(42)


# ─── Demo credentials (DEVELOPMENT ONLY) ──────────────────────────────────────
ADMIN = {
    "email": "admin@gov.in",
    "password": "Admin@123",
    "full_name": "System Administrator",
    "role": "admin",
}

STAFF_ACCOUNTS = [
    {
        "email": "staff.water@gov.in",
        "password": "Staff@123",
        "full_name": "Ravi Kumar",
        "role": "staff",
        "dept_code": "WATER",
    },
    {
        "email": "staff.roads@gov.in",
        "password": "Staff@123",
        "full_name": "Priya Sharma",
        "role": "staff",
        "dept_code": "ROADS",
    },
    {
        "email": "staff.sanitation@gov.in",
        "password": "Staff@123",
        "full_name": "Suresh Reddy",
        "role": "staff",
        "dept_code": "SANITATION",
    },
]

CITIZENS = [
    {"email": "ramesh.sharma@gmail.com", "password": "Citizen@123", "full_name": "Ramesh Sharma", "phone": "9876543210"},
    {"email": "citizen1@example.com", "password": "Citizen@123", "full_name": "Rajesh Patel", "phone": "9876543210"},
    {"email": "citizen2@example.com", "password": "Citizen@123", "full_name": "Meera Nair", "phone": "9876543211"},
    {"email": "citizen3@example.com", "password": "Citizen@123", "full_name": "Arun Kumar", "phone": "9876543212"},
    {"email": "citizen4@example.com", "password": "Citizen@123", "full_name": "Sunita Devi", "phone": "9876543213"},
    {"email": "citizen5@example.com", "password": "Citizen@123", "full_name": "Vikram Singh", "phone": "9876543214"},
    {"email": "demo@citizen.com", "password": "Demo@123", "full_name": "Demo Citizen", "phone": "9000000001"},
]

DEPARTMENTS = [
    {
        "name": "Water Supply Department",
        "code": "WATER",
        "category_mapping": "Water Supply",
        "description": "Manages drinking water supply, pipelines, and water quality.",
        "head_name": "Mr. D.K. Rao",
        "contact_email": "water@municipality.gov.in",
        "contact_phone": "1800-111-001",
    },
    {
        "name": "Roads & Infrastructure Department",
        "code": "ROADS",
        "category_mapping": "Roads",
        "description": "Road construction, maintenance, and traffic infrastructure.",
        "head_name": "Ms. A. Verma",
        "contact_email": "roads@municipality.gov.in",
        "contact_phone": "1800-111-002",
    },
    {
        "name": "Sanitation Department",
        "code": "SANITATION",
        "category_mapping": "Sanitation",
        "description": "Waste collection, public toilet maintenance, and cleanliness.",
        "head_name": "Mr. P. Nair",
        "contact_email": "sanitation@municipality.gov.in",
        "contact_phone": "1800-111-003",
    },
    {
        "name": "Electricity Department",
        "code": "ELECTRICITY",
        "category_mapping": "Electricity",
        "description": "Power supply, transformer maintenance, and electrical safety.",
        "head_name": "Mr. S. Chandra",
        "contact_email": "electricity@municipality.gov.in",
        "contact_phone": "1800-111-004",
    },
    {
        "name": "Street Lighting Department",
        "code": "STREETLIGHT",
        "category_mapping": "Street Lighting",
        "description": "Street light installation, repair, and maintenance.",
        "head_name": "Ms. R. Kumari",
        "contact_email": "streetlight@municipality.gov.in",
        "contact_phone": "1800-111-005",
    },
    {
        "name": "Drainage Department",
        "code": "DRAINAGE",
        "category_mapping": "Drainage",
        "description": "Drain cleaning, sewage management, and flood prevention.",
        "head_name": "Mr. K. Reddy",
        "contact_email": "drainage@municipality.gov.in",
        "contact_phone": "1800-111-006",
    },
]

SAMPLE_COMPLAINTS = [
    {
        "description": "There has been no water supply in our area for the last three days. "
                       "The entire Ward 5 colony is affected and people are suffering without drinking water.",
        "location": "Ward 5, Rajampet",
        "duration": "3 days",
        "severity": "High",
        "category": "Water Supply",
        "priority": "High",
        "dept_code": "WATER",
        "status": "RESOLVED",
    },
    {
        "description": "The road near MG Road has too many potholes and is causing accidents. "
                       "Two-wheelers are falling into them every day.",
        "location": "MG Road, near bus stand",
        "duration": "2 weeks",
        "severity": "High",
        "category": "Roads",
        "priority": "High",
        "dept_code": "ROADS",
        "status": "IN_PROGRESS",
    },
    {
        "description": "Garbage has not been collected in Gandhi Nagar for 5 days. "
                       "The dustbin is overflowing and creating a health hazard.",
        "location": "Gandhi Nagar, Main Street",
        "duration": "5 days",
        "severity": "Medium",
        "category": "Sanitation",
        "priority": "Medium",
        "dept_code": "SANITATION",
        "status": "ASSIGNED",
    },
    {
        "description": "Street light near RTC bus stand is not working for the past week. "
                       "Women feel unsafe walking at night.",
        "location": "RTC Bus Stand, Rajampet",
        "duration": "1 week",
        "severity": "High",
        "category": "Street Lighting",
        "priority": "High",
        "dept_code": "STREETLIGHT",
        "status": "VERIFIED",
    },
    {
        "description": "Power supply is completely disrupted in Nehru Colony since yesterday. "
                       "Transformer has blown and nobody has come to fix it.",
        "location": "Nehru Colony, Block C",
        "duration": "1 day",
        "severity": "Critical",
        "category": "Electricity",
        "priority": "Critical",
        "dept_code": "ELECTRICITY",
        "status": "IN_PROGRESS",
    },
    {
        "description": "Drain near Ambedkar Nagar is blocked and water is overflowing on the road. "
                       "Mosquitoes are breeding and there is a bad smell.",
        "location": "Ambedkar Nagar, Ward 12",
        "duration": "10 days",
        "severity": "High",
        "category": "Drainage",
        "priority": "High",
        "dept_code": "DRAINAGE",
        "status": "SUBMITTED",
    },
    {
        "description": "Water not coming from tap for 2 days in Srinivasa Nagar.",
        "location": "Srinivasa Nagar",
        "duration": "2 days",
        "severity": "Medium",
        "category": "Water Supply",
        "priority": "Medium",
        "dept_code": "WATER",
        "status": "AI_ANALYZED",
    },
    {
        "description": "Road surface broken in Old Town after heavy rain. Large cracks visible.",
        "location": "Old Town, Station Road",
        "duration": "4 days",
        "severity": "Medium",
        "category": "Roads",
        "priority": "Medium",
        "dept_code": "ROADS",
        "status": "SUBMITTED",
    },
    {
        "description": "Sewage water is entering our homes in Lakshmi Puram. "
                       "The sewer line is broken and needs immediate repair.",
        "location": "Lakshmi Puram, 3rd Street",
        "duration": "2 days",
        "severity": "Critical",
        "category": "Drainage",
        "priority": "Critical",
        "dept_code": "DRAINAGE",
        "status": "ASSIGNED",
    },
    {
        "description": "Public water tap not working in Patel Nagar for a week.",
        "location": "Patel Nagar",
        "duration": "1 week",
        "severity": "Medium",
        "category": "Water Supply",
        "priority": "Medium",
        "dept_code": "WATER",
        "status": "RESOLVED",
    },
]


def seed():
    print("=" * 60)
    print("  Seeding Database")
    print("=" * 60)

    create_tables()
    db = SessionLocal()

    try:
        # ── Departments ────────────────────────────────────────────────────────
        dept_map = {}  # code → Department object
        print("\n[1/5] Creating departments...")
        for dept_data in DEPARTMENTS:
            existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
            if not existing:
                dept = Department(id=str(uuid.uuid4()), **dept_data)
                db.add(dept)
                db.flush()
                dept_map[dept_data["code"]] = dept
                print(f"  [OK] {dept_data['name']}")
            else:
                dept_map[dept_data["code"]] = existing
                print(f"  - {dept_data['name']} (exists)")

        db.commit()

        # ── Admin ──────────────────────────────────────────────────────────────
        print("\n[2/5] Creating admin user...")
        admin = db.query(User).filter(User.email == ADMIN["email"]).first()
        if not admin:
            admin = User(
                id=str(uuid.uuid4()),
                email=ADMIN["email"],
                full_name=ADMIN["full_name"],
                password_hash=hash_password(ADMIN["password"]),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"  [OK] Admin: {ADMIN['email']} / {ADMIN['password']}")
        else:
            print(f"  - Admin exists: {ADMIN['email']}")

        # ── Staff ──────────────────────────────────────────────────────────────
        print("\n[3/5] Creating staff accounts...")
        for staff_data in STAFF_ACCOUNTS:
            existing = db.query(User).filter(User.email == staff_data["email"]).first()
            if not existing:
                dept = dept_map.get(staff_data["dept_code"])
                staff = User(
                    id=str(uuid.uuid4()),
                    email=staff_data["email"],
                    full_name=staff_data["full_name"],
                    password_hash=hash_password(staff_data["password"]),
                    role="staff",
                    department_id=dept.id if dept else None,
                    is_active=True,
                )
                db.add(staff)
                print(f"  [OK] Staff: {staff_data['email']} / {staff_data['password']}")
            else:
                print(f"  - Staff exists: {staff_data['email']}")
        db.commit()

        # ── Citizens ────────────────────────────────────────────────────────────
        print("\n[4/5] Creating citizen accounts...")
        citizen_ids = []
        for cit_data in CITIZENS:
            existing = db.query(User).filter(User.email == cit_data["email"]).first()
            if not existing:
                cit = User(
                    id=str(uuid.uuid4()),
                    email=cit_data["email"],
                    full_name=cit_data["full_name"],
                    phone=cit_data.get("phone"),
                    password_hash=hash_password(cit_data["password"]),
                    role="citizen",
                    is_active=True,
                )
                db.add(cit)
                db.flush()
                citizen_ids.append(cit.id)
                print(f"  [OK] Citizen: {cit_data['email']} / {cit_data['password']}")
            else:
                citizen_ids.append(existing.id)
                print(f"  - Citizen exists: {cit_data['email']}")
        db.commit()

        # ── Sample Complaints ──────────────────────────────────────────────────
        print("\n[5/5] Creating sample complaints...")
        existing_count = db.query(Complaint).count()
        if existing_count == 0 and citizen_ids:
            for i, comp_data in enumerate(SAMPLE_COMPLAINTS):
                cid = citizen_ids[i % len(citizen_ids)]
                year = datetime.now(timezone.utc).year
                num = str(uuid.uuid4().int)[:6].zfill(6)
                complaint_number = f"GRV-{year}-{num}"

                dept = dept_map.get(comp_data["dept_code"])

                # Create complaint
                comp = Complaint(
                    id=str(uuid.uuid4()),
                    complaint_number=complaint_number,
                    citizen_id=cid,
                    description=comp_data["description"],
                    location=comp_data["location"],
                    duration=comp_data["duration"],
                    severity=comp_data["severity"],
                    status=comp_data["status"],
                    category=comp_data["category"],
                    priority=comp_data["priority"],
                    department_id=dept.id if dept else None,
                    is_verified=comp_data["status"] not in ("SUBMITTED", "AI_ANALYZED"),
                    raw_chat_history=[],
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30)),
                )

                if comp_data["status"] in ("RESOLVED",):
                    comp.resolved_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5))
                    comp.resolution_notes = "Issue has been addressed and resolved by the department."

                db.add(comp)
                db.flush()

                # AI Prediction record
                confidence = round(random.uniform(0.82, 0.97), 4)
                pred = ComplaintPrediction(
                    id=str(uuid.uuid4()),
                    complaint_id=comp.id,
                    predicted_category=comp_data["category"],
                    category_confidence=confidence,
                    predicted_priority=comp_data["priority"],
                    priority_confidence=round(random.uniform(0.78, 0.95), 4),
                    is_duplicate=False,
                    recommended_department_id=dept.id if dept else None,
                    recommended_department_name=dept.name if dept else None,
                    low_confidence_flag=confidence < 0.70,
                    model_version="1.0.0",
                )
                db.add(pred)

                # Status history
                statuses = _get_status_chain(comp_data["status"])
                for j, (old_s, new_s) in enumerate(statuses):
                    db.add(ComplaintStatusHistory(
                        id=str(uuid.uuid4()),
                        complaint_id=comp.id,
                        old_status=old_s,
                        new_status=new_s,
                        changed_by=admin.id,
                        changed_by_name="System Administrator",
                        remarks=_get_remark(new_s),
                    ))

                print(f"  [OK] {complaint_number} - {comp_data['category']} [{comp_data['status']}]")

            db.commit()
        else:
            print(f"  - {existing_count} complaints already exist, skipping.")

        print("\n" + "=" * 60)
        print("  Seed Complete!")
        print("=" * 60)
        print("\n  Demo Credentials:")
        print(f"  Admin:   {ADMIN['email']} / {ADMIN['password']}")
        for s in STAFF_ACCOUNTS[:2]:
            print(f"  Staff:   {s['email']} / {s['password']}")
        print(f"  Citizen: demo@citizen.com / Demo@123")
        print("\n  API Docs: http://localhost:8000/docs")
        print("=" * 60)

    finally:
        db.close()


def _get_status_chain(final_status: str) -> list:
    """Build status history chain from SUBMITTED to final_status."""
    chain = ["SUBMITTED", "AI_ANALYZED", "VERIFIED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
    try:
        end_idx = chain.index(final_status)
    except ValueError:
        end_idx = 0
    pairs = []
    for i in range(end_idx + 1):
        pairs.append((chain[i - 1] if i > 0 else None, chain[i]))
    return pairs


def _get_remark(status: str) -> str:
    remarks = {
        "SUBMITTED": "Complaint submitted by citizen via chatbot.",
        "AI_ANALYZED": "AI analysis completed: classification and priority assigned.",
        "VERIFIED": "Complaint verified by administrator.",
        "ASSIGNED": "Complaint assigned to department for resolution.",
        "IN_PROGRESS": "Department staff has started working on the complaint.",
        "RESOLVED": "Issue has been resolved. Notification sent to citizen.",
        "CLOSED": "Complaint closed after resolution confirmation.",
    }
    return remarks.get(status, "Status updated.")


if __name__ == "__main__":
    seed()
