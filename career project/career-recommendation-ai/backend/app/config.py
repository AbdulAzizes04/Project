import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Explainable AI Career Recommendation System"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "career-recommendation-super-secret-jwt-key-2026-annamacharya"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # MySQL Database Config
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "career_ai_db"

    # Connection Strings
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/career_ai_db"
    SQLITE_FALLBACK_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "career_ai.db"
    )

    # Hybrid Recommendation Engine Weights
    WEIGHT_SKILLS: float = 0.30
    WEIGHT_ACADEMICS: float = 0.15
    WEIGHT_PROJECTS: float = 0.15
    WEIGHT_CERTIFICATIONS: float = 0.10
    WEIGHT_APTITUDE: float = 0.10
    WEIGHT_INTEREST: float = 0.10
    WEIGHT_DOMAIN: float = 0.10

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
