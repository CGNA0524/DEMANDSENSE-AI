from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Product, SalesRecord
from app.inventory.calculations import InventoryCalculator
from app.optimization.budget_optimizer import BudgetOptimizer
from app.schemas.optimization import BudgetOptimizationRequest, BudgetOptimizationResponse
from app.schemas.common import ApiResponse

router = APIRouter()

@router.post("/budget-optimizer", response_model=ApiResponse[BudgetOptimizationResponse])
def optimize_purchasing_budget(req: BudgetOptimizationRequest, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No products found in the database. Please import or load demo data first."
        )

    items_data = []
    for p in products:
        sales = db.query(SalesRecord).filter(
            SalesRecord.product_id == p.product_id
        ).order_by(desc(SalesRecord.date)).limit(60).all()

        if not sales:
            continue

        current_stock = sales[0].inventory_on_hand if sales[0].inventory_on_hand is not None else 0.0
        demands = [s.units_sold for s in sales]

        metrics = InventoryCalculator.calculate_inventory_metrics(
            demand_series=demands,
            lead_time_days=p.supplier_lead_time_days,
            current_stock=current_stock,
            unit_cost=p.unit_cost,
            unit_price=p.unit_price,
            service_level=req.service_level,
            min_order_quantity=p.min_order_quantity,
            pack_size=p.pack_size,
            priority_level=p.priority_level
        )

        items_data.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "category": p.category,
            "unit_cost": p.unit_cost,
            "current_stock": current_stock,
            "safety_stock": metrics["safety_stock"],
            "recommended_order_qty": metrics["recommended_order_qty"],
            "pack_size": p.pack_size,
            "min_order_quantity": p.min_order_quantity,
            "priority_level": p.priority_level,
            "avg_daily_demand": metrics["avg_daily_demand"]
        })

    result = BudgetOptimizer.optimize(
        items_data=items_data,
        budget=req.budget,
        custom_priorities=req.custom_priorities
    )

    return ApiResponse(
        success=True,
        message=f"Purchasing budget optimized: ${result.allocated_cost:,.2f} allocated ({result.budget_utilization_pct}% utilization).",
        data=result
    )
