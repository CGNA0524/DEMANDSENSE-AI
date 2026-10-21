"use client";

import { useState, useEffect } from "react";
import { 
  AlertTriangle, 
  ShieldAlert, 
  Clock, 
  Filter, 
  ArrowUpRight, 
  CheckCircle,
  AlertOctagon,
  Boxes,
  RefreshCw
} from "lucide-react";

import { apiClient } from "@/lib/api";
import { StockoutRiskAlert } from "@/types";

export default function StockoutRiskPage() {
  const [alerts, setAlerts] = useState<StockoutRiskAlert[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>("ALL");
  const [selectedStore, setSelectedStore] = useState<string>("ALL");
  const [loading, setLoading] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const [res, cats] = await Promise.all([
        apiClient.getStockoutRisk(selectedCategory, selectedRiskLevel, selectedStore),
        apiClient.getCategories()
      ]);
      setAlerts(res);
      setCategories(cats);
    } catch (err) {
      console.error("Failed to fetch stockout risk:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [selectedCategory, selectedRiskLevel, selectedStore]);

  const criticalCount = alerts.filter(a => a.risk_classification === "Critical").length;
  const highCount = alerts.filter(a => a.risk_classification === "High").length;
  const moderateCount = alerts.filter(a => a.risk_classification === "Moderate").length;

  return (
    <div className="space-y-6">
      {/* Header and Filter bar */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-rose-600" />
              Stockout Risk &amp; Early-Warning Center
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Identifies inventory exposure, run-out times before supplier arrival, and explainable replenishment guidance
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Risk filter */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <span className="font-semibold text-slate-500">Risk Level:</span>
              <select
                value={selectedRiskLevel}
                onChange={(e) => setSelectedRiskLevel(e.target.value)}
                className="bg-transparent font-medium text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Risk Levels</option>
                <option value="CRITICAL">Critical Only</option>
                <option value="HIGH">High Only</option>
                <option value="MODERATE">Moderate Only</option>
                <option value="LOW">Low Only</option>
              </select>
            </div>

            {/* Category filter */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <span className="font-semibold text-slate-500">Category:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-transparent font-medium text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Categories</option>
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <button
              onClick={fetchAlerts}
              className="p-2 text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Risk Metrics Summary Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-rose-200 shadow-2xs flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-rose-700">Critical Stockout Exposure</span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-rose-900">{criticalCount}</span>
              <span className="text-xs text-rose-600 font-medium">SKUs run out &lt; lead time</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-100 flex items-center justify-center text-rose-600">
            <AlertOctagon className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-amber-200 shadow-2xs flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-amber-700">Elevated / High Risk</span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-amber-900">{highCount}</span>
              <span className="text-xs text-amber-600 font-medium">SKUs below reorder point</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">Moderate / Monitored</span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900">{moderateCount}</span>
              <span className="text-xs text-slate-500 font-medium">Stable coverage window</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600">
            <Clock className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {alerts.length > 0 ? (
          alerts.map((alert) => {
            const isCrit = alert.risk_classification === "Critical";
            const isHigh = alert.risk_classification === "High";

            return (
              <div
                key={alert.product_id}
                className={`bg-white p-5 rounded-xl border transition shadow-2xs ${
                  isCrit
                    ? "border-rose-300 hover:border-rose-400"
                    : isHigh
                    ? "border-amber-300 hover:border-amber-400"
                    : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                          isCrit
                            ? "bg-rose-100 text-rose-800 border-rose-300"
                            : isHigh
                            ? "bg-amber-100 text-amber-800 border-amber-300"
                            : "bg-slate-100 text-slate-700 border-slate-200"
                        }`}
                      >
                        {alert.risk_classification} Risk ({alert.risk_score}/100)
                      </span>
                      <span className="text-xs font-semibold text-slate-500">{alert.category}</span>
                      <span className="text-xs font-mono text-slate-400">SKU: {alert.product_id}</span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900">{alert.product_name}</h3>
                    
                    <p className="text-xs text-slate-600 leading-relaxed max-w-3xl">
                      {alert.alert_reason}
                    </p>
                  </div>

                  {/* Telemetry Pill Grid */}
                  <div className="flex items-center gap-4 text-xs font-medium bg-slate-50 p-3 rounded-lg border border-slate-100 shrink-0">
                    <div>
                      <span className="text-[10px] text-slate-400 block">Current Stock</span>
                      <span className="text-slate-900 font-bold">{alert.current_inventory.toFixed(0)} units</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">Avg Demand</span>
                      <span className="text-slate-900 font-bold">{alert.avg_daily_demand.toFixed(1)}/d</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">Lead Time</span>
                      <span className="text-slate-900 font-bold">{alert.lead_time_days} days</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">Est. Runout</span>
                      <span className={`font-bold ${isCrit ? "text-rose-600" : isHigh ? "text-amber-600" : "text-slate-900"}`}>
                        {alert.days_until_stockout.toFixed(1)} days
                      </span>
                    </div>
                  </div>
                </div>

                {/* Recommended Operational Action Footer */}
                <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 text-slate-700">
                    <span className="font-bold text-blue-700">Action:</span>
                    <span>{alert.recommended_action}</span>
                  </div>
                  <a
                    href="/inventory"
                    className="text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1 shrink-0"
                  >
                    View in Planner <ArrowUpRight className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })
        ) : (
          <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-400">
            No stockout alerts match the selected criteria.
          </div>
        )}
      </div>
    </div>
  );
}
