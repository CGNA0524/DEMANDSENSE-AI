from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ScenarioSimulationRequest(BaseModel):
    name: Optional[str] = "Simulated Scenario"
    demand_multiplier: float = Field(default=1.0, ge=0.1, le=3.0) # e.g. 1.2 = +20% demand
    lead_time_change_days: int = Field(default=0, ge=-10, le=30) # e.g. +3 days delay
    service_level: float = Field(default=0.95, ge=0.5, le=0.999)
    budget: float = Field(default=50000.0, gt=0)
    inventory_shock_pct: float = Field(default=0.0, ge=-0.9, le=1.0) # e.g. -0.2 = -20% initial stock

class ScenarioMetricComparison(BaseModel):
    metric_name: str
    baseline_value: float
    simulated_value: float
    absolute_change: float
    percentage_change: float
    unit: str

class ScenarioItemComparison(BaseModel):
    product_id: str
    product_name: str
    category: str
    baseline_order_qty: float
    simulated_order_qty: float
    baseline_safety_stock: float
    simulated_safety_stock: float
    baseline_cost: float
    simulated_cost: float
    baseline_status: str
    simulated_status: str
    baseline_stockout_days: float
    simulated_stockout_days: float

class ScenarioSimulationResponse(BaseModel):
    scenario_name: str
    parameters: Dict[str, Any]
    metric_comparisons: List[ScenarioMetricComparison]
    product_comparisons: List[ScenarioItemComparison]
    executive_summary: str
