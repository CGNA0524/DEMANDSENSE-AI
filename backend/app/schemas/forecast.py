from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ForecastRequest(BaseModel):
    product_id: str
    store_id: Optional[str] = None
    horizon_days: int = Field(default=30, ge=7, le=90)
    selected_model: Optional[str] = "AUTO" # AUTO, SeasonalNaive, MovingAverage, RidgeRegression, RandomForest, XGBoost

class ForecastPoint(BaseModel):
    date: str
    predicted_units: float
    lower_bound: float
    upper_bound: float

class HistoricalPoint(BaseModel):
    date: str
    units_sold: float
    promotion: bool = False
    stockout: bool = False

class ModelMetric(BaseModel):
    model_name: str
    mae: float
    rmse: float
    wape: float
    mape: Optional[float] = None
    rank: int
    is_selected: bool

class ForecastResponse(BaseModel):
    product_id: str
    product_name: str
    store_id: Optional[str] = None
    horizon_days: int
    selected_model: str
    model_description: str
    historical_points: List[HistoricalPoint]
    forecast_points: List[ForecastPoint]
    validation_metrics: List[ModelMetric]
    avg_predicted_daily: float
    total_predicted_units: float
    forecast_start_date: str
    forecast_end_date: str
