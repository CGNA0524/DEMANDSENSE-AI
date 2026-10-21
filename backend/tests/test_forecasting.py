import pytest
import numpy as np
import pandas as pd
from datetime import date, timedelta
from app.forecasting.feature_engineering import TimeSeriesFeatureEngineer
from app.forecasting.evaluation import ForecastEvaluator
from app.forecasting.models import (
    SeasonalNaiveForecaster, MovingAverageForecaster, MLRegressionForecaster
)
from app.forecasting.engine import ForecastingEngine

def test_feature_engineering_leakage_safeguard():
    dates = pd.date_range("2026-01-01", periods=35, freq="D").date
    units = np.arange(1, 36, dtype=float)
    df = pd.DataFrame({"date": dates, "units_sold": units})
    
    feat_df = TimeSeriesFeatureEngineer.create_features(df)
    
    # Lag 1 must equal the previous row's units_sold
    assert np.isnan(feat_df["lag_1"].iloc[0])
    assert feat_df["lag_1"].iloc[1] == df["units_sold"].iloc[0]
    assert feat_df["lag_1"].iloc[10] == df["units_sold"].iloc[9]
    
    # Rolling mean 7 on row i must only use rows before i
    assert np.isnan(feat_df["rolling_mean_7"].iloc[0])
    # The rolling mean at row 7 should be mean of rows 0..6, not including row 7
    expected_mean = df["units_sold"].iloc[0:7].mean()
    assert abs(feat_df["rolling_mean_7"].iloc[7] - expected_mean) < 1e-4

def test_evaluation_metrics():
    y_true = np.array([10.0, 20.0, 30.0, 0.0])
    y_pred = np.array([12.0, 18.0, 33.0, 2.0])
    
    metrics = ForecastEvaluator.calculate_metrics(y_true, y_pred)
    assert metrics["mae"] == 2.25
    assert metrics["rmse"] > 2.0
    assert metrics["wape"] > 0
    # Zero actual handled gracefully
    assert metrics["mape"] is not None

def test_forecasting_models_produce_valid_output():
    dates = pd.date_range("2026-01-01", periods=60, freq="D").date
    units = 20.0 + 5.0 * np.sin(np.arange(60)) + np.random.normal(0, 1, 60)
    df = pd.DataFrame({"date": dates, "units_sold": np.clip(units, 0, None), "promotion": False, "discount": 0.0})

    for model in [SeasonalNaiveForecaster(7), MovingAverageForecaster(7), MLRegressionForecaster("ridge"), MLRegressionForecaster("random_forest")]:
        preds = model.fit_and_forecast(df, horizon_days=14)
        assert len(preds) == 14
        assert (preds >= 0).all()

def test_forecasting_engine_chronological_selection():
    dates = pd.date_range("2026-01-01", periods=90, freq="D").date
    units = 30.0 + 8.0 * np.cos(np.arange(90)) + np.random.normal(0, 2, 90)
    df = pd.DataFrame({"date": dates, "units_sold": np.clip(units, 0, None), "promotion": False, "discount": 0.0})

    res = ForecastingEngine.run_forecast(
        history_df=df,
        product_id="TEST-001",
        product_name="Test Widget",
        horizon_days=30
    )
    assert len(res.forecast_points) == 30
    assert len(res.validation_metrics) > 0
    assert any(m.is_selected for m in res.validation_metrics)
    assert res.avg_predicted_daily > 0
