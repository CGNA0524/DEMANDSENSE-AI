import re
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.db.models import Product, Store, SalesRecord, DatasetImport
from app.schemas.dataset import (
    ColumnMapping, DatasetPreviewResponse, ValidationSummary,
    ValidationErrorItem, DatasetImportHistoryItem
)

logger = logging.getLogger(__name__)

CANONICAL_FIELDS = {
    "date": ["date", "sale_date", "transaction_date", "day", "timestamp", "datetime"],
    "product_id": ["product_id", "sku", "item_id", "product_code", "product_number", "id"],
    "product_name": ["product_name", "item_name", "item_title", "itemtitle", "title", "product_description", "name"],
    "category": ["category", "dept", "department", "product_category", "group"],
    "store_id": ["store_id", "store", "location_id", "branch_id", "shop_id"],
    "units_sold": ["units_sold", "quantity", "qty", "sales", "units", "volume", "amount_sold", "qty_sold", "quantity_sold"],
    "unit_price": ["unit_price", "price", "retail_price", "selling_price", "sale_price", "retailprice"],
    "unit_cost": ["unit_cost", "cost", "wholesale_cost", "purchase_cost", "cogs"],
    "inventory_on_hand": ["inventory_on_hand", "stock", "inventory", "stock_on_hand", "on_hand_qty", "current_stock", "on_hand", "onhand"],
    "supplier_lead_time_days": ["supplier_lead_time_days", "lead_time_days", "lead_time", "leadtime", "supplier_lead_time"],
    "promotion": ["promotion", "promo", "is_promotion", "on_promotion", "promo_active"],
    "discount": ["discount", "discount_rate", "discount_pct", "discount_percentage"],
    "stockout_indicator": ["stockout_indicator", "stockout", "out_of_stock", "is_stockout"]
}

def guess_column_mapping(df_columns: List[str]) -> Dict[str, Optional[str]]:
    mapping: Dict[str, Optional[str]] = {}
    normalized_cols = {re.sub(r'[^a-z0-9]', '', c.lower()): c for c in df_columns}
    
    for canon_field, aliases in CANONICAL_FIELDS.items():
        found = None
        for alias in aliases:
            norm_alias = re.sub(r'[^a-z0-9]', '', alias.lower())
            if norm_alias in normalized_cols:
                found = normalized_cols[norm_alias]
                break
        mapping[canon_field] = found
    return mapping

class DatasetService:
    @staticmethod
    def read_dataframe(file_path: Path) -> pd.DataFrame:
        suffix = file_path.suffix.lower()
        if suffix in [".csv", ".txt"]:
            return pd.read_csv(file_path)
        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    @staticmethod
    def preview_dataset(file_path: Path) -> DatasetPreviewResponse:
        df = DatasetService.read_dataframe(file_path)
        preview_rows = df.head(10).replace({np.nan: None}).to_dict(orient="records")
        suggested = guess_column_mapping(df.columns.tolist())
        return DatasetPreviewResponse(
            filename=file_path.name,
            detected_columns=df.columns.tolist(),
            suggested_mapping=suggested,
            total_preview_rows=len(df),
            preview_data=preview_rows
        )

    @staticmethod
    def validate_and_prepare(df: pd.DataFrame, mapping: ColumnMapping) -> Tuple[pd.DataFrame, ValidationSummary]:
        issues: List[ValidationErrorItem] = []
        total_rows = len(df)
        
        # Check mandatory columns
        for req_field, mapped_name in [("date", mapping.date), ("product_id", mapping.product_id), ("units_sold", mapping.units_sold)]:
            if not mapped_name or mapped_name not in df.columns:
                issues.append(ValidationErrorItem(
                    issue_type="ERROR",
                    message=f"Mandatory column '{req_field}' is not mapped to any column in the dataset."
                ))
        
        if any(i.issue_type == "ERROR" for i in issues):
            return pd.DataFrame(), ValidationSummary(
                is_valid=False,
                total_rows=total_rows,
                valid_rows=0,
                error_count=len(issues),
                warning_count=0,
                detected_products_count=0,
                issues=issues
            )

        # Standardize mapped dataframe
        std_df = pd.DataFrame()
        
        # Date parsing
        try:
            std_df["date"] = pd.to_datetime(df[mapping.date], errors="coerce").dt.date
            null_dates = std_df["date"].isna().sum()
            if null_dates > 0:
                issues.append(ValidationErrorItem(
                    column=mapping.date,
                    issue_type="ERROR",
                    message=f"{null_dates} rows have invalid or unparseable dates."
                ))
        except Exception as e:
            issues.append(ValidationErrorItem(
                column=mapping.date,
                issue_type="ERROR",
                message=f"Failed to parse dates: {str(e)}"
            ))

        # Product ID
        std_df["product_id"] = df[mapping.product_id].astype(str).str.strip()
        empty_pids = (std_df["product_id"] == "") | (std_df["product_id"].isna()) | (std_df["product_id"] == "nan")
        if empty_pids.sum() > 0:
            issues.append(ValidationErrorItem(
                column=mapping.product_id,
                issue_type="ERROR",
                message=f"{empty_pids.sum()} rows have missing or empty product IDs."
            ))

        # Units Sold
        std_df["units_sold"] = pd.to_numeric(df[mapping.units_sold], errors="coerce")
        null_units = std_df["units_sold"].isna().sum()
        if null_units > 0:
            issues.append(ValidationErrorItem(
                column=mapping.units_sold,
                issue_type="WARNING",
                message=f"{null_units} rows have missing units sold (treated as 0.0)."
            ))
            std_df["units_sold"] = std_df["units_sold"].fillna(0.0)
            
        neg_units = (std_df["units_sold"] < 0).sum()
        if neg_units > 0:
            issues.append(ValidationErrorItem(
                column=mapping.units_sold,
                issue_type="WARNING",
                message=f"{neg_units} rows have negative units sold (clipped to 0.0)."
            ))
            std_df["units_sold"] = std_df["units_sold"].clip(lower=0.0)

        # Product Name
        if mapping.product_name and mapping.product_name in df.columns:
            std_df["product_name"] = df[mapping.product_name].fillna(std_df["product_id"]).astype(str)
        else:
            std_df["product_name"] = std_df["product_id"]

        # Category
        if mapping.category and mapping.category in df.columns:
            std_df["category"] = df[mapping.category].fillna("General").astype(str)
        else:
            std_df["category"] = "General"

        # Store ID
        if mapping.store_id and mapping.store_id in df.columns:
            std_df["store_id"] = df[mapping.store_id].fillna("DEFAULT").astype(str)
        else:
            std_df["store_id"] = "DEFAULT"

        # Unit Price
        if mapping.unit_price and mapping.unit_price in df.columns:
            std_df["unit_price"] = pd.to_numeric(df[mapping.unit_price], errors="coerce").fillna(10.0)
        else:
            std_df["unit_price"] = 10.0

        # Unit Cost
        if mapping.unit_cost and mapping.unit_cost in df.columns:
            std_df["unit_cost"] = pd.to_numeric(df[mapping.unit_cost], errors="coerce").fillna(std_df["unit_price"] * 0.6)
        else:
            std_df["unit_cost"] = std_df["unit_price"] * 0.6

        # Inventory on hand
        if mapping.inventory_on_hand and mapping.inventory_on_hand in df.columns:
            std_df["inventory_on_hand"] = pd.to_numeric(df[mapping.inventory_on_hand], errors="coerce")
        else:
            std_df["inventory_on_hand"] = np.nan

        # Supplier lead time days
        if mapping.supplier_lead_time_days and mapping.supplier_lead_time_days in df.columns:
            std_df["supplier_lead_time_days"] = pd.to_numeric(df[mapping.supplier_lead_time_days], errors="coerce").fillna(7).astype(int)
        else:
            std_df["supplier_lead_time_days"] = 7

        # Promotion
        if mapping.promotion and mapping.promotion in df.columns:
            std_df["promotion"] = df[mapping.promotion].apply(lambda x: True if str(x).lower() in ["1", "true", "yes", "y"] else False)
        else:
            std_df["promotion"] = False

        # Discount
        if mapping.discount and mapping.discount in df.columns:
            std_df["discount"] = pd.to_numeric(df[mapping.discount], errors="coerce").fillna(0.0)
        else:
            std_df["discount"] = 0.0

        # Stockout indicator
        if mapping.stockout_indicator and mapping.stockout_indicator in df.columns:
            std_df["stockout_indicator"] = df[mapping.stockout_indicator].apply(lambda x: True if str(x).lower() in ["1", "true", "yes", "y"] else False)
        else:
            std_df["stockout_indicator"] = False

        # Drop invalid date rows
        valid_mask = ~std_df["date"].isna() & ~empty_pids
        std_df = std_df[valid_mask].copy()

        # Check duplicates
        dup_mask = std_df.duplicated(subset=["date", "product_id", "store_id"], keep="last")
        dup_count = dup_mask.sum()
        if dup_count > 0:
            issues.append(ValidationErrorItem(
                issue_type="WARNING",
                message=f"{dup_count} duplicate records found for the same date/product/store. Only the latest record was preserved."
            ))
            std_df = std_df[~dup_mask].copy()

        valid_rows = len(std_df)
        detected_pids = std_df["product_id"].nunique()
        date_min_str = str(std_df["date"].min()) if valid_rows > 0 else None
        date_max_str = str(std_df["date"].max()) if valid_rows > 0 else None

        summary = ValidationSummary(
            is_valid=valid_rows > 0 and not any(i.issue_type == "ERROR" for i in issues),
            total_rows=total_rows,
            valid_rows=valid_rows,
            error_count=sum(1 for i in issues if i.issue_type == "ERROR"),
            warning_count=sum(1 for i in issues if i.issue_type == "WARNING"),
            detected_products_count=detected_pids,
            date_min=date_min_str,
            date_max=date_max_str,
            issues=issues
        )
        return std_df, summary

    @staticmethod
    def save_to_database(db: Session, df: pd.DataFrame, filename: str, file_type: str, is_demo: bool, summary: ValidationSummary) -> DatasetImport:
        import_record = DatasetImport(
            filename=filename,
            file_type=file_type,
            row_count=summary.total_rows,
            valid_row_count=summary.valid_rows,
            error_count=summary.error_count,
            warning_count=summary.warning_count,
            is_demo=is_demo,
            status="SUCCESS" if summary.is_valid else "PARTIAL",
            summary_json=json.dumps(summary.model_dump(), default=str)
        )
        db.add(import_record)
        db.flush()

        # Update or Insert Products
        prod_meta = df.groupby("product_id").agg({
            "product_name": "first",
            "category": "first",
            "unit_price": "median",
            "unit_cost": "median",
            "supplier_lead_time_days": "median"
        }).reset_index()

        existing_pids = {p.product_id: p for p in db.query(Product).all()}
        
        for _, row in prod_meta.iterrows():
            pid = str(row["product_id"])
            pname = str(row["product_name"])
            pcat = str(row["category"])
            price = float(row["unit_price"]) if not np.isnan(row["unit_price"]) else 15.0
            cost = float(row["unit_cost"]) if not np.isnan(row["unit_cost"]) else price * 0.6
            lead = int(row["supplier_lead_time_days"]) if not np.isnan(row["supplier_lead_time_days"]) else 7
            
            if pid in existing_pids:
                p = existing_pids[pid]
                p.product_name = pname
                p.category = pcat
                p.unit_price = price
                p.unit_cost = cost
                p.supplier_lead_time_days = lead
            else:
                new_p = Product(
                    product_id=pid,
                    product_name=pname,
                    category=pcat,
                    unit_price=price,
                    unit_cost=cost,
                    supplier_lead_time_days=lead,
                    min_order_quantity=5,
                    pack_size=10,
                    priority_level="HIGH" if cost * price > 500 else "MEDIUM"
                )
                db.add(new_p)
                existing_pids[pid] = new_p

        # Update or Insert Stores
        store_ids = df["store_id"].unique()
        existing_stores = {s.store_id: s for s in db.query(Store).all()}
        for sid in store_ids:
            sid_str = str(sid)
            if sid_str not in existing_stores:
                new_store = Store(
                    store_id=sid_str,
                    store_name=f"Store {sid_str}" if sid_str != "DEFAULT" else "Primary Flagship Store",
                    location="Main Distribution Center"
                )
                db.add(new_store)
                existing_stores[sid_str] = new_store

        db.flush()

        # Deduplication strategy: delete any existing sales records for the exact same (date, product_id, store_id)
        # to prevent double counting on re-imports
        records_to_add = []
        for _, r in df.iterrows():
            records_to_add.append(SalesRecord(
                date=r["date"],
                product_id=str(r["product_id"]),
                store_id=str(r["store_id"]),
                units_sold=float(r["units_sold"]),
                unit_price=float(r["unit_price"]),
                unit_cost=float(r["unit_cost"]),
                inventory_on_hand=float(r["inventory_on_hand"]) if pd.notna(r["inventory_on_hand"]) else None,
                promotion=bool(r["promotion"]),
                discount=float(r["discount"]),
                stockout_indicator=bool(r["stockout_indicator"]),
                import_id=import_record.id
            ))

        db.bulk_save_objects(records_to_add)
        db.commit()
        return import_record

    @staticmethod
    def generate_synthetic_demo_dataset() -> pd.DataFrame:
        """
        Generates realistic synthetic retail data:
        15 products, 4 categories, 180 days (6 months) with:
        - Day-of-week seasonality (higher weekend demand)
        - Category growth trends
        - Periodic marketing promotions (+40-80% lift)
        - Stockout events where inventory reached zero
        - Clearly deterministic with fixed seed
        """
        np.random.seed(42)
        end_date = date.today()
        start_date = end_date - timedelta(days=180)
        dates = pd.date_range(start=start_date, end=end_date, freq="D").date

        products_spec = [
            {"id": "PROD-EL-001", "name": "Ultra Wireless Noise-Cancelling Headphones", "cat": "Electronics", "base_price": 199.99, "base_cost": 110.0, "mean_demand": 18, "std": 5, "lead_time": 10, "pack": 5, "moq": 10, "prio": "HIGH"},
            {"id": "PROD-EL-002", "name": "Smart Fitness Tracker Band V4", "cat": "Electronics", "base_price": 79.99, "base_cost": 38.0, "mean_demand": 32, "std": 8, "lead_time": 14, "pack": 10, "moq": 20, "prio": "HIGH"},
            {"id": "PROD-EL-003", "name": "4K Ultra-HD Streaming Media Player", "cat": "Electronics", "base_price": 49.99, "base_cost": 24.5, "mean_demand": 25, "std": 6, "lead_time": 7, "pack": 10, "moq": 15, "prio": "MEDIUM"},
            {"id": "PROD-EL-004", "name": "Ergonomic Mechanical Keyboard RGB", "cat": "Electronics", "base_price": 129.50, "base_cost": 65.0, "mean_demand": 14, "std": 4, "lead_time": 12, "pack": 5, "moq": 10, "prio": "MEDIUM"},
            
            {"id": "PROD-AP-101", "name": "Classic Organic Cotton Crewneck T-Shirt", "cat": "Apparel", "base_price": 24.00, "base_cost": 8.50, "mean_demand": 55, "std": 12, "lead_time": 6, "pack": 25, "moq": 50, "prio": "HIGH"},
            {"id": "PROD-AP-102", "name": "Slim Fit Stretch Denim Jeans", "cat": "Apparel", "base_price": 68.00, "base_cost": 29.00, "mean_demand": 28, "std": 7, "lead_time": 15, "pack": 10, "moq": 20, "prio": "HIGH"},
            {"id": "PROD-AP-103", "name": "All-Weather Performance Windbreaker", "cat": "Apparel", "base_price": 95.00, "base_cost": 42.00, "mean_demand": 16, "std": 5, "lead_time": 18, "pack": 5, "moq": 15, "prio": "MEDIUM"},
            {"id": "PROD-AP-104", "name": "Breathable Athletic Running Socks (3-Pack)", "cat": "Apparel", "base_price": 16.50, "base_cost": 4.80, "mean_demand": 62, "std": 15, "lead_time": 5, "pack": 30, "moq": 60, "prio": "LOW"},
            
            {"id": "PROD-GR-201", "name": "Artisan Cold-Brew Arabica Coffee Beans (1kg)", "cat": "Grocery", "base_price": 28.50, "base_cost": 13.00, "mean_demand": 45, "std": 10, "lead_time": 4, "pack": 12, "moq": 24, "prio": "HIGH"},
            {"id": "PROD-GR-202", "name": "Organic Pure Raw Honey (500g)", "cat": "Grocery", "base_price": 14.99, "base_cost": 6.80, "mean_demand": 38, "std": 8, "lead_time": 7, "pack": 12, "moq": 24, "prio": "MEDIUM"},
            {"id": "PROD-GR-203", "name": "Cold-Pressed Extra Virgin Olive Oil (1L)", "cat": "Grocery", "base_price": 22.00, "base_cost": 11.20, "mean_demand": 30, "std": 7, "lead_time": 6, "pack": 6, "moq": 18, "prio": "MEDIUM"},
            {"id": "PROD-GR-204", "name": "Gluten-Free Rolled Oats (1.2kg)", "cat": "Grocery", "base_price": 9.50, "base_cost": 3.90, "mean_demand": 50, "std": 11, "lead_time": 5, "pack": 15, "moq": 30, "prio": "LOW"},
            
            {"id": "PROD-HG-301", "name": "Stainless Steel Thermal Water Bottle (750ml)", "cat": "Home Goods", "base_price": 34.00, "base_cost": 14.50, "mean_demand": 24, "std": 6, "lead_time": 9, "pack": 10, "moq": 20, "prio": "MEDIUM"},
            {"id": "PROD-HG-302", "name": "Bamboo Fiber Anti-Bacterial Bed Sheet Set", "cat": "Home Goods", "base_price": 85.00, "base_cost": 36.00, "mean_demand": 12, "std": 4, "lead_time": 14, "pack": 5, "moq": 10, "prio": "MEDIUM"},
            {"id": "PROD-HG-303", "name": "Aromatherapy Ultrasonic Essential Oil Diffuser", "cat": "Home Goods", "base_price": 42.00, "base_cost": 17.50, "mean_demand": 20, "std": 5, "lead_time": 8, "pack": 8, "moq": 16, "prio": "LOW"}
        ]

        stores = ["STORE-01", "STORE-02"]
        rows = []

        for p in products_spec:
            # Current inventory tracking simulation
            current_inv = p["mean_demand"] * (p["lead_time"] + 5)
            
            for d in dates:
                day_of_week = d.weekday() # 0 = Monday, 6 = Sunday
                weekend_boost = 1.35 if day_of_week in [4, 5, 6] else 0.95
                
                # Bi-weekly promotional events
                is_promo = (d.day % 14 == 0) or (d.day == 28)
                promo_boost = 1.6 if is_promo else 1.0
                discount = 0.20 if is_promo else 0.0

                # Slight positive monthly trend
                trend = 1.0 + (d - dates[0]).days * 0.0008

                for s in stores:
                    store_mult = 1.1 if s == "STORE-01" else 0.9
                    
                    # Base simulated demand with Poisson/Gaussian noise
                    expected = p["mean_demand"] * weekend_boost * promo_boost * trend * store_mult
                    actual_demand = max(0.0, np.random.normal(expected, p["std"]))
                    
                    # Periodic stockout simulation: 1 or 2 products hit stockout near recent weeks
                    is_stockout = False
                    if p["id"] in ["PROD-EL-001", "PROD-AP-101"] and (d - dates[0]).days in range(160, 166):
                        current_inv = 0.0
                        is_stockout = True
                        actual_sold = 0.0
                    else:
                        actual_sold = round(actual_demand, 1)
                        current_inv = max(0.0, current_inv - actual_sold)
                        # Supplier restock arrival periodically
                        if current_inv < p["mean_demand"] * 3:
                            current_inv += p["mean_demand"] * p["lead_time"] * 1.5

                    rows.append({
                        "date": d,
                        "product_id": p["id"],
                        "product_name": p["name"],
                        "category": p["cat"],
                        "store_id": s,
                        "units_sold": actual_sold,
                        "unit_price": p["base_price"],
                        "unit_cost": p["base_cost"],
                        "inventory_on_hand": round(current_inv, 1),
                        "supplier_lead_time_days": p["lead_time"],
                        "promotion": is_promo,
                        "discount": discount,
                        "stockout_indicator": is_stockout
                    })

        return pd.DataFrame(rows)

    @staticmethod
    def load_demo_data_if_empty(db: Session) -> bool:
        record_count = db.query(SalesRecord).count()
        if record_count == 0:
            logger.info("Database is empty. Generating and loading synthetic demo dataset...")
            df = DatasetService.generate_synthetic_demo_dataset()
            summary = ValidationSummary(
                is_valid=True,
                total_rows=len(df),
                valid_rows=len(df),
                error_count=0,
                warning_count=0,
                detected_products_count=df["product_id"].nunique(),
                date_min=str(df["date"].min()),
                date_max=str(df["date"].max()),
                issues=[]
            )
            DatasetService.save_to_database(
                db=db,
                df=df,
                filename="synthetic_retail_demo_dataset.csv",
                file_type="synthetic",
                is_demo=True,
                summary=summary
            )
            return True
        return False
