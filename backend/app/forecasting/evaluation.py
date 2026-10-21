import numpy as np
from typing import Dict, Any, Optional

class ForecastEvaluator:
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Optional[float]]:
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)
        
        # Ensure predictions are non-negative
        y_pred = np.clip(y_pred, 0, None)

        if len(y_true) == 0:
            return {"mae": 0.0, "rmse": 0.0, "wape": 0.0, "mape": None}

        # MAE
        mae = float(np.mean(np.abs(y_true - y_pred)))
        
        # RMSE
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
        
        # WAPE (Weighted Absolute Percentage Error = sum(|y - y_hat|) / sum(y))
        sum_actual = float(np.sum(y_true))
        if sum_actual > 0:
            wape = float(np.sum(np.abs(y_true - y_pred)) / sum_actual)
        else:
            wape = 0.0 if np.all(y_pred == 0) else 1.0

        # MAPE with safeguard for zero demand
        # Only evaluate MAPE on points where actual demand > 0
        non_zero_mask = y_true > 0
        if np.any(non_zero_mask):
            mape = float(np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100.0)
        else:
            mape = None

        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "wape": round(wape, 4),
            "mape": round(mape, 2) if mape is not None else None
        }
