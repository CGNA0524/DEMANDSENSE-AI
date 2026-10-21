export interface Product {
  product_id: string;
  product_name: string;
  category: string;
  unit_price: number;
  unit_cost: number;
  supplier_lead_time_days: number;
  min_order_quantity: number;
  pack_size: number;
  priority_level: string;
  current_inventory: number;
}

export interface Store {
  store_id: string;
  store_name: string;
  location?: string;
}

export interface DashboardKPIs {
  total_products: number;
  total_inventory_value: number;
  replenishment_needed_count: number;
  high_stockout_risk_count: number;
  estimated_purchasing_budget_needed: number;
  avg_model_wape?: number;
  data_points_count: number;
  latest_import_date?: string;
  is_demo_data: boolean;
}

export interface DemandTrendPoint {
  date: string;
  total_sales_units: number;
  total_revenue: number;
  units_on_hand?: number;
}

export interface CategoryDistributionItem {
  category: string;
  product_count: number;
  inventory_value: number;
  critical_count: number;
  low_stock_count: number;
  healthy_count: number;
  overstocked_count: number;
}

export interface UrgentActionItem {
  product_id: string;
  product_name: string;
  category: string;
  current_stock: number;
  safety_stock: number;
  reorder_point: number;
  recommended_order_qty: number;
  urgency_level: "CRITICAL" | "HIGH" | "MODERATE";
  reason: string;
  action: string;
}

export interface HistoricalPoint {
  date: string;
  units_sold: number;
  promotion: boolean;
  stockout: boolean;
}

export interface ForecastPoint {
  date: string;
  predicted_units: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ModelMetric {
  model_name: string;
  mae: number;
  rmse: number;
  wape: number;
  mape?: number;
  rank: number;
  is_selected: boolean;
}

export interface ForecastResponse {
  product_id: string;
  product_name: string;
  store_id?: string;
  horizon_days: number;
  selected_model: string;
  model_description: string;
  historical_points: HistoricalPoint[];
  forecast_points: ForecastPoint[];
  validation_metrics: ModelMetric[];
  avg_predicted_daily: number;
  total_predicted_units: number;
  forecast_start_date: string;
  forecast_end_date: string;
}

export interface InventoryItemRecommendation {
  product_id: string;
  product_name: string;
  category: string;
  store_id?: string;
  current_stock: number;
  avg_daily_demand: number;
  demand_std: number;
  supplier_lead_time_days: number;
  service_level: number;
  z_score: number;
  safety_stock: number;
  lead_time_demand: number;
  reorder_point: number;
  recommended_order_qty: number;
  unit_cost: number;
  unit_price: number;
  estimated_cost: number;
  inventory_status: "Critical" | "Low Stock" | "Healthy" | "Overstocked" | string;
  days_of_coverage: number;
  min_order_quantity: number;
  pack_size: number;
  priority_level: string;
  risk_score: number;
  risk_reason: string;
  recommended_action: string;
}

export interface InventorySummaryResponse {
  total_skus: number;
  total_inventory_units: number;
  total_inventory_value: number;
  replenishment_needed_skus: number;
  total_recommended_order_units: number;
  total_estimated_reorder_cost: number;
  status_breakdown: Record<string, number>;
  items: InventoryItemRecommendation[];
}

export interface StockoutRiskAlert {
  product_id: string;
  product_name: string;
  category: string;
  current_inventory: number;
  avg_daily_demand: number;
  lead_time_days: number;
  days_until_stockout: number;
  risk_classification: string;
  risk_score: number;
  alert_reason: string;
  recommended_action: string;
}

export interface OptimizedOrderItem {
  product_id: string;
  product_name: string;
  category: string;
  priority_level: string;
  unit_cost: number;
  current_stock: number;
  safety_stock: number;
  unconstrained_order_qty: number;
  optimized_order_qty: number;
  pack_size: number;
  min_order_quantity: number;
  item_total_cost: number;
  unmet_units: number;
  replenishment_fulfillment_pct: number;
  expected_days_coverage: number;
  is_partially_fulfilled: boolean;
}

export interface BudgetOptimizationResponse {
  total_budget: number;
  allocated_cost: number;
  remaining_budget: number;
  budget_utilization_pct: number;
  total_unconstrained_cost: number;
  total_unconstrained_units: number;
  total_optimized_units: number;
  fully_replenished_skus_count: number;
  partially_replenished_skus_count: number;
  unreplenished_skus_count: number;
  optimization_method: string;
  items: OptimizedOrderItem[];
}

export interface ScenarioMetricComparison {
  metric_name: string;
  baseline_value: number;
  simulated_value: number;
  absolute_change: number;
  percentage_change: number;
  unit: string;
}

export interface ScenarioItemComparison {
  product_id: string;
  product_name: string;
  category: string;
  baseline_order_qty: number;
  simulated_order_qty: number;
  baseline_safety_stock: number;
  simulated_safety_stock: number;
  baseline_cost: number;
  simulated_cost: number;
  baseline_status: string;
  simulated_status: string;
  baseline_stockout_days: number;
  simulated_stockout_days: number;
}

export interface ScenarioSimulationResponse {
  scenario_name: string;
  parameters: Record<string, any>;
  metric_comparisons: ScenarioMetricComparison[];
  product_comparisons: ScenarioItemComparison[];
  executive_summary: string;
}

export interface DatasetImportHistoryItem {
  id: number;
  filename: string;
  file_type: string;
  row_count: number;
  valid_row_count: number;
  error_count: number;
  warning_count: number;
  is_demo: boolean;
  status: string;
  created_at: string;
}

export interface DatasetPreviewResponse {
  filename: string;
  detected_columns: string[];
  suggested_mapping: Record<string, string | null>;
  total_preview_rows: number;
  preview_data: Record<string, any>[];
}

export interface ValidationSummary {
  is_valid: boolean;
  total_rows: number;
  valid_rows: number;
  error_count: number;
  warning_count: number;
  detected_products_count: number;
  date_min?: string;
  date_max?: string;
  issues: {
    row?: number;
    column?: string;
    issue_type: string;
    message: string;
  }[];
}
