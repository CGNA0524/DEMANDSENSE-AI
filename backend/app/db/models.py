from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(64), unique=True, index=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), index=True, nullable=False)
    unit_price = Column(Float, default=0.0)
    unit_cost = Column(Float, default=0.0)
    supplier_lead_time_days = Column(Integer, default=7)
    min_order_quantity = Column(Integer, default=1)
    pack_size = Column(Integer, default=1)
    priority_level = Column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    sales_records = relationship("SalesRecord", back_populates="product", cascade="all, delete-orphan")
    forecast_runs = relationship("ForecastRun", back_populates="product", cascade="all, delete-orphan")

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(64), unique=True, index=True, nullable=False)
    store_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    sales_records = relationship("SalesRecord", back_populates="store", cascade="all, delete-orphan")

class DatasetImport(Base):
    __tablename__ = "dataset_imports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False) # csv, xlsx, synthetic
    row_count = Column(Integer, default=0)
    valid_row_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    is_demo = Column(Boolean, default=False)
    status = Column(String(50), default="SUCCESS") # SUCCESS, PARTIAL, FAILED
    summary_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    sales_records = relationship("SalesRecord", back_populates="dataset_import", cascade="all, delete-orphan")

class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    product_id = Column(String(64), ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    store_id = Column(String(64), ForeignKey("stores.store_id", ondelete="CASCADE"), index=True, nullable=True)
    units_sold = Column(Float, nullable=False, default=0.0)
    unit_price = Column(Float, nullable=False, default=0.0)
    unit_cost = Column(Float, nullable=False, default=0.0)
    inventory_on_hand = Column(Float, nullable=True)
    promotion = Column(Boolean, default=False)
    discount = Column(Float, default=0.0)
    stockout_indicator = Column(Boolean, default=False)
    import_id = Column(Integer, ForeignKey("dataset_imports.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    product = relationship("Product", back_populates="sales_records")
    store = relationship("Store", back_populates="sales_records")
    dataset_import = relationship("DatasetImport", back_populates="sales_records")

    __table_args__ = (
        Index("idx_sales_product_date", "product_id", "date"),
        Index("idx_sales_store_product_date", "store_id", "product_id", "date"),
    )

class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(64), ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    store_id = Column(String(64), nullable=True)
    horizon_days = Column(Integer, nullable=False)
    model_name = Column(String(100), nullable=False)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    wape = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    metrics_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    product = relationship("Product", back_populates="forecast_runs")
    details = relationship("ForecastDetail", back_populates="run", cascade="all, delete-orphan")

class ForecastDetail(Base):
    __tablename__ = "forecast_details"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("forecast_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    date = Column(Date, nullable=False)
    predicted_units = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)

    run = relationship("ForecastRun", back_populates="details")

class InventoryPlan(Base):
    __tablename__ = "inventory_plans"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(64), index=True, nullable=False)
    store_id = Column(String(64), nullable=True)
    current_stock = Column(Float, default=0.0)
    avg_daily_demand = Column(Float, default=0.0)
    demand_std = Column(Float, default=0.0)
    lead_time_demand = Column(Float, default=0.0)
    safety_stock = Column(Float, default=0.0)
    reorder_point = Column(Float, default=0.0)
    recommended_order_qty = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    inventory_status = Column(String(50), default="Healthy") # Critical, Low Stock, Healthy, Overstocked
    risk_score = Column(Float, default=0.0) # 0 to 100
    days_coverage = Column(Float, default=0.0)
    run_date = Column(DateTime, default=utc_now)

class ScenarioRun(Base):
    __tablename__ = "scenario_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    demand_multiplier = Column(Float, default=1.0)
    lead_time_change_days = Column(Integer, default=0)
    service_level = Column(Float, default=0.95)
    budget = Column(Float, default=50000.0)
    parameters_json = Column(Text, nullable=True)
    results_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
