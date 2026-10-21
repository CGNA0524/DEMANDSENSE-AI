import pandas as pd
import numpy as np
from typing import Tuple, List

class TimeSeriesFeatureEngineer:
    @staticmethod
    def create_features(df: pd.DataFrame, target_col: str = "units_sold") -> pd.DataFrame:
        """
        Creates time-series lag, rolling, and calendar features.
        CRITICAL: All rolling and lag features are strictly shifted to prevent future data leakage.
        """
        df = df.sort_values("date").copy()
        
        # Calendar features
        df["date_dt"] = pd.to_datetime(df["date"])
        df["day_of_week"] = df["date_dt"].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x in [5, 6] else 0)
        df["day_of_month"] = df["date_dt"].dt.day
        df["month"] = df["date_dt"].dt.month
        df["week_of_year"] = df["date_dt"].dt.isocalendar().week.astype(int)

        # Lags (shifted to ensure no lookahead)
        for lag in [1, 2, 7, 14, 21, 28]:
            df[f"lag_{lag}"] = df[target_col].shift(lag)

        # Rolling statistics (using shift(1) to avoid including current day in rolling statistics)
        shifted_target = df[target_col].shift(1)
        df["rolling_mean_7"] = shifted_target.rolling(window=7, min_periods=1).mean()
        df["rolling_mean_14"] = shifted_target.rolling(window=14, min_periods=1).mean()
        df["rolling_mean_28"] = shifted_target.rolling(window=28, min_periods=1).mean()
        df["rolling_std_7"] = shifted_target.rolling(window=7, min_periods=1).std().fillna(0.0)
        
        # Exogenous features
        if "promotion" in df.columns:
            df["promo_flag"] = df["promotion"].astype(int)
        else:
            df["promo_flag"] = 0

        if "discount" in df.columns:
            df["discount_val"] = df["discount"].fillna(0.0)
        else:
            df["discount_val"] = 0.0

        return df

    @staticmethod
    def get_feature_columns() -> List[str]:
        return [
            "day_of_week", "is_weekend", "day_of_month", "month", "week_of_year",
            "lag_1", "lag_2", "lag_7", "lag_14", "lag_21", "lag_28",
            "rolling_mean_7", "rolling_mean_14", "rolling_mean_28", "rolling_std_7",
            "promo_flag", "discount_val"
        ]
