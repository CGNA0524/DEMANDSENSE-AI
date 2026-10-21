import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DemandSense AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = BASE_DIR / "data" / "uploads"
    EXPORTS_DIR: Path = BASE_DIR / "data" / "exports"
    DEMO_DIR: Path = BASE_DIR / "data" / "demo"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'demandsense.db'}")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Default Business Assumptions
    DEFAULT_SERVICE_LEVEL: float = 0.95
    DEFAULT_FORECAST_HORIZON_DAYS: int = 30
    DEFAULT_BUDGET: float = 50000.0

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure directories exist
for d in [settings.DATA_DIR, settings.UPLOADS_DIR, settings.EXPORTS_DIR, settings.DEMO_DIR, settings.MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
