"""
Database engine, session factory, and Base class.
Uses SQLAlchemy 2.x with SQLite (development) or PostgreSQL (production).
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _get_engine():
    """Create the appropriate database engine based on DATABASE_URL."""
    if settings.DATABASE_URL.startswith("sqlite"):
        # SQLite: disable check_same_thread (required for FastAPI threading)
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG,
        )

        # Enable WAL mode and foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    else:
        # PostgreSQL / other databases
        return create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
        )


engine = _get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in ORM models. Called at application startup."""
    # Import all models so SQLAlchemy can discover them
    from app.models import user, complaint, department, prediction, notification, audit  # noqa
    Base.metadata.create_all(bind=engine)
