from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Product, SalesRecord
from app.inventory.calculations import InventoryCalculator
from app.inventory.risk_intelligence import StockoutRiskAnalyzer
from app.schemas.inventory import (
    InventorySummaryResponse, InventoryItemRecommendation, StockoutRiskAlert
)
from app.schemas.common import ApiResponse

router = APIRouter()

def _compute_product_inventory(
    p: Product,
    db: Session,
    service_level: float = 0.95,
    store_id: Optional[str] = None
) -> Optional[InventoryItemRecommendation]:
    query = db.query(SalesRecord).filter(SalesRecord.product_id == p.product_id)
    if store_id and store_id != "ALL":
        query = query.filter(SalesRecord.store_id == store_id)
    
    sales = query.order_by(desc(SalesRecord.date)).limit(60).all()
    if not sales:
        return None

    current_stock = sales[0].inventory_on_hand if sales[0].inventory_on_hand is not None else 0.0
    demand_series = [s.units_sold for s in sales]

    metrics = InventoryCalculator.calculate_inventory_metrics(
        demand_series=demand_series,
        lead_time_days=p.supplier_lead_time_days,
        current_stock=current_stock,
        unit_cost=p.unit_cost,
        unit_price=p.unit_price,
        service_level=service_level,
        min_order_quantity=p.min_order_quantity,
        pack_size=p.pack_size,
        priority_level=p.priority_level
    )

    status_str, risk_score, reason, action = StockoutRiskAnalyzer.evaluate_risk_and_status(
        current_stock=current_stock,
        safety_stock=metrics["safety_stock"],
        reorder_point=metrics["reorder_point"],
        lead_time_days=p.supplier_lead_time_days,
        avg_daily_demand=metrics["avg_daily_demand"]
    )

    return InventoryItemRecommendation(
        product_id=p.product_id,
        product_name=p.product_name,
        category=p.category,
        store_id=store_id,
        current_stock=current_stock,
        avg_daily_demand=metrics["avg_daily_demand"],
        demand_std=metrics["demand_std"],
        supplier_lead_time_days=p.supplier_lead_time_days,
        service_level=metrics["service_level"],
        z_score=metrics["z_score"],
        safety_stock=metrics["safety_stock"],
        lead_time_demand=metrics["lead_time_demand"],
        reorder_point=metrics["reorder_point"],
        recommended_order_qty=metrics["recommended_order_qty"],
        unit_cost=p.unit_cost,
        unit_price=p.unit_price,
        estimated_cost=metrics["estimated_cost"],
        inventory_status=status_str,
        days_of_coverage=metrics["days_of_coverage"],
        min_order_quantity=p.min_order_quantity,
        pack_size=p.pack_size,
        priority_level=p.priority_level,
        risk_score=risk_score,
        risk_reason=reason,
        recommended_action=action
    )

@router.get("/summary", response_model=ApiResponse[InventorySummaryResponse])
def get_inventory_summary(
    service_level: float = Query(0.95, ge=0.5, le=0.999),
    category: Optional[str] = None,
    store_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category and category != "ALL":
        query = query.filter(Product.category == category)
    products = query.order_by(Product.product_name).all()

    items: List[InventoryItemRecommendation] = []
    total_units = 0.0
    total_value = 0.0
    replenishment_needed_skus = 0
    total_reorder_units = 0.0
    total_reorder_cost = 0.0
    status_counts = {"Critical": 0, "Low Stock": 0, "Healthy": 0, "Overstocked": 0}

    for p in products:
        item = _compute_product_inventory(p, db, service_level, store_id)
        if item:
            items.append(item)
            total_units += item.current_stock
            total_value += item.current_stock * item.unit_cost
            if item.recommended_order_qty > 0:
                replenishment_needed_skus += 1
                total_reorder_units += item.recommended_order_qty
                total_reorder_cost += item.estimated_cost
            status_counts[item.inventory_status] = status_counts.get(item.inventory_status, 0) + 1

    summary = InventorySummaryResponse(
        total_skus=len(items),
        total_inventory_units=round(total_units, 1),
        total_inventory_value=round(total_value, 2),
        replenishment_needed_skus=replenishment_needed_skus,
        total_recommended_order_units=round(total_reorder_units, 1),
        total_estimated_reorder_cost=round(total_reorder_cost, 2),
        status_breakdown=status_counts,
        items=items
    )
    return ApiResponse(success=True, message="Inventory summary computed.", data=summary)

@router.get("/item/{product_id}", response_model=ApiResponse[InventoryItemRecommendation])
def get_single_inventory_item(
    product_id: str,
    service_level: float = Query(0.95, ge=0.5, le=0.999),
    db: Session = Depends(get_db)
):
    p = db.query(Product).filter(Product.product_id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    
    item = _compute_product_inventory(p, db, service_level)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient inventory history.")
    
    return ApiResponse(success=True, message="Product inventory recommendation computed.", data=item)

@router.get("/stockout-risk", response_model=ApiResponse[List[StockoutRiskAlert]])
def get_stockout_risk_intelligence(
    category: Optional[str] = None,
    risk_level: Optional[str] = None, # Critical, High, Moderate, Low
    store_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category and category != "ALL":
        query = query.filter(Product.category == category)
    products = query.all()

    alerts: List[StockoutRiskAlert] = []
    for p in products:
        item = _compute_product_inventory(p, db, 0.95, store_id)
        if not item:
            continue

        if item.risk_score >= 75:
            classification = "Critical"
        elif item.risk_score >= 50:
            classification = "High"
        elif item.risk_score >= 25:
            classification = "Moderate"
        else:
            classification = "Low"

        if risk_level and risk_level != "ALL" and classification.upper() != risk_level.upper():
            continue

        alerts.append(StockoutRiskAlert(
            product_id=item.product_id,
            product_name=item.product_name,
            category=item.category,
            current_inventory=item.current_stock,
            avg_daily_demand=item.avg_daily_demand,
            lead_time_days=item.supplier_lead_time_days,
            days_until_stockout=item.days_of_coverage,
            risk_classification=classification,
            risk_score=item.risk_score,
            alert_reason=item.risk_reason,
            recommended_action=item.recommended_action
        ))

    alerts.sort(key=lambda a: a.risk_score, reverse=True)
    return ApiResponse(success=True, message="Stockout risk alerts generated.", data=alerts)
