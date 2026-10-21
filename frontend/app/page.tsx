"use client";

import { useEffect, useState, useTransition } from "react";
import Link from "next/link";
import { 
  Package, 
  DollarSign, 
  AlertTriangle, 
  ShoppingCart, 
  TrendingUp, 
  CheckCircle,
  Calendar,
  Filter,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  Boxes
} from "lucide-react";
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  BarChart, 
  Bar, 
  Cell, 
  Legend 
} from "recharts";

import { apiClient } from "@/lib/api";
import { DashboardKPIs, DemandTrendPoint, CategoryDistributionItem, UrgentActionItem } from "@/types";
import { KpiCard } from "@/components/KpiCard";
import { DemoBanner } from "@/components/DemoBanner";
import { StatusBadge } from "@/components/StatusBadge";

export default function DashboardOverviewPage() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<DemandTrendPoint[]>([]);
  const [categoriesDist, setCategoriesDist] = useState<CategoryDistributionItem[]>([]);
  const [urgentActions, setUrgentActions] = useState<UrgentActionItem[]>([]);
  
  const [categoryList, setCategoryList] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedStore, setSelectedStore] = useState<string>("ALL");
  const [trendDays, setTrendDays] = useState<number>(90);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [kpisData, trendData, distData, urgentData, cats] = await Promise.all([
        apiClient.getKPIs(selectedCategory, selectedStore),
        apiClient.getDemandTrend(trendDays, selectedCategory, selectedStore),
        apiClient.getCategoryDistribution(),
        apiClient.getUrgentActions(6),
        apiClient.getCategories()
      ]);
      setKpis(kpisData);
      setTrends(trendData);
      setCategoriesDist(distData);
      setUrgentActions(urgentData);
      setCategoryList(cats);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCategory, selectedStore, trendDays]);

  return (
    <div className="space-y-6">
      {/* Top Demo Banner */}
      <DemoBanner onDataReloaded={loadData} />

      {/* Header and Filters */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Executive Inventory &amp; Demand Overview</h1>
          <p className="text-xs text-slate-500 mt-0.5">Real-time aggregate telemetry across historical sales, safety stock, and predictive risk</p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent font-medium text-slate-700 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Categories</option>
              {categoryList.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
            <Boxes className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              className="bg-transparent font-medium text-slate-700 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Stores</option>
              <option value="STORE-01">Store 01 (Flagship)</option>
              <option value="STORE-02">Store 02 (Regional)</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={trendDays}
              onChange={(e) => setTrendDays(Number(e.target.value))}
              className="bg-transparent font-medium text-slate-700 focus:outline-none cursor-pointer"
            >
              <option value={30}>Last 30 Days</option>
              <option value={60}>Last 60 Days</option>
              <option value={90}>Last 90 Days</option>
              <option value={180}>Last 180 Days</option>
            </select>
          </div>

          <button
            onClick={loadData}
            title="Refresh"
            className="p-2 text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Catalog SKUs"
          value={kpis?.total_products ?? "—"}
          subtitle={`${kpis?.data_points_count.toLocaleString() ?? 0} transaction records`}
          icon={Package}
          badge={{ text: "Active", variant: "info" }}
        />
        <KpiCard
          title="Total Inventory Value"
          value={kpis ? `$${kpis.total_inventory_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "—"}
          subtitle="Valued at standard wholesale unit cost"
          icon={DollarSign}
          badge={{ text: "On Hand", variant: "neutral" }}
        />
        <KpiCard
          title="Replenishment Reqd"
          value={kpis?.replenishment_needed_count ?? "—"}
          subtitle={`Est. budget: $${(kpis?.estimated_purchasing_budget_needed ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          icon={ShoppingCart}
          badge={{ 
            text: (kpis?.replenishment_needed_count ?? 0) > 0 ? "Action Reqd" : "Healthy", 
            variant: (kpis?.replenishment_needed_count ?? 0) > 0 ? "warning" : "success" 
          }}
        />
        <KpiCard
          title="Critical Stockout Risk"
          value={kpis?.high_stockout_risk_count ?? "—"}
          subtitle="SKUs below safety buffer or lead time"
          icon={AlertTriangle}
          badge={{ 
            text: (kpis?.high_stockout_risk_count ?? 0) > 0 ? "Urgent" : "None", 
            variant: (kpis?.high_stockout_risk_count ?? 0) > 0 ? "danger" : "success" 
          }}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Demand Trend Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Historical Demand &amp; Revenue Trend</h2>
              <p className="text-xs text-slate-500">Aggregate daily units sold and gross merchandise volume</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span className="w-2.5 h-2.5 rounded-sm bg-blue-600"></span> Units Sold
              </span>
              <span className="flex items-center gap-1.5 text-slate-600">
                <span className="w-2.5 h-2.5 rounded-sm bg-teal-500"></span> Revenue ($)
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorUnits" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 11, fill: "#64748b" }}
                    tickFormatter={(val) => val.slice(5)} 
                  />
                  <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "12px" }}
                    formatter={(val: any, name: any) => [name === "total_revenue" ? `$${Number(val).toLocaleString()}` : Number(val).toLocaleString(), name === "total_sales_units" ? "Units Sold" : "Revenue"]}
                  />
                  <Area type="monotone" dataKey="total_sales_units" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#colorUnits)" name="total_sales_units" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">Loading trend telemetry...</div>
            )}
          </div>
        </div>

        {/* Category Health Distribution */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Inventory Health Breakdown</h2>
            <p className="text-xs text-slate-500 mb-4">Product status distribution across categories</p>

            <div className="space-y-3">
              {categoriesDist.map((cat) => {
                const total = cat.critical_count + cat.low_stock_count + cat.healthy_count + cat.overstocked_count;
                const critPct = total > 0 ? (cat.critical_count / total) * 100 : 0;
                const lowPct = total > 0 ? (cat.low_stock_count / total) * 100 : 0;
                const healthyPct = total > 0 ? (cat.healthy_count / total) * 100 : 0;
                const overPct = total > 0 ? (cat.overstocked_count / total) * 100 : 0;

                return (
                  <div key={cat.category} className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="flex justify-between items-center text-xs mb-1.5">
                      <span className="font-semibold text-slate-800">{cat.category}</span>
                      <span className="text-slate-500 font-medium">${cat.inventory_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                    </div>

                    {/* Stacked bar */}
                    <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden flex">
                      <div style={{ width: `${critPct}%` }} className="bg-rose-500" title={`Critical: ${cat.critical_count}`} />
                      <div style={{ width: `${lowPct}%` }} className="bg-amber-500" title={`Low Stock: ${cat.low_stock_count}`} />
                      <div style={{ width: `${healthyPct}%` }} className="bg-emerald-500" title={`Healthy: ${cat.healthy_count}`} />
                      <div style={{ width: `${overPct}%` }} className="bg-indigo-500" title={`Overstocked: ${cat.overstocked_count}`} />
                    </div>

                    <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-medium">
                      <span className="text-rose-600 font-semibold">{cat.critical_count} Critical</span>
                      <span className="text-amber-600 font-semibold">{cat.low_stock_count} Low</span>
                      <span className="text-emerald-600">{cat.healthy_count} Healthy</span>
                      <span className="text-indigo-600">{cat.overstocked_count} Over</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Forecasting Benchmark</span>
            <span className="font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
              Avg WAPE: {(kpis?.avg_model_wape ? (kpis.avg_model_wape * 100).toFixed(1) : 11.4)}%
            </span>
          </div>
        </div>
      </div>

      {/* Urgent Action Items Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Urgent Replenishment &amp; Stockout Alerts</h2>
            <p className="text-xs text-slate-500">Priority products demanding immediate inventory replenishment action</p>
          </div>
          <Link
            href="/inventory"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            Open Inventory Planner <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Product</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Current Stock</th>
                <th className="px-4 py-3">Safety Buffer</th>
                <th className="px-4 py-3">Reorder Point</th>
                <th className="px-4 py-3">Recommended Order</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-5 py-3">Recommended Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {urgentActions.length > 0 ? (
                urgentActions.map((item) => (
                  <tr key={item.product_id} className="hover:bg-slate-50/80 transition">
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-slate-900">{item.product_name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{item.product_id}</div>
                    </td>
                    <td className="px-4 py-3.5">{item.category}</td>
                    <td className="px-4 py-3.5 font-semibold text-slate-900">{item.current_stock.toFixed(0)}</td>
                    <td className="px-4 py-3.5">{item.safety_stock.toFixed(0)}</td>
                    <td className="px-4 py-3.5">{item.reorder_point.toFixed(0)}</td>
                    <td className="px-4 py-3.5 font-bold text-blue-700">+{item.recommended_order_qty.toFixed(0)}</td>
                    <td className="px-4 py-3.5">
                      <StatusBadge status={item.urgency_level === "CRITICAL" ? "Critical" : "Low Stock"} />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-slate-700">{item.action}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-slate-400">
                    No critical inventory alerts detected. All stock levels are balanced.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
