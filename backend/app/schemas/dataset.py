from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ColumnMapping(BaseModel):
    date: str = "date"
    product_id: str = "product_id"
    product_name: Optional[str] = "product_name"
    category: Optional[str] = "category"
    store_id: Optional[str] = "store_id"
    units_sold: str = "units_sold"
    unit_price: Optional[str] = "unit_price"
    unit_cost: Optional[str] = "unit_cost"
    inventory_on_hand: Optional[str] = "inventory_on_hand"
    supplier_lead_time_days: Optional[str] = "supplier_lead_time_days"
    promotion: Optional[str] = "promotion"
    discount: Optional[str] = "discount"
    stockout_indicator: Optional[str] = "stockout_indicator"

class DatasetPreviewResponse(BaseModel):
    filename: str
    detected_columns: List[str]
    suggested_mapping: Dict[str, Optional[str]]
    total_preview_rows: int
    preview_data: List[Dict[str, Any]]

class ValidationErrorItem(BaseModel):
    row: Optional[int] = None
    column: Optional[str] = None
    issue_type: str # ERROR, WARNING
    message: str

class ValidationSummary(BaseModel):
    is_valid: bool
    total_rows: int
    valid_rows: int
    error_count: int
    warning_count: int
    detected_products_count: int
    date_min: Optional[str] = None
    date_max: Optional[str] = None
    issues: List[ValidationErrorItem] = []

class ImportCommitRequest(BaseModel):
    filename: str
    mapping: ColumnMapping

class DatasetImportHistoryItem(BaseModel):
    id: int
    filename: str
    file_type: str
    row_count: int
    valid_row_count: int
    error_count: int
    warning_count: int
    is_demo: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProductSchema(BaseModel):
    product_id: str
    product_name: str
    category: str
    unit_price: float
    unit_cost: float
    supplier_lead_time_days: int
    min_order_quantity: int
    pack_size: int
    priority_level: str
    current_inventory: Optional[float] = 0.0

    class Config:
        from_attributes = True

class StoreSchema(BaseModel):
    store_id: str
    store_name: str
    location: Optional[str] = None

    class Config:
        from_attributes = True
