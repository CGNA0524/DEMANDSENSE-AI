from typing import Dict, Any, Tuple

class StockoutRiskAnalyzer:
    @staticmethod
    def evaluate_risk_and_status(
        current_stock: float,
        safety_stock: float,
        reorder_point: float,
        lead_time_days: int,
        avg_daily_demand: float
    ) -> Tuple[str, float, str, str]:
        """
        Evaluates inventory health status, risk score (0-100), alert rationale, and recommended action.
        Returns:
            (status, risk_score, alert_reason, recommended_action)
        """
        days_coverage = current_stock / avg_daily_demand if avg_daily_demand > 0.001 else 999.0

        # Status determination
        if current_stock <= safety_stock or days_coverage <= lead_time_days:
            status = "Critical"
            # Risk score calculation
            deficit_ratio = max(0.0, (reorder_point - current_stock) / max(1.0, reorder_point))
            lead_time_exposure = max(0.0, (lead_time_days - days_coverage) / max(1, lead_time_days))
            risk_score = round(min(100.0, 75.0 + (lead_time_exposure * 20.0) + (deficit_ratio * 5.0)), 1)
            
            reason = (
                f"Immediate stockout risk: Available inventory ({current_stock:.0f} units, {days_coverage:.1f} days coverage) "
                f"is insufficient to cover supplier lead time ({lead_time_days} days) or is below safety threshold ({safety_stock:.0f} units)."
            )
            action = f"Issue expedited purchase order immediately to prevent stockout within {days_coverage:.0f} days."

        elif current_stock <= reorder_point:
            status = "Low Stock"
            ratio = (reorder_point - current_stock) / max(1.0, (reorder_point - safety_stock)) if reorder_point > safety_stock else 0.5
            risk_score = round(40.0 + min(34.0, ratio * 34.0), 1)
            
            reason = (
                f"Reorder threshold breached: Current inventory ({current_stock:.0f} units) has fallen below "
                f"reorder point ({reorder_point:.0f} units). Expected coverage is {days_coverage:.1f} days."
            )
            action = "Place standard replenishment order with supplier to restore target inventory levels."

        elif current_stock > (reorder_point + (avg_daily_demand * 45)):
            status = "Overstocked"
            risk_score = 5.0
            excess_units = current_stock - (reorder_point + (avg_daily_demand * 30))
            reason = (
                f"Excess inventory detected: {current_stock:.0f} units on hand represents {days_coverage:.1f} days of coverage "
                f"(exceeds 45-day operational threshold). Approximately {excess_units:.0f} excess units."
            )
            action = "Pause replenishment orders. Consider promotional discount or reallocating to high-demand channels."

        else:
            status = "Healthy"
            risk_score = round(max(5.0, min(25.0, 25.0 - (days_coverage / 2.0))), 1)
            reason = (
                f"Inventory is balanced: Stock level ({current_stock:.0f} units, {days_coverage:.1f} days coverage) "
                f"is safely above reorder threshold ({reorder_point:.0f} units)."
            )
            action = "No immediate replenishment required. Continue regular demand monitoring."

        return status, risk_score, reason, action
