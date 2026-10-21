from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.analytics.kpi_service import KpiService
from app.schemas.analytics import (
    DashboardKpiResponse, DemandTrendPoint, CategoryDistributionItem, UrgentActionItem
)
from app.schemas.common import ApiResponse

router = APIRouter()

@router.get("/dashboard-kpis", response_model=ApiResponse[DashboardKpiResponse])
def get_kpis(
    category: Optional[str] = None,
    store_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    kpis = KpiService.get_dashboard_kpis(db, category, store_id)
    return ApiResponse(success=True, message="KPIs retrieved successfully.", data=kpis)

@router.get("/demand-trend", response_model=ApiResponse[List[DemandTrendPoint]])
def get_trend(
    days: int = Query(90, ge=7, le=365),
    category: Optional[str] = None,
    store_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    trend = KpiService.get_demand_trend(db, days, category, store_id)
    return ApiResponse(success=True, message="Demand trend data retrieved.", data=trend)

@router.get("/category-distribution", response_model=ApiResponse[List[CategoryDistributionItem]])
def get_categories_distribution(db: Session = Depends(get_db)):
    dist = KpiService.get_category_distribution(db)
    return ApiResponse(success=True, message="Category distribution retrieved.", data=dist)

@router.get("/urgent-actions", response_model=ApiResponse[List[UrgentActionItem]])
def get_urgent_actions(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    items = KpiService.get_urgent_action_items(db, limit)
    return ApiResponse(success=True, message="Urgent action items retrieved.", data=items)
