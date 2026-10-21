import json
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Product, SalesRecord, ForecastRun, ForecastDetail
from app.forecasting.engine import ForecastingEngine
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.schemas.common import ApiResponse

router = APIRouter()

@router.post("/forecast", response_model=ApiResponse[ForecastResponse])
def generate_forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == req.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{req.product_id}' not found."
        )

    # Fetch sales records
    query = db.query(SalesRecord).filter(SalesRecord.product_id == req.product_id)
    if req.store_id and req.store_id != "ALL":
        query = query.filter(SalesRecord.store_id == req.store_id)
    
    records = query.order_by(SalesRecord.date).all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No sales history exists for product '{req.product_id}'."
        )

    # Convert to DataFrame
    df_data = []
    for r in records:
        df_data.append({
            "date": r.date,
            "units_sold": r.units_sold,
            "promotion": r.promotion,
            "discount": r.discount,
            "stockout_indicator": r.stockout_indicator
        })
    history_df = pd.DataFrame(df_data)

    try:
        forecast_res = ForecastingEngine.run_forecast(
            history_df=history_df,
            product_id=product.product_id,
            product_name=product.product_name,
            store_id=req.store_id,
            horizon_days=req.horizon_days,
            selected_model_name=req.selected_model or "AUTO"
        )

        # Persist run to database
        best_metric = next((m for m in forecast_res.validation_metrics if m.is_selected), None)
        run_record = ForecastRun(
            product_id=product.product_id,
            store_id=req.store_id,
            horizon_days=req.horizon_days,
            model_name=forecast_res.selected_model,
            mae=best_metric.mae if best_metric else None,
            rmse=best_metric.rmse if best_metric else None,
            wape=best_metric.wape if best_metric else None,
            mape=best_metric.mape if best_metric else None,
            metrics_json=json.dumps([m.model_dump() for m in forecast_res.validation_metrics])
        )
        db.add(run_record)
        db.flush()

        detail_objs = [
            ForecastDetail(
                run_id=run_record.id,
                date=pd.to_datetime(fp.date).date(),
                predicted_units=fp.predicted_units,
                lower_bound=fp.lower_bound,
                upper_bound=fp.upper_bound
            )
            for fp in forecast_res.forecast_points
        ]
        db.bulk_save_objects(detail_objs)
        db.commit()

        return ApiResponse(
            success=True,
            message=f"Forecast generated using {forecast_res.selected_model} across {req.horizon_days} days horizon.",
            data=forecast_res
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Forecasting error: {str(e)}")
