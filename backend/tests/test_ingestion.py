import pytest
import pandas as pd
from app.schemas.dataset import ColumnMapping
from app.services.dataset_service import DatasetService, guess_column_mapping

def test_column_mapping_fuzzy_matching():
    cols = ["SaleDate", "SKU", "Item_Title", "Qty_Sold", "RetailPrice", "OnHand"]
    mapping = guess_column_mapping(cols)
    assert mapping["date"] == "SaleDate"
    assert mapping["product_id"] == "SKU"
    assert mapping["product_name"] == "Item_Title"
    assert mapping["units_sold"] == "Qty_Sold"
    assert mapping["unit_price"] == "RetailPrice"
    assert mapping["inventory_on_hand"] == "OnHand"

def test_validate_and_prepare_valid():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "product_id": ["P1", "P1", "P1"],
        "units_sold": [10, 15, 20],
        "unit_price": [25.0, 25.0, 25.0]
    })
    mapping = ColumnMapping(date="date", product_id="product_id", units_sold="units_sold", unit_price="unit_price")
    std_df, summary = DatasetService.validate_and_prepare(df, mapping)
    assert summary.is_valid is True
    assert summary.valid_rows == 3
    assert summary.error_count == 0
    assert summary.detected_products_count == 1

def test_validate_and_prepare_missing_mandatory():
    df = pd.DataFrame({"product_id": ["P1"], "sales": [10]})
    mapping = ColumnMapping(date="date_missing", product_id="product_id", units_sold="sales")
    std_df, summary = DatasetService.validate_and_prepare(df, mapping)
    assert summary.is_valid is False
    assert summary.error_count > 0

def test_validate_and_prepare_negative_sales_and_duplicates():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01", "2026-01-02"],
        "product_id": ["P1", "P1", "P1"],
        "units_sold": [-5, 12, 10],
    })
    mapping = ColumnMapping(date="date", product_id="product_id", units_sold="units_sold")
    std_df, summary = DatasetService.validate_and_prepare(df, mapping)
    assert summary.warning_count >= 1
    # Negative sales clipped to >= 0
    assert (std_df["units_sold"] >= 0).all()
    # Duplicate on same date/product deduplicated
    assert len(std_df) == 2

def test_synthetic_demo_dataset_generation():
    df = DatasetService.generate_synthetic_demo_dataset()
    assert len(df) > 1000
    assert df["product_id"].nunique() >= 10
    assert "date" in df.columns
    assert "units_sold" in df.columns
    assert "inventory_on_hand" in df.columns
