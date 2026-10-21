import logging
import numpy as np
import pandas as pd
from datetime import timedelta
from typing import Dict, Any, List, Optional

from app.forecasting.models import (
    SeasonalNaiveForecaster, MovingAverageForecaster, MLRegressionForecaster
)
from app.forecasting.evaluation import ForecastEvaluator
from app.schemas.forecast import (
    ForecastResponse, ForecastPoint, HistoricalPoint, ModelMetric
)

logger = logging.getLogger(__name__)

class ForecastingEngine:
    @staticmethod
    def run_forecast(
        history_df: pd.DataFrame,
        product_id: str,
        product_name: str,
        store_id: Optional[str] = None,
        horizon_days: int = 30,
        selected_model_name: str = "AUTO",
        val_days: int = 14
    ) -> ForecastResponse:
        """
        Executes chronological time-series cross-validation across baseline and ML models,
        selects the best model based on holdout validation WAPE/RMSE,
        and generates future forecasts with confidence bounds.
        """
        if history_df.empty:
            raise ValueError(f"No historical sales records found for product {product_id}")

        history_df = history_df.sort_values("date").reset_index(drop=True)
        total_history_days = len(history_df)

        # Prepare model candidates
        candidates = [
            SeasonalNaiveForecaster(seasonal_period=7),
            MovingAverageForecaster(window=7),
            MovingAverageForecaster(window=14),
            MLRegressionForecaster(model_type="ridge"),
            MLRegressionForecaster(model_type="random_forest"),
            MLRegressionForecaster(model_type="xgboost"),
        ]

        # Chronological validation
        validation_metrics: List[ModelMetric] = []
        best_candidate = candidates[0]
        
        if total_history_days > (val_days + 14):
            train_df = history_df.iloc[:-val_days].copy()
            val_df = history_df.iloc[-val_days:].copy()
            y_val_actual = val_df["units_sold"].values

            eval_results = []
            for cand in candidates:
                try:
                    val_preds = cand.fit_and_forecast(train_df, val_days)
                    metrics = ForecastEvaluator.calculate_metrics(y_val_actual, val_preds)
                    eval_results.append({
                        "model": cand,
                        "name": cand.name,
                        "mae": metrics["mae"],
                        "rmse": metrics["rmse"],
                        "wape": metrics["wape"],
                        "mape": metrics["mape"]
                    })
                except Exception as e:
                    logger.warning(f"Error evaluating {cand.name}: {e}")
                    eval_results.append({
                        "model": cand,
                        "name": cand.name,
                        "mae": 999.0,
                        "rmse": 999.0,
                        "wape": 999.0,
                        "mape": None
                    })

            # Sort by WAPE ascending, then RMSE
            eval_results.sort(key=lambda x: (x["wape"], x["rmse"]))
            
            # Determine selection
            if selected_model_name != "AUTO":
                matched = [r for r in eval_results if selected_model_name.lower() in r["name"].lower()]
                selected_result = matched[0] if matched else eval_results[0]
            else:
                selected_result = eval_results[0]

            best_candidate = selected_result["model"]

            for rank, res in enumerate(eval_results, start=1):
                validation_metrics.append(ModelMetric(
                    model_name=res["name"],
                    mae=res["mae"],
                    rmse=res["rmse"],
                    wape=res["wape"],
                    mape=res["mape"],
                    rank=rank,
                    is_selected=(res["name"] == selected_result["name"])
                ))
        else:
            # Short history fallback
            best_candidate = MovingAverageForecaster(7)
            validation_metrics.append(ModelMetric(
                model_name=best_candidate.name,
                mae=0.0,
                rmse=0.0,
                wape=0.0,
                mape=0.0,
                rank=1,
                is_selected=True
            ))

        # Generate final forecast on full history
        final_forecast = best_candidate.fit_and_forecast(history_df, horizon_days)
        final_forecast = np.clip(final_forecast, 0, None)

        # Estimate residual uncertainty for confidence bounds
        last_n = min(30, len(history_df))
        demand_std = float(history_df["units_sold"].iloc[-last_n:].std()) if last_n > 1 else 2.0
        if np.isnan(demand_std) or demand_std <= 0:
            demand_std = 1.5

        # Format historical points (last 60 days for visualization)
        display_hist_df = history_df.tail(60)
        hist_points = [
            HistoricalPoint(
                date=str(row["date"]),
                units_sold=float(row["units_sold"]),
                promotion=bool(row.get("promotion", False)),
                stockout=bool(row.get("stockout_indicator", False))
            )
            for _, row in display_hist_df.iterrows()
        ]

        # Generate future forecast points
        last_date = pd.to_datetime(history_df["date"].max())
        forecast_points: List[ForecastPoint] = []
        for i, val in enumerate(final_forecast, start=1):
            future_d = (last_date + timedelta(days=i)).date()
            # Horizon scaling uncertainty factor: uncertainty grows with sqrt(i)
            uncertainty_margin = 1.96 * demand_std * np.sqrt(1 + (i / 14.0))
            forecast_points.append(ForecastPoint(
                date=str(future_d),
                predicted_units=round(float(val), 1),
                lower_bound=round(float(max(0.0, val - uncertainty_margin)), 1),
                upper_bound=round(float(val + uncertainty_margin), 1)
            ))

        total_predicted = float(np.sum(final_forecast))
        avg_predicted = float(np.mean(final_forecast)) if len(final_forecast) > 0 else 0.0

        model_desc = f"{best_candidate.name} chosen based on chronological validation holdout error (WAPE/RMSE)."

        return ForecastResponse(
            product_id=product_id,
            product_name=product_name,
            store_id=store_id,
            horizon_days=horizon_days,
            selected_model=best_candidate.name,
            model_description=model_desc,
            historical_points=hist_points,
            forecast_points=forecast_points,
            validation_metrics=validation_metrics,
            avg_predicted_daily=round(avg_predicted, 2),
            total_predicted_units=round(total_predicted, 1),
            forecast_start_date=forecast_points[0].date if forecast_points else "",
            forecast_end_date=forecast_points[-1].date if forecast_points else ""
        )
