from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DashboardKpiResponse(BaseModel):
    total_products: int
    total_inventory_value: float
    replenishment_needed_count: int
    high_stockout_risk_count: int
    estimated_purchasing_budget_needed: float
    avg_model_wape: Optional[float] = None
    data_points_count: int
    latest_import_date: Optional[str] = None
    is_demo_data: bool

class DemandTrendPoint(BaseModel):
    date: str
    total_sales_units: float
    total_revenue: float
    units_on_hand: Optional[float] = None

class CategoryDistributionItem(BaseModel):
    category: str
    product_count: int
    inventory_value: float
    critical_count: int
    low_stock_count: int
    healthy_count: int
    overstocked_count: int

class UrgentActionItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    current_stock: float
    safety_stock: float
    reorder_point: float
    recommended_order_qty: float
    urgency_level: str # CRITICAL, HIGH, MODERATE
    reason: str
    action: str
