"""Analytics Service — aggregates complaint data for dashboard and charts."""
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models.complaint import Complaint
from app.models.user import User
from app.models.department import Department
from app.models.prediction import ComplaintPrediction, ModelEvaluation


class AnalyticsService:

    def get_dashboard_stats(self, db: Session) -> dict:
        total = db.query(Complaint).count()
        pending = db.query(Complaint).filter(
            Complaint.status.in_(["SUBMITTED", "AI_ANALYZED"])
        ).count()
        in_progress = db.query(Complaint).filter(
            Complaint.status.in_(["VERIFIED", "ASSIGNED", "IN_PROGRESS"])
        ).count()
        resolved = db.query(Complaint).filter(Complaint.status == "RESOLVED").count()
        closed = db.query(Complaint).filter(Complaint.status == "CLOSED").count()
        critical = db.query(Complaint).filter(
            Complaint.priority == "Critical"
        ).count()
        possible_duplicates = db.query(ComplaintPrediction).filter(
            ComplaintPrediction.is_duplicate == True
        ).count()
        verified = db.query(Complaint).filter(Complaint.is_verified == True).count()
        unverified = total - verified
        total_citizens = db.query(User).filter(User.role == "citizen").count()
        total_depts = db.query(Department).filter(Department.is_active == True).count()

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        complaints_today = db.query(Complaint).filter(
            Complaint.created_at >= today_start
        ).count()

        resolution_rate = 0.0
        if total > 0:
            resolution_rate = round(((resolved + closed) / total) * 100, 1)

        return {
            "total_complaints": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed,
            "critical": critical,
            "possible_duplicates": possible_duplicates,
            "verified": verified,
            "unverified": unverified,
            "total_citizens": total_citizens,
            "total_departments": total_depts,
            "complaints_today": complaints_today,
            "resolution_rate": resolution_rate,
        }

    def complaints_by_category(self, db: Session) -> List[dict]:
        rows = (
            db.query(Complaint.category, func.count(Complaint.id).label("count"))
            .filter(Complaint.category.isnot(None))
            .group_by(Complaint.category)
            .all()
        )
        total = sum(r.count for r in rows)
        return [
            {
                "category": r.category,
                "count": r.count,
                "percentage": round((r.count / total) * 100, 1) if total > 0 else 0,
            }
            for r in sorted(rows, key=lambda x: x.count, reverse=True)
        ]

    def complaints_by_priority(self, db: Session) -> List[dict]:
        rows = (
            db.query(Complaint.priority, func.count(Complaint.id).label("count"))
            .filter(Complaint.priority.isnot(None))
            .group_by(Complaint.priority)
            .all()
        )
        total = sum(r.count for r in rows)
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        return [
            {
                "priority": r.priority,
                "count": r.count,
                "percentage": round((r.count / total) * 100, 1) if total > 0 else 0,
            }
            for r in sorted(rows, key=lambda x: priority_order.get(x.priority, 99))
        ]

    def complaints_by_status(self, db: Session) -> List[dict]:
        rows = (
            db.query(Complaint.status, func.count(Complaint.id).label("count"))
            .group_by(Complaint.status)
            .all()
        )
        total = sum(r.count for r in rows)
        return [
            {
                "status": r.status,
                "count": r.count,
                "percentage": round((r.count / total) * 100, 1) if total > 0 else 0,
            }
            for r in sorted(rows, key=lambda x: x.count, reverse=True)
        ]

    def complaints_by_department(self, db: Session) -> List[dict]:
        depts = db.query(Department).filter(Department.is_active == True).all()
        result = []
        for dept in depts:
            total = db.query(Complaint).filter(Complaint.department_id == dept.id).count()
            resolved = db.query(Complaint).filter(
                Complaint.department_id == dept.id,
                Complaint.status.in_(["RESOLVED", "CLOSED"]),
            ).count()
            pending = total - resolved
            result.append({
                "department_id": dept.id,
                "department_name": dept.name,
                "total": total,
                "resolved": resolved,
                "pending": pending,
            })
        return sorted(result, key=lambda x: x["total"], reverse=True)

    def complaints_timeline(self, db: Session, days: int = 30) -> List[dict]:
        """Complaints created per day for the last N days."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(
                func.date(Complaint.created_at).label("date"),
                func.count(Complaint.id).label("count"),
            )
            .filter(Complaint.created_at >= start_date)
            .group_by(func.date(Complaint.created_at))
            .order_by(func.date(Complaint.created_at))
            .all()
        )
        return [{"date": str(r.date), "count": r.count} for r in rows]

    def get_model_metrics(self, db: Session) -> List[dict]:
        """Returns actual model evaluation metrics from the database."""
        evals = (
            db.query(ModelEvaluation)
            .order_by(ModelEvaluation.evaluated_at.desc())
            .all()
        )
        return [
            {
                "model_name": e.model_name,
                "model_type": e.model_type,
                "algorithm": e.algorithm,
                "accuracy": e.accuracy,
                "precision_score": e.precision_score,
                "recall_score": e.recall_score,
                "f1_score": e.f1_score,
                "train_accuracy": e.train_accuracy,
                "dataset_size": e.dataset_size,
                "confusion_matrix": e.confusion_matrix,
                "classification_report": e.classification_report,
                "label_names": e.label_names,
                "evaluated_at": e.evaluated_at.isoformat() if e.evaluated_at else None,
                "is_active": e.is_active,
            }
            for e in evals
        ]


analytics_service = AnalyticsService()
