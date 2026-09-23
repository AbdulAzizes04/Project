import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("career_ai.database")
logging.basicConfig(level=logging.INFO)

Base = declarative_base()

def get_engine():
    """
    Initializes SQLAlchemy database engine with automatic fallback:
    1. Attempts MySQL connection using settings.DATABASE_URL.
    2. If MySQL is unavailable or credentials fail, gracefully falls back
       to a local SQLite database file to ensure the application remains 100% operational.
    """
    mysql_url = settings.DATABASE_URL
    sqlite_url = f"sqlite:///{os.path.abspath(settings.SQLITE_FALLBACK_PATH)}"

    # Try MySQL first
    try:
        engine = create_engine(
            mysql_url,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Successfully connected to MySQL database at {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        return engine
    except Exception as exc:
        logger.warning(
            f"MySQL connection to '{mysql_url}' could not be established ({exc}). "
            f"Falling back to high-performance local SQLite database at: {sqlite_url}"
        )
        engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
