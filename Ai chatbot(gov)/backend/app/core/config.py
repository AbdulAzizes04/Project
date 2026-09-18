"""
Application configuration using Pydantic Settings.
All values are loaded from environment variables or .env file.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AI Grievance Redressal System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-32chars!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./grievance.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ML Models
    MODEL_DIR: str = "app/ml/models"
    CLASSIFIER_MODEL_PATH: str = "app/ml/models/complaint_classifier.pkl"
    PRIORITY_MODEL_PATH: str = "app/ml/models/priority_predictor.pkl"
    VECTORIZER_PATH: str = "app/ml/models/tfidf_vectorizer.pkl"
    PRIORITY_VECTORIZER_PATH: str = "app/ml/models/priority_vectorizer.pkl"

    # Sentence Transformer
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # Thresholds
    DUPLICATE_THRESHOLD: float = 0.85
    LOW_CONFIDENCE_THRESHOLD: float = 0.70

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/grievance.log"

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per application lifecycle."""
    return Settings()


settings = get_settings()
