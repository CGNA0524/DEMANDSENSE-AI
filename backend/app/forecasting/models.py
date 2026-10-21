import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

from app.forecasting.feature_engineering import TimeSeriesFeatureEngineer

class BaseForecaster:
    def __init__(self, name: str):
        self.name = name

    def fit_and_forecast(self, history_df: pd.DataFrame, horizon_days: int) -> np.ndarray:
        raise NotImplementedError

class SeasonalNaiveForecaster(BaseForecaster):
    def __init__(self, seasonal_period: int = 7):
        super().__init__("Seasonal-Naive (7-Day)")
        self.seasonal_period = seasonal_period

    def fit_and_forecast(self, history_df: pd.DataFrame, horizon_days: int) -> np.ndarray:
        series = history_df["units_sold"].values
        if len(series) == 0:
            return np.zeros(horizon_days)
        
        # Take the last 'seasonal_period' days and tile them across horizon
        period_data = series[-self.seasonal_period:] if len(series) >= self.seasonal_period else series
        reps = int(np.ceil(horizon_days / len(period_data)))
        forecast = np.tile(period_data, reps)[:horizon_days]
        return np.clip(forecast, 0, None)

class MovingAverageForecaster(BaseForecaster):
    def __init__(self, window: int = 7):
        super().__init__(f"Moving Average ({window}-Day)")
        self.window = window

    def fit_and_forecast(self, history_df: pd.DataFrame, horizon_days: int) -> np.ndarray:
        series = history_df["units_sold"].values
        if len(series) == 0:
            return np.zeros(horizon_days)
        
        window_data = series[-self.window:] if len(series) >= self.window else series
        avg = float(np.mean(window_data))
        return np.full(horizon_days, avg)

class MLRegressionForecaster(BaseForecaster):
    def __init__(self, model_type: str = "ridge"):
        name_map = {
            "ridge": "Ridge Regression",
            "random_forest": "Random Forest Regressor",
            "xgboost": "XGBoost Regressor"
        }
        super().__init__(name_map.get(model_type, "ML Regressor"))
        self.model_type = model_type
        self.model = None

    def _init_estimator(self):
        if self.model_type == "ridge":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("regressor", Ridge(alpha=1.0))
            ])
        elif self.model_type == "random_forest":
            return RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42)
        elif self.model_type == "xgboost":
            if XGB_AVAILABLE:
                return xgb.XGBRegressor(n_estimators=60, max_depth=5, learning_rate=0.08, random_state=42, n_jobs=1)
            else:
                return GradientBoostingRegressor(n_estimators=60, max_depth=5, learning_rate=0.08, random_state=42)
        else:
            return Ridge(alpha=1.0)

    def fit_and_forecast(self, history_df: pd.DataFrame, horizon_days: int) -> np.ndarray:
        if len(history_df) < 14:
            # Fallback to seasonal-naive or moving average if insufficient data
            return MovingAverageForecaster(7).fit_and_forecast(history_df, horizon_days)

        feat_df = TimeSeriesFeatureEngineer.create_features(history_df)
        feature_cols = TimeSeriesFeatureEngineer.get_feature_columns()
        
        # Drop rows where lag features are NaN (first 28 days or min required)
        clean_df = feat_df.dropna(subset=feature_cols).copy()
        if len(clean_df) < 10:
            clean_df = feat_df.fillna(0.0)

        X = clean_df[feature_cols].values
        y = clean_df["units_sold"].values

        estimator = self._init_estimator()
        estimator.fit(X, y)
        self.model = estimator

        # Multi-step recursive forecasting
        working_df = history_df[["date", "units_sold", "promotion", "discount"]].copy()
        last_date = pd.to_datetime(working_df["date"].max())
        
        preds = []
        for step in range(1, horizon_days + 1):
            next_date = last_date + pd.Timedelta(days=step)
            
            # Predict step using latest working_df
            temp_df = pd.concat([
                working_df,
                pd.DataFrame([{
                    "date": next_date.date(),
                    "units_sold": 0.0,
                    "promotion": False,
                    "discount": 0.0
                }])
            ], ignore_index=True)

            temp_feat = TimeSeriesFeatureEngineer.create_features(temp_df)
            last_row_X = temp_feat[feature_cols].iloc[[-1]].fillna(0.0).values
            pred_val = float(max(0.0, estimator.predict(last_row_X)[0]))
            preds.append(pred_val)

            # Append prediction to working_df to feed subsequent recursive lags
            working_df = pd.concat([
                working_df,
                pd.DataFrame([{
                    "date": next_date.date(),
                    "units_sold": pred_val,
                    "promotion": False,
                    "discount": 0.0
                }])
            ], ignore_index=True)

        return np.array(preds)
