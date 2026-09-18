"""
Department Recommendation Service.
Maps predicted complaint categories to departments using database records.
No hard-coded category→department mappings in application code.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from loguru import logger
from app.models.department import Department


class DepartmentService:

    def recommend_department(
        self, category: str, db: Session
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the department that handles the given complaint category.
        Uses DB-driven mapping (category_mapping column).

        Returns: (department_id, department_name)
        """
        if not category:
            return None, None

        # Exact match first
        dept = db.query(Department).filter(
            Department.category_mapping == category,
            Department.is_active == True,
        ).first()

        if not dept:
            # Partial match (case-insensitive)
            dept = db.query(Department).filter(
                Department.category_mapping.ilike(f"%{category}%"),
                Department.is_active == True,
            ).first()

        if dept:
            return dept.id, dept.name

        logger.warning(f"No department found for category: {category}")
        return None, None

    def get_all_departments(self, db: Session) -> list:
        return db.query(Department).filter(Department.is_active == True).all()

    def get_department_by_id(self, dept_id: str, db: Session) -> Optional[Department]:
        return db.query(Department).filter(Department.id == dept_id).first()

    def get_department_staff(self, dept_id: str, db: Session) -> list:
        from app.models.user import User
        return db.query(User).filter(
            User.department_id == dept_id,
            User.role == "staff",
            User.is_active == True,
        ).all()

    def create_department(self, data: dict, db: Session) -> Department:
        import uuid
        dept = Department(
            id=str(uuid.uuid4()),
            **data,
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept

    def update_department(self, dept_id: str, updates: dict, db: Session) -> Optional[Department]:
        dept = self.get_department_by_id(dept_id, db)
        if not dept:
            return None
        for key, value in updates.items():
            if value is not None:
                setattr(dept, key, value)
        db.commit()
        db.refresh(dept)
        return dept


department_service = DepartmentService()
