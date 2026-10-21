import math
from typing import Dict, Any, Optional
import numpy as np
from scipy import stats

class InventoryCalculator:
    @staticmethod
    def calculate_z_score(service_level: float = 0.95) -> float:
        """Calculates normal distribution inverse CDF (z-score) for target service level."""
        service_level = max(0.50, min(0.999, service_level))
        return float(stats.norm.ppf(service_level))

    @staticmethod
    def calculate_inventory_metrics(
        demand_series: np.ndarray,
        lead_time_days: int,
        current_stock: float,
        unit_cost: float,
        unit_price: float,
        service_level: float = 0.95,
        min_order_quantity: int = 1,
        pack_size: int = 1,
        priority_level: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Computes formal inventory policy metrics:
        - Average daily demand (mu_d)
        - Demand standard deviation (sigma_d)
        - Expected lead-time demand (L * mu_d)
        - Safety stock (Z * sigma_d * sqrt(L))
        - Reorder Point (ROP = LTD + SS)
        - Recommended order quantity with MOQ and pack size rounding
        - Days of coverage
        """
        demand_series = np.asarray(demand_series, dtype=float)
        
        # 1. Average daily demand & variability
        if len(demand_series) > 0:
            avg_daily_demand = float(np.mean(demand_series))
            demand_std = float(np.std(demand_series, ddof=1)) if len(demand_series) > 1 else avg_daily_demand * 0.25
        else:
            avg_daily_demand = 0.0
            demand_std = 0.0

        if np.isnan(demand_std) or demand_std < 0:
            demand_std = 0.0

        lead_time_days = max(1, int(lead_time_days))
        z_score = InventoryCalculator.calculate_z_score(service_level)

        # 2. Lead-time demand & Safety Stock
        lead_time_demand = avg_daily_demand * lead_time_days
        # Safety Stock formula: Z * sigma_d * sqrt(L)
        safety_stock = z_score * demand_std * math.sqrt(lead_time_days)
        reorder_point = lead_time_demand + safety_stock

        # 3. Recommended order quantity
        net_requirement = max(0.0, reorder_point - current_stock)
        
        recommended_order_qty = 0.0
        if net_requirement > 0:
            # Baseline cycle stock replenishment to cover lead time + review period
            base_target = net_requirement + (avg_daily_demand * 7) # target 1 week cycle buffer
            
            # Apply Minimum Order Quantity (MOQ)
            order_before_pack = max(base_target, float(min_order_quantity))
            
            # Apply Pack Size constraint (round up to nearest integer multiple of pack_size)
            pack_size = max(1, int(pack_size))
            num_packs = math.ceil(order_before_pack / pack_size)
            recommended_order_qty = float(num_packs * pack_size)

        estimated_cost = recommended_order_qty * unit_cost

        # 4. Days of coverage
        if avg_daily_demand > 0.001:
            days_of_coverage = current_stock / avg_daily_demand
        else:
            days_of_coverage = 999.0 if current_stock > 0 else 0.0

        return {
            "avg_daily_demand": round(avg_daily_demand, 2),
            "demand_std": round(demand_std, 2),
            "supplier_lead_time_days": lead_time_days,
            "service_level": round(service_level, 3),
            "z_score": round(z_score, 2),
            "lead_time_demand": round(lead_time_demand, 1),
            "safety_stock": round(safety_stock, 1),
            "reorder_point": round(reorder_point, 1),
            "recommended_order_qty": round(recommended_order_qty, 1),
            "estimated_cost": round(estimated_cost, 2),
            "days_of_coverage": round(days_of_coverage, 1),
            "min_order_quantity": min_order_quantity,
            "pack_size": pack_size,
            "priority_level": priority_level
        }
