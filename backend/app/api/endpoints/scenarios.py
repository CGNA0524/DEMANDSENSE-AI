import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Product, SalesRecord
from app.inventory.calculations import InventoryCalculator
from app.inventory.risk_intelligence import StockoutRiskAnalyzer
from app.optimization.budget_optimizer import BudgetOptimizer
from app.schemas.scenario import (
    ScenarioSimulationRequest, ScenarioSimulationResponse,
    ScenarioMetricComparison, ScenarioItemComparison
)
from app.schemas.common import ApiResponse

router = APIRouter()

@router.post("/simulate", response_model=ApiResponse[ScenarioSimulationResponse])
def simulate_scenario(req: ScenarioSimulationRequest, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    if not products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No products available to simulate.")

    baseline_total_cost = 0.0
    simulated_total_cost = 0.0
    baseline_critical_count = 0
    simulated_critical_count = 0
    baseline_total_units = 0.0
    simulated_total_units = 0.0
    baseline_total_safety_stock = 0.0
    simulated_total_safety_stock = 0.0

    product_comparisons = []

    for p in products:
        sales = db.query(SalesRecord).filter(
            SalesRecord.product_id == p.product_id
        ).order_by(desc(SalesRecord.date)).limit(60).all()

        if not sales:
            continue

        base_stock = sales[0].inventory_on_hand if sales[0].inventory_on_hand is not None else 0.0
        base_demand_vals = np.array([s.units_sold for s in sales], dtype=float)

        # Baseline Calculation
        base_metrics = InventoryCalculator.calculate_inventory_metrics(
            demand_series=base_demand_vals,
            lead_time_days=p.supplier_lead_time_days,
            current_stock=base_stock,
            unit_cost=p.unit_cost,
            unit_price=p.unit_price,
            service_level=0.95,
            min_order_quantity=p.min_order_quantity,
            pack_size=p.pack_size,
            priority_level=p.priority_level
        )
        base_status, _, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
            current_stock=base_stock,
            safety_stock=base_metrics["safety_stock"],
            reorder_point=base_metrics["reorder_point"],
            lead_time_days=p.supplier_lead_time_days,
            avg_daily_demand=base_metrics["avg_daily_demand"]
        )

        # Scenario Calculation
        # Demand shock: multiply historical demand
        sim_demand_vals = base_demand_vals * req.demand_multiplier
        # Lead time delta
        sim_lead_time = max(1, p.supplier_lead_time_days + req.lead_time_change_days)
        # Inventory shock
        sim_stock = max(0.0, base_stock * (1.0 + req.inventory_shock_pct))

        sim_metrics = InventoryCalculator.calculate_inventory_metrics(
            demand_series=sim_demand_vals,
            lead_time_days=sim_lead_time,
            current_stock=sim_stock,
            unit_cost=p.unit_cost,
            unit_price=p.unit_price,
            service_level=req.service_level,
            min_order_quantity=p.min_order_quantity,
            pack_size=p.pack_size,
            priority_level=p.priority_level
        )
        sim_status, _, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
            current_stock=sim_stock,
            safety_stock=sim_metrics["safety_stock"],
            reorder_point=sim_metrics["reorder_point"],
            lead_time_days=sim_lead_time,
            avg_daily_demand=sim_metrics["avg_daily_demand"]
        )

        # Accumulate totals
        baseline_total_cost += base_metrics["estimated_cost"]
        simulated_total_cost += sim_metrics["estimated_cost"]
        baseline_total_units += base_metrics["recommended_order_qty"]
        simulated_total_units += sim_metrics["recommended_order_qty"]
        baseline_total_safety_stock += base_metrics["safety_stock"]
        simulated_total_safety_stock += sim_metrics["safety_stock"]

        if base_status == "Critical":
            baseline_critical_count += 1
        if sim_status == "Critical":
            simulated_critical_count += 1

        product_comparisons.append(ScenarioItemComparison(
            product_id=p.product_id,
            product_name=p.product_name,
            category=p.category,
            baseline_order_qty=base_metrics["recommended_order_qty"],
            simulated_order_qty=sim_metrics["recommended_order_qty"],
            baseline_safety_stock=base_metrics["safety_stock"],
            simulated_safety_stock=sim_metrics["safety_stock"],
            baseline_cost=base_metrics["estimated_cost"],
            simulated_cost=sim_metrics["estimated_cost"],
            baseline_status=base_status,
            simulated_status=sim_status,
            baseline_stockout_days=base_metrics["days_of_coverage"],
            simulated_stockout_days=sim_metrics["days_of_coverage"]
        ))

    # Metric comparisons
    def diff_pct(b, s):
        return round(((s - b) / b * 100.0) if b != 0 else 0.0, 1)

    metric_comparisons = [
        ScenarioMetricComparison(
            metric_name="Estimated Replenishment Cost",
            baseline_value=round(baseline_total_cost, 2),
            simulated_value=round(simulated_total_cost, 2),
            absolute_change=round(simulated_total_cost - baseline_total_cost, 2),
            percentage_change=diff_pct(baseline_total_cost, simulated_total_cost),
            unit="$"
        ),
        ScenarioMetricComparison(
            metric_name="Total Recommended Reorder Units",
            baseline_value=round(baseline_total_units, 1),
            simulated_value=round(simulated_total_units, 1),
            absolute_change=round(simulated_total_units - baseline_total_units, 1),
            percentage_change=diff_pct(baseline_total_units, simulated_total_units),
            unit="units"
        ),
        ScenarioMetricComparison(
            metric_name="Critical Stockout Risk SKUs",
            baseline_value=float(baseline_critical_count),
            simulated_value=float(simulated_critical_count),
            absolute_change=float(simulated_critical_count - baseline_critical_count),
            percentage_change=diff_pct(baseline_critical_count, simulated_critical_count),
            unit="SKUs"
        ),
        ScenarioMetricComparison(
            metric_name="Total Safety Stock Buffer",
            baseline_value=round(baseline_total_safety_stock, 1),
            simulated_value=round(simulated_total_safety_stock, 1),
            absolute_change=round(simulated_total_safety_stock - baseline_total_safety_stock, 1),
            percentage_change=diff_pct(baseline_total_safety_stock, simulated_total_safety_stock),
            unit="units"
        ),
    ]

    summary_text = (
        f"Scenario simulation with demand factor {req.demand_multiplier}x, lead time delta {req.lead_time_change_days:+d}d, "
        f"and service level {req.service_level*100:.1f}%. "
        f"Replenishment capital requirement shifts by {diff_pct(baseline_total_cost, simulated_total_cost):+0.1f}%, "
        f"and critical risk SKUs change from {baseline_critical_count} to {simulated_critical_count}."
    )

    response_data = ScenarioSimulationResponse(
        scenario_name=req.name or "What-If Scenario",
        parameters={
            "demand_multiplier": req.demand_multiplier,
            "lead_time_change_days": req.lead_time_change_days,
            "service_level": req.service_level,
            "budget": req.budget,
            "inventory_shock_pct": req.inventory_shock_pct
        },
        metric_comparisons=metric_comparisons,
        product_comparisons=product_comparisons,
        executive_summary=summary_text
    )

    return ApiResponse(
        success=True,
        message="Scenario simulated successfully.",
        data=response_data
    )
