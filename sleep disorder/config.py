import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "academic-sleep-disorder-xai-2026-secret")
    db_file = os.path.join(BASE_DIR, "sleep_health.db").replace("\\", "/")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini AI configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = "gemini-2.5-flash"  # Free-tier fast multimodal/text model in new SDK
    
    # Paths
    DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
    PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
    FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, "feature_names.pkl")
    METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
