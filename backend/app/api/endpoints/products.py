from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Product, Store, SalesRecord
from app.schemas.dataset import ProductSchema, StoreSchema
from app.schemas.common import ApiResponse

router = APIRouter()

@router.get("/products", response_model=ApiResponse[List[ProductSchema]])
def list_products(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Product)
    if category and category != "ALL":
        query = query.filter(Product.category == category)
    products = query.order_by(Product.product_name).all()

    items = []
    for p in products:
        latest_sale = db.query(SalesRecord.inventory_on_hand).filter(
            SalesRecord.product_id == p.product_id
        ).order_by(desc(SalesRecord.date)).first()

        current_inv = latest_sale[0] if (latest_sale and latest_sale[0] is not None) else 0.0

        items.append(ProductSchema(
            product_id=p.product_id,
            product_name=p.product_name,
            category=p.category,
            unit_price=p.unit_price,
            unit_cost=p.unit_cost,
            supplier_lead_time_days=p.supplier_lead_time_days,
            min_order_quantity=p.min_order_quantity,
            pack_size=p.pack_size,
            priority_level=p.priority_level,
            current_inventory=current_inv
        ))

    return ApiResponse(success=True, message="Products fetched successfully.", data=items)

@router.get("/categories", response_model=ApiResponse[List[str]])
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Product.category).distinct().order_by(Product.category).all()
    categories = [c[0] for c in cats if c[0]]
    return ApiResponse(success=True, message="Categories retrieved.", data=categories)

@router.get("/stores", response_model=ApiResponse[List[StoreSchema]])
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).order_by(Store.store_id).all()
    items = [
        StoreSchema(store_id=s.store_id, store_name=s.store_name, location=s.location)
        for s in stores
    ]
    return ApiResponse(success=True, message="Stores retrieved.", data=items)
