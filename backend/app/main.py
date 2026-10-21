import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.db import models
from app.api.router import api_router
from app.services.dataset_service import DatasetService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Create tables if not present
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Automatically load synthetic demo dataset if database is brand new/empty
    db = SessionLocal()
    try:
        loaded = DatasetService.load_demo_data_if_empty(db)
        if loaded:
            logger.info("Deterministic synthetic demo dataset populated successfully.")
        else:
            logger.info("Existing database verified. Ready to serve requests.")
    except Exception as e:
        logger.error(f"Error checking/loading demo data: {e}", exc_info=True)
    finally:
        db.close()

    yield
    # Shutdown logic
    logger.info("DemandSense AI backend shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="DemandSense AI — Demand Forecasting & Inventory Optimization Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"Internal server error: {str(exc)}"}
    )

# Mount API V1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
