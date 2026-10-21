from fastapi import APIRouter
from app.api.endpoints import (
    health, datasets, products, forecasting, inventory, optimization, scenarios, analytics, reports
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(products.router, prefix="/catalog", tags=["Catalog"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["Forecasting"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory Planner"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["Budget Optimizer"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["What-If Simulator"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & KPIs"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Exports"])
