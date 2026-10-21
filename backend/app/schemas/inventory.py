from typing import Optional, List
from pydantic import BaseModel, Field

class InventoryCalculationParams(BaseModel):
    service_level: float = Field(default=0.95, ge=0.5, le=0.999)
    lead_time_override_days: Optional[int] = None
    horizon_days: int = Field(default=30, ge=7, le=90)

class InventoryItemRecommendation(BaseModel):
    product_id: str
    product_name: str
    category: str
    store_id: Optional[str] = None
    current_stock: float
    avg_daily_demand: float
    demand_std: float
    supplier_lead_time_days: int
    service_level: float
    z_score: float
    safety_stock: float
    lead_time_demand: float
    reorder_point: float
    recommended_order_qty: float
    unit_cost: float
    unit_price: float
    estimated_cost: float
    inventory_status: str # Critical, Low Stock, Healthy, Overstocked
    days_of_coverage: float
    min_order_quantity: int
    pack_size: int
    priority_level: str
    risk_score: float
    risk_reason: str
    recommended_action: str

class InventorySummaryResponse(BaseModel):
    total_skus: int
    total_inventory_units: float
    total_inventory_value: float
    replenishment_needed_skus: int
    total_recommended_order_units: float
    total_estimated_reorder_cost: float
    status_breakdown: dict[str, int] # Critical, Low Stock, Healthy, Overstocked
    items: List[InventoryItemRecommendation]

class StockoutRiskAlert(BaseModel):
    product_id: str
    product_name: str
    category: str
    current_inventory: float
    avg_daily_demand: float
    lead_time_days: int
    days_until_stockout: float
    risk_classification: str # Critical, High, Moderate, Low
    risk_score: float # 0 - 100
    alert_reason: str
    recommended_action: str
