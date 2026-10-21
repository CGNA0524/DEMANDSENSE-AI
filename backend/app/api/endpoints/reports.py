import io
import csv
import pandas as pd
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Product, SalesRecord
from app.forecasting.engine import ForecastingEngine
from app.inventory.calculations import InventoryCalculator
from app.inventory.risk_intelligence import StockoutRiskAnalyzer

router = APIRouter()

@router.get("/export/inventory-recommendations")
def export_inventory_recommendations(
    format: str = Query("csv", regex="^(csv|xlsx)$"),
    service_level: float = Query(0.95, ge=0.5, le=0.999),
    db: Session = Depends(get_db)
):
    products = db.query(Product).order_by(Product.product_name).all()
    rows = []

    for p in products:
        sales = db.query(SalesRecord).filter(
            SalesRecord.product_id == p.product_id
        ).order_by(desc(SalesRecord.date)).limit(60).all()

        if not sales:
            continue

        stock = sales[0].inventory_on_hand if sales[0].inventory_on_hand is not None else 0.0
        demands = [s.units_sold for s in sales]

        metrics = InventoryCalculator.calculate_inventory_metrics(
            demand_series=demands,
            lead_time_days=p.supplier_lead_time_days,
            current_stock=stock,
            unit_cost=p.unit_cost,
            unit_price=p.unit_price,
            service_level=service_level,
            min_order_quantity=p.min_order_quantity,
            pack_size=p.pack_size,
            priority_level=p.priority_level
        )

        status_str, risk_score, reason, action = StockoutRiskAnalyzer.evaluate_risk_and_status(
            current_stock=stock,
            safety_stock=metrics["safety_stock"],
            reorder_point=metrics["reorder_point"],
            lead_time_days=p.supplier_lead_time_days,
            avg_daily_demand=metrics["avg_daily_demand"]
        )

        rows.append({
            "Product ID": p.product_id,
            "Product Name": p.product_name,
            "Category": p.category,
            "Priority": p.priority_level,
            "Current Stock": stock,
            "Avg Daily Demand": metrics["avg_daily_demand"],
            "Lead Time (Days)": p.supplier_lead_time_days,
            "Safety Stock": metrics["safety_stock"],
            "Reorder Point": metrics["reorder_point"],
            "Recommended Order Qty": metrics["recommended_order_qty"],
            "Unit Cost ($)": p.unit_cost,
            "Estimated Cost ($)": metrics["estimated_cost"],
            "Days of Coverage": metrics["days_of_coverage"],
            "Status": status_str,
            "Risk Score": risk_score,
            "Action": action
        })

    df = pd.DataFrame(rows)

    if format == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Inventory Plan")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=demandsense_inventory_recommendations.xlsx"}
        )
    else:
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        return StreamingResponse(
            io.BytesIO(stream.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=demandsense_inventory_recommendations.csv"}
        )

@router.get("/export/forecast/{product_id}")
def export_forecast(
    product_id: str,
    horizon_days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    sales = db.query(SalesRecord).filter(
        SalesRecord.product_id == product_id
    ).order_by(SalesRecord.date).all()

    if not sales:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No sales history for product.")

    df_data = [{"date": s.date, "units_sold": s.units_sold, "promotion": s.promotion, "discount": s.discount, "stockout_indicator": s.stockout_indicator} for s in sales]
    history_df = pd.DataFrame(df_data)

    res = ForecastingEngine.run_forecast(
        history_df=history_df,
        product_id=product.product_id,
        product_name=product.product_name,
        horizon_days=horizon_days
    )

    rows = []
    for fp in res.forecast_points:
        rows.append({
            "Date": fp.date,
            "Product ID": res.product_id,
            "Product Name": res.product_name,
            "Model": res.selected_model,
            "Predicted Units": fp.predicted_units,
            "Lower Bound 95%": fp.lower_bound,
            "Upper Bound 95%": fp.upper_bound
        })

    df = pd.DataFrame(rows)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)
    return StreamingResponse(
        io.BytesIO(stream.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=demandsense_forecast_{product_id}.csv"}
    )
