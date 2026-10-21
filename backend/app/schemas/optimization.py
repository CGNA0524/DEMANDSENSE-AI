from typing import List, Optional
from pydantic import BaseModel, Field

class BudgetOptimizationRequest(BaseModel):
    budget: float = Field(..., gt=0)
    service_level: float = Field(default=0.95, ge=0.5, le=0.999)
    custom_priorities: Optional[dict[str, str]] = None # product_id -> 'HIGH'|'MEDIUM'|'LOW'

class OptimizedOrderItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    priority_level: str
    unit_cost: float
    current_stock: float
    safety_stock: float
    unconstrained_order_qty: float
    optimized_order_qty: float
    pack_size: int
    min_order_quantity: int
    item_total_cost: float
    unmet_units: float
    replenishment_fulfillment_pct: float
    expected_days_coverage: float
    is_partially_fulfilled: bool

class BudgetOptimizationResponse(BaseModel):
    total_budget: float
    allocated_cost: float
    remaining_budget: float
    budget_utilization_pct: float
    total_unconstrained_cost: float
    total_unconstrained_units: float
    total_optimized_units: float
    fully_replenished_skus_count: int
    partially_replenished_skus_count: int
    unreplenished_skus_count: int
    optimization_method: str # Priority-Weighted Bounded Integer Knapsack Optimizer
    items: List[OptimizedOrderItem]
