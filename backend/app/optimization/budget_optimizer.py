import math
from typing import List, Dict, Any, Optional
from app.schemas.optimization import (
    BudgetOptimizationResponse, OptimizedOrderItem
)

class BudgetOptimizer:
    @staticmethod
    def optimize(
        items_data: List[Dict[str, Any]],
        budget: float,
        custom_priorities: Optional[Dict[str, str]] = None
    ) -> BudgetOptimizationResponse:
        """
        Solves the budget-constrained multi-item inventory replenishment problem
        subject to pack sizes, MOQs, priority weights, and budget ceilings.
        Uses a priority-weighted bounded discrete knapsack allocation algorithm.
        """
        custom_priorities = custom_priorities or {}
        
        # Priority weight mapping
        priority_weights = {
            "HIGH": 4.0,
            "MEDIUM": 2.0,
            "LOW": 1.0
        }

        # Prepare items
        unconstrained_total_cost = 0.0
        unconstrained_total_units = 0.0

        prepared_items = []
        for raw in items_data:
            pid = raw["product_id"]
            pname = raw["product_name"]
            cat = raw.get("category", "General")
            unit_cost = max(0.01, float(raw.get("unit_cost", 10.0)))
            current_stock = float(raw.get("current_stock", 0.0))
            safety_stock = float(raw.get("safety_stock", 0.0))
            unconstrained_qty = max(0.0, float(raw.get("recommended_order_qty", 0.0)))
            pack_size = max(1, int(raw.get("pack_size", 1)))
            moq = max(1, int(raw.get("min_order_quantity", 1)))
            
            prio = custom_priorities.get(pid, raw.get("priority_level", "MEDIUM")).upper()
            if prio not in priority_weights:
                prio = "MEDIUM"

            # Determine urgency score boost if current stock is critically below safety stock
            urgency_boost = 3.0 if current_stock < safety_stock else 1.0
            score_per_dollar = (priority_weights[prio] * urgency_boost) / unit_cost

            unconstrained_total_units += unconstrained_qty
            unconstrained_total_cost += unconstrained_qty * unit_cost

            prepared_items.append({
                "product_id": pid,
                "product_name": pname,
                "category": cat,
                "priority_level": prio,
                "unit_cost": unit_cost,
                "current_stock": current_stock,
                "safety_stock": safety_stock,
                "unconstrained_qty": unconstrained_qty,
                "pack_size": pack_size,
                "moq": moq,
                "score_per_dollar": score_per_dollar,
                "allocated_qty": 0.0,
                "avg_daily_demand": float(raw.get("avg_daily_demand", 1.0))
            })

        # If total unconstrained cost fits in budget, fully satisfy all requests
        remaining_budget = float(budget)
        allocated_cost = 0.0

        # Sort by ROI (score per dollar) descending
        prepared_items.sort(key=lambda x: x["score_per_dollar"], reverse=True)

        # Pass 1: Try to allocate MOQ for Critical/High priority items if needed
        for item in prepared_items:
            if item["unconstrained_qty"] > 0 and (item["priority_level"] == "HIGH" or item["current_stock"] < item["safety_stock"]):
                initial_target = max(float(item["moq"]), float(item["pack_size"]))
                initial_target = min(initial_target, item["unconstrained_qty"])
                num_packs = math.ceil(initial_target / item["pack_size"])
                alloc_qty = float(num_packs * item["pack_size"])
                cost = alloc_qty * item["unit_cost"]

                if cost <= remaining_budget:
                    item["allocated_qty"] = alloc_qty
                    remaining_budget -= cost
                    allocated_cost += cost

        # Pass 2: Greedily allocate packs to items with remaining need in order of score_per_dollar
        progress = True
        while progress and remaining_budget > 0:
            progress = False
            for item in prepared_items:
                if item["allocated_qty"] < item["unconstrained_qty"]:
                    pack_cost = item["pack_size"] * item["unit_cost"]
                    if pack_cost <= remaining_budget:
                        # Add one pack
                        item["allocated_qty"] += item["pack_size"]
                        remaining_budget -= pack_cost
                        allocated_cost += pack_cost
                        progress = True
                        if remaining_budget < 0.01:
                            break

        # Build response items
        response_items: List[OptimizedOrderItem] = []
        fully_replenished = 0
        partially_replenished = 0
        unreplenished = 0
        total_optimized_units = 0.0

        for item in prepared_items:
            alloc = item["allocated_qty"]
            uncon = item["unconstrained_qty"]
            cost = alloc * item["unit_cost"]
            unmet = max(0.0, uncon - alloc)
            fulfillment_pct = round((alloc / uncon * 100.0) if uncon > 0 else 100.0, 1)

            total_stock_after = item["current_stock"] + alloc
            avg_demand = max(0.001, item["avg_daily_demand"])
            days_coverage = round(total_stock_after / avg_demand, 1)

            if uncon == 0:
                is_partial = False
            elif alloc >= uncon:
                fully_replenished += 1
                is_partial = False
            elif alloc > 0:
                partially_replenished += 1
                is_partial = True
            else:
                unreplenished += 1
                is_partial = False

            total_optimized_units += alloc

            response_items.append(OptimizedOrderItem(
                product_id=item["product_id"],
                product_name=item["product_name"],
                category=item["category"],
                priority_level=item["priority_level"],
                unit_cost=item["unit_cost"],
                current_stock=item["current_stock"],
                safety_stock=item["safety_stock"],
                unconstrained_order_qty=uncon,
                optimized_order_qty=alloc,
                pack_size=item["pack_size"],
                min_order_quantity=item["moq"],
                item_total_cost=round(cost, 2),
                unmet_units=round(unmet, 1),
                replenishment_fulfillment_pct=fulfillment_pct,
                expected_days_coverage=days_coverage,
                is_partially_fulfilled=is_partial
            ))

        utilization_pct = round((allocated_cost / budget * 100.0) if budget > 0 else 0.0, 2)

        return BudgetOptimizationResponse(
            total_budget=round(budget, 2),
            allocated_cost=round(allocated_cost, 2),
            remaining_budget=round(max(0.0, remaining_budget), 2),
            budget_utilization_pct=utilization_pct,
            total_unconstrained_cost=round(unconstrained_total_cost, 2),
            total_unconstrained_units=round(unconstrained_total_units, 1),
            total_optimized_units=round(total_optimized_units, 1),
            fully_replenished_skus_count=fully_replenished,
            partially_replenished_skus_count=partially_replenished,
            unreplenished_skus_count=unreplenished,
            optimization_method="Priority-Weighted Bounded Integer Knapsack Optimizer",
            items=response_items
        )
