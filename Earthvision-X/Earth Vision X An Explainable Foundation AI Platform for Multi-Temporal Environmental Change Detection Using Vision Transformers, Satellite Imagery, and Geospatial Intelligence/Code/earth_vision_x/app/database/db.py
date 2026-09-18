"""
Database Connection and Session Factory for EARTH VISION-X.
Supports SQLite out-of-the-box and seamless transition to PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from earth_vision_x.app.config.settings import settings
from earth_vision_x.app.config.logging_config import logger

Base = declarative_base()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at: {settings.DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_db():
    """Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
