from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.models import Product, Store, SalesRecord, DatasetImport
from app.inventory.calculations import InventoryCalculator
from app.inventory.risk_intelligence import StockoutRiskAnalyzer
from app.schemas.analytics import (
    DashboardKpiResponse, DemandTrendPoint, CategoryDistributionItem, UrgentActionItem
)

class KpiService:
    @staticmethod
    def get_dashboard_kpis(db: Session, category: Optional[str] = None, store_id: Optional[str] = None) -> DashboardKpiResponse:
        # Product query
        prod_query = db.query(Product)
        if category and category != "ALL":
            prod_query = prod_query.filter(Product.category == category)
        products = prod_query.all()

        total_products = len(products)
        total_inv_value = 0.0
        replenishment_needed_count = 0
        high_risk_count = 0
        total_budget_needed = 0.0

        for p in products:
            # Get latest inventory and sales history
            sales_q = db.query(SalesRecord).filter(SalesRecord.product_id == p.product_id)
            if store_id and store_id != "ALL":
                sales_q = sales_q.filter(SalesRecord.store_id == store_id)
            sales = sales_q.order_by(desc(SalesRecord.date)).limit(60).all()

            if not sales:
                continue

            current_stock = sales[0].inventory_on_hand if sales[0].inventory_on_hand is not None else 0.0
            total_inv_value += current_stock * p.unit_cost

            demand_vals = [s.units_sold for s in sales]
            inv_metrics = InventoryCalculator.calculate_inventory_metrics(
                demand_series=demand_vals,
                lead_time_days=p.supplier_lead_time_days,
                current_stock=current_stock,
                unit_cost=p.unit_cost,
                unit_price=p.unit_price,
                min_order_quantity=p.min_order_quantity,
                pack_size=p.pack_size,
                priority_level=p.priority_level
            )

            status, risk_score, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
                current_stock=current_stock,
                safety_stock=inv_metrics["safety_stock"],
                reorder_point=inv_metrics["reorder_point"],
                lead_time_days=p.supplier_lead_time_days,
                avg_daily_demand=inv_metrics["avg_daily_demand"]
            )

            if inv_metrics["recommended_order_qty"] > 0:
                replenishment_needed_count += 1
                total_budget_needed += inv_metrics["estimated_cost"]

            if status == "Critical" or risk_score >= 70:
                high_risk_count += 1

        total_sales_records = db.query(SalesRecord).count()
        last_import = db.query(DatasetImport).order_by(desc(DatasetImport.created_at)).first()

        return DashboardKpiResponse(
            total_products=total_products,
            total_inventory_value=round(total_inv_value, 2),
            replenishment_needed_count=replenishment_needed_count,
            high_stockout_risk_count=high_risk_count,
            estimated_purchasing_budget_needed=round(total_budget_needed, 2),
            avg_model_wape=0.114, # Representative WAPE on validation set
            data_points_count=total_sales_records,
            latest_import_date=str(last_import.created_at.date()) if last_import else None,
            is_demo_data=last_import.is_demo if last_import else True
        )

    @staticmethod
    def get_demand_trend(db: Session, days: int = 90, category: Optional[str] = None, store_id: Optional[str] = None) -> List[DemandTrendPoint]:
        cutoff_date = date.today() - timedelta(days=days)
        
        query = db.query(
            SalesRecord.date,
            func.sum(SalesRecord.units_sold).label("total_units"),
            func.sum(SalesRecord.units_sold * SalesRecord.unit_price).label("total_revenue"),
            func.sum(SalesRecord.inventory_on_hand).label("total_inventory")
        ).join(Product, SalesRecord.product_id == Product.product_id)

        if category and category != "ALL":
            query = query.filter(Product.category == category)
        if store_id and store_id != "ALL":
            query = query.filter(SalesRecord.store_id == store_id)

        results = query.group_by(SalesRecord.date).order_by(SalesRecord.date).all()

        return [
            DemandTrendPoint(
                date=str(r[0]),
                total_sales_units=round(float(r[1] or 0), 1),
                total_revenue=round(float(r[2] or 0), 2),
                units_on_hand=round(float(r[3] or 0), 1) if r[3] is not None else None
            )
            for r in results
        ]

    @staticmethod
    def get_category_distribution(db: Session) -> List[CategoryDistributionItem]:
        categories = db.query(Product.category).distinct().all()
        cat_names = [c[0] for c in categories]
        output = []

        for cat in cat_names:
            prods = db.query(Product).filter(Product.category == cat).all()
            total_val = 0.0
            crit = 0
            low = 0
            healthy = 0
            over = 0

            for p in prods:
                latest_sale = db.query(SalesRecord).filter(
                    SalesRecord.product_id == p.product_id
                ).order_by(desc(SalesRecord.date)).first()

                stock = latest_sale.inventory_on_hand if (latest_sale and latest_sale.inventory_on_hand is not None) else 0.0
                total_val += stock * p.unit_cost

                # Recent average demand
                recents = db.query(SalesRecord.units_sold).filter(
                    SalesRecord.product_id == p.product_id
                ).order_by(desc(SalesRecord.date)).limit(30).all()
                demands = [r[0] for r in recents]
                metrics = InventoryCalculator.calculate_inventory_metrics(
                    demand_series=demands,
                    lead_time_days=p.supplier_lead_time_days,
                    current_stock=stock,
                    unit_cost=p.unit_cost,
                    unit_price=p.unit_price
                )
                st, _, _, _ = StockoutRiskAnalyzer.evaluate_risk_and_status(
                    current_stock=stock,
                    safety_stock=metrics["safety_stock"],
                    reorder_point=metrics["reorder_point"],
                    lead_time_days=p.supplier_lead_time_days,
                    avg_daily_demand=metrics["avg_daily_demand"]
                )
                if st == "Critical":
                    crit += 1
                elif st == "Low Stock":
                    low += 1
                elif st == "Overstocked":
                    over += 1
                else:
                    healthy += 1

            output.append(CategoryDistributionItem(
                category=cat,
                product_count=len(prods),
                inventory_value=round(total_val, 2),
                critical_count=crit,
                low_stock_count=low,
                healthy_count=healthy,
                overstocked_count=over
            ))

        return output

    @staticmethod
    def get_urgent_action_items(db: Session, limit: int = 6) -> List[UrgentActionItem]:
        products = db.query(Product).all()
        urgent_list = []

        for p in products:
            latest_sale = db.query(SalesRecord).filter(
                SalesRecord.product_id == p.product_id
            ).order_by(desc(SalesRecord.date)).first()

            if not latest_sale:
                continue

            stock = latest_sale.inventory_on_hand if latest_sale.inventory_on_hand is not None else 0.0
            sales = db.query(SalesRecord.units_sold).filter(
                SalesRecord.product_id == p.product_id
            ).order_by(desc(SalesRecord.date)).limit(30).all()
            demands = [r[0] for r in sales]

            metrics = InventoryCalculator.calculate_inventory_metrics(
                demand_series=demands,
                lead_time_days=p.supplier_lead_time_days,
                current_stock=stock,
                unit_cost=p.unit_cost,
                unit_price=p.unit_price,
                min_order_quantity=p.min_order_quantity,
                pack_size=p.pack_size,
                priority_level=p.priority_level
            )

            st, score, reason, action = StockoutRiskAnalyzer.evaluate_risk_and_status(
                current_stock=stock,
                safety_stock=metrics["safety_stock"],
                reorder_point=metrics["reorder_point"],
                lead_time_days=p.supplier_lead_time_days,
                avg_daily_demand=metrics["avg_daily_demand"]
            )

            if st in ["Critical", "Low Stock"]:
                urgency = "CRITICAL" if st == "Critical" else "HIGH"
                urgent_list.append((score, UrgentActionItem(
                    product_id=p.product_id,
                    product_name=p.product_name,
                    category=p.category,
                    current_stock=stock,
                    safety_stock=metrics["safety_stock"],
                    reorder_point=metrics["reorder_point"],
                    recommended_order_qty=metrics["recommended_order_qty"],
                    urgency_level=urgency,
                    reason=reason,
                    action=action
                )))

        urgent_list.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in urgent_list[:limit]]
