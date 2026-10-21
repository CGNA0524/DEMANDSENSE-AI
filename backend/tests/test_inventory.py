import pytest
import numpy as np
from app.inventory.calculations import InventoryCalculator
from app.inventory.risk_intelligence import StockoutRiskAnalyzer

def test_safety_stock_and_reorder_point_calculations():
    # Constant demand of 10 with std = 2, lead time = 4 days, service level 95% (Z ~ 1.645)
    demands = [8, 12, 10, 9, 11, 10, 10]
    lead_time = 4
    current_stock = 15.0
    
    metrics = InventoryCalculator.calculate_inventory_metrics(
        demand_series=demands,
        lead_time_days=lead_time,
        current_stock=current_stock,
        unit_cost=10.0,
        unit_price=20.0,
        service_level=0.95,
        min_order_quantity=5,
        pack_size=10
    )
    
    assert metrics["lead_time_demand"] == round(metrics["avg_daily_demand"] * lead_time, 1)
    # SS = Z * sigma * sqrt(4) = 1.645 * sigma * 2
    assert metrics["safety_stock"] > 0
    assert metrics["reorder_point"] == round(metrics["lead_time_demand"] + metrics["safety_stock"], 1)
    
    # Recommended order qty must be integer multiple of pack_size (10)
    assert metrics["recommended_order_qty"] % 10 == 0
    assert metrics["recommended_order_qty"] >= metrics["min_order_quantity"]
    assert metrics["recommended_order_qty"] >= 0

def test_inventory_status_and_risk_classifications():
    # Critical state: stock below safety stock
    status, score, reason, action = StockoutRiskAnalyzer.evaluate_risk_and_status(
        current_stock=5.0,
        safety_stock=20.0,
        reorder_point=60.0,
        lead_time_days=7,
        avg_daily_demand=10.0
    )
    assert status == "Critical"
    assert score >= 75.0
    assert "stockout" in reason.lower()

    # Low Stock state: stock between safety stock and ROP with coverage > lead time
    status, score, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
        current_stock=35.0,
        safety_stock=20.0,
        reorder_point=60.0,
        lead_time_days=3,
        avg_daily_demand=10.0
    )
    assert status == "Low Stock"
    assert 40.0 <= score < 75.0

    # Healthy state: stock above ROP
    status, score, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
        current_stock=80.0,
        safety_stock=20.0,
        reorder_point=60.0,
        lead_time_days=7,
        avg_daily_demand=10.0
    )
    assert status == "Healthy"
    assert score < 40.0

    # Overstocked state: stock exceeds ROP + 45 days demand
    status, score, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
        current_stock=600.0,
        safety_stock=20.0,
        reorder_point=60.0,
        lead_time_days=7,
        avg_daily_demand=10.0
    )
    assert status == "Overstocked"
