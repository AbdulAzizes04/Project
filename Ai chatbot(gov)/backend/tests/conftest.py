"""
Pytest configuration and shared fixtures for backend tests.
Uses SQLite in-memory database with test clients.
"""
import os
import sys
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.core.database import Base, get_db
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.department import Department

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables in the in-memory test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator:
    """Provide a transactional database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator:
    """FastAPI TestClient with overridden database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session) -> User:
    """Create a persistent test admin user."""
    user = db_session.query(User).filter_by(email="testadmin@gov.in").first()
    if not user:
        user = User(
            id="admin-test-uuid",
            email="testadmin@gov.in",
            full_name="Test Administrator",
            password_hash=hash_password("AdminTest@123"),
            role="admin",
            phone="9876543210",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def test_citizen_user(db_session) -> User:
    """Create a persistent test citizen user."""
    user = db_session.query(User).filter_by(email="testcitizen@gmail.com").first()
    if not user:
        user = User(
            id="citizen-test-uuid",
            email="testcitizen@gmail.com",
            full_name="Ramesh Sharma",
            password_hash=hash_password("Citizen@123"),
            role="citizen",
            phone="9876543211",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(test_admin_user) -> str:
    """Generate JWT access token for admin."""
    return create_access_token(
        subject=test_admin_user.id,
        role=test_admin_user.role,
        extra_data={"email": test_admin_user.email},
    )


@pytest.fixture
def citizen_token(test_citizen_user) -> str:
    """Generate JWT access token for citizen."""
    return create_access_token(
        subject=test_citizen_user.id,
        role=test_citizen_user.role,
        extra_data={"email": test_citizen_user.email},
    )


@pytest.fixture
def test_department(db_session) -> Department:
    """Create a test department."""
    dept = db_session.query(Department).filter_by(code="WATER").first()
    if not dept:
        dept = Department(
            id="dept-water-uuid",
            name="Department of Water Supply & Sewerage",
            code="WATER",
            description="Handles piped water supply, pipeline leaks, contamination, and low pressure issues.",
            category_mapping="Water Supply",
            is_active=True,
        )
        db_session.add(dept)
        db_session.commit()
        db_session.refresh(dept)
    return dept
