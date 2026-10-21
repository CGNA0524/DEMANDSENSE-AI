import pytest
from app.optimization.budget_optimizer import BudgetOptimizer

def test_budget_optimizer_respects_budget():
    items = [
        {"product_id": "P1", "product_name": "Prod 1", "unit_cost": 50.0, "current_stock": 2.0, "safety_stock": 10.0, "recommended_order_qty": 40.0, "pack_size": 10, "min_order_quantity": 10, "priority_level": "HIGH", "avg_daily_demand": 5.0},
        {"product_id": "P2", "product_name": "Prod 2", "unit_cost": 100.0, "current_stock": 20.0, "safety_stock": 15.0, "recommended_order_qty": 30.0, "pack_size": 5, "min_order_quantity": 5, "priority_level": "MEDIUM", "avg_daily_demand": 3.0},
        {"product_id": "P3", "product_name": "Prod 3", "unit_cost": 200.0, "current_stock": 5.0, "safety_stock": 10.0, "recommended_order_qty": 20.0, "pack_size": 5, "min_order_quantity": 5, "priority_level": "LOW", "avg_daily_demand": 2.0},
    ]
    budget = 2500.0
    res = BudgetOptimizer.optimize(items, budget=budget)

    # Constraint 1: Allocated cost must never exceed budget
    assert res.allocated_cost <= budget
    assert res.remaining_budget >= 0

    # Constraint 2: Pack size multiple
    for item in res.items:
        if item.optimized_order_qty > 0:
            assert item.optimized_order_qty % item.pack_size == 0
            assert item.optimized_order_qty <= item.unconstrained_order_qty

def test_budget_optimizer_prioritizes_high():
    items = [
        {"product_id": "P_LOW", "product_name": "Low Prio", "unit_cost": 10.0, "current_stock": 10.0, "safety_stock": 5.0, "recommended_order_qty": 100.0, "pack_size": 10, "min_order_quantity": 10, "priority_level": "LOW", "avg_daily_demand": 5.0},
        {"product_id": "P_HIGH", "product_name": "High Prio", "unit_cost": 10.0, "current_stock": 1.0, "safety_stock": 15.0, "recommended_order_qty": 100.0, "pack_size": 10, "min_order_quantity": 10, "priority_level": "HIGH", "avg_daily_demand": 5.0},
    ]
    budget = 400.0 # Enough for 40 units total, but not both 100 units
    res = BudgetOptimizer.optimize(items, budget=budget)

    high_item = next(i for i in res.items if i.product_id == "P_HIGH")
    low_item = next(i for i in res.items if i.product_id == "P_LOW")
    
    # High priority item must get significantly more allocation
    assert high_item.optimized_order_qty > low_item.optimized_order_qty

def test_budget_optimizer_zero_budget():
    items = [
        {"product_id": "P1", "product_name": "Prod 1", "unit_cost": 20.0, "current_stock": 0.0, "safety_stock": 10.0, "recommended_order_qty": 50.0, "pack_size": 10, "min_order_quantity": 10, "priority_level": "HIGH", "avg_daily_demand": 5.0}
    ]
    res = BudgetOptimizer.optimize(items, budget=0.0)
    assert res.allocated_cost == 0.0
    assert res.items[0].optimized_order_qty == 0.0
