"use client";

import { useState, useEffect } from "react";
import { 
  Layers, 
  DollarSign, 
  PieChart, 
  AlertCircle, 
  CheckCircle2, 
  Download, 
  ArrowRight,
  TrendingUp,
  Percent,
  Sliders,
  Sparkles
} from "lucide-react";
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from "recharts";

import { apiClient } from "@/lib/api";
import { BudgetOptimizationResponse, OptimizedOrderItem } from "@/types";
import { KpiCard } from "@/components/KpiCard";

export default function BudgetOptimizerPage() {
  const [budget, setBudget] = useState<number>(35000);
  const [serviceLevel, setServiceLevel] = useState<number>(0.95);
  const [customPriorities, setCustomPriorities] = useState<Record<string, string>>({});
  const [optimizationResult, setOptimizationResult] = useState<BudgetOptimizationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.optimizeBudget({
        budget,
        service_level: serviceLevel,
        custom_priorities: Object.keys(customPriorities).length > 0 ? customPriorities : undefined
      });
      setOptimizationResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to optimize purchasing budget.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runOptimization();
  }, [budget, serviceLevel]);

  const handlePriorityChange = (productId: string, newPrio: string) => {
    setCustomPriorities(prev => ({
      ...prev,
      [productId]: newPrio
    }));
  };

  // Recharts data comparing unconstrained vs optimized for top items
  const chartData = optimizationResult?.items.slice(0, 10).map((item) => ({
    name: item.product_id.replace("PROD-", ""),
    unconstrained: item.unconstrained_order_qty,
    optimized: item.optimized_order_qty,
    cost: item.item_total_cost
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Layers className="w-5 h-5 text-blue-600" />
              Budget-Constrained Replenishment Optimizer
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Priority-weighted bounded integer knapsack solver enforcing minimum order quantities, pack sizes, and capital limits
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Budget Input */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-semibold text-slate-500">Available Budget:</span>
              <input
                type="number"
                step="5000"
                min="1000"
                value={budget}
                onChange={(e) => setBudget(Math.max(0, Number(e.target.value)))}
                className="w-24 bg-transparent font-bold text-slate-900 focus:outline-none"
              />
            </div>

            {/* Quick Preset Buttons */}
            <div className="flex items-center gap-1">
              {[20000, 35000, 50000, 75000].map((preset) => (
                <button
                  key={preset}
                  onClick={() => setBudget(preset)}
                  className={`px-2 py-1 text-[11px] rounded font-semibold transition ${
                    budget === preset
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 hover:bg-slate-200 text-slate-700"
                  }`}
                >
                  ${(preset / 1000).toFixed(0)}k
                </button>
              ))}
            </div>

            {/* Service Level */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <Sliders className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={serviceLevel}
                onChange={(e) => setServiceLevel(Number(e.target.value))}
                className="bg-transparent font-bold text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value={0.90}>90% SLA</option>
                <option value={0.95}>95% SLA</option>
                <option value={0.98}>98% SLA</option>
              </select>
            </div>

            <button
              onClick={runOptimization}
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition shadow-xs shadow-blue-500/20 disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {loading ? "Optimizing..." : "Re-Optimize"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-medium">
          {error}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Allocated Spend"
          value={optimizationResult ? `$${optimizationResult.allocated_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "—"}
          subtitle={`${optimizationResult?.budget_utilization_pct.toFixed(1) ?? 0}% budget utilization`}
          icon={DollarSign}
          badge={{ 
            text: `${(optimizationResult?.budget_utilization_pct ?? 0) >= 95 ? "Near Ceiling" : "Within Budget"}`,
            variant: "info"
          }}
        />
        <KpiCard
          title="Remaining Budget"
          value={optimizationResult ? `$${optimizationResult.remaining_budget.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "—"}
          subtitle="Unallocated procurement cash"
          icon={Percent}
          badge={{ text: "Available", variant: "success" }}
        />
        <KpiCard
          title="Unconstrained Need"
          value={optimizationResult ? `$${optimizationResult.total_unconstrained_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "—"}
          subtitle={`Total ideal units: ${optimizationResult?.total_unconstrained_units.toLocaleString() ?? 0}`}
          icon={Layers}
        />
        <KpiCard
          title="SKU Fulfillment"
          value={optimizationResult ? `${optimizationResult.fully_replenished_skus_count} / ${optimizationResult.items.length}` : "—"}
          subtitle={`${optimizationResult?.partially_replenished_skus_count ?? 0} partial &bull; ${optimizationResult?.unreplenished_skus_count ?? 0} deferred`}
          icon={CheckCircle2}
          badge={{ text: "Knapsack Plan", variant: "neutral" }}
        />
      </div>

      {/* Allocation Comparison Chart */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              Unconstrained Demand vs. Budget-Constrained Allocation (Top SKUs)
            </h2>
            <p className="text-xs text-slate-500">
              Compares theoretical ideal order quantities with pack-size optimized purchase orders
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 text-slate-500">
              <span className="w-2.5 h-2.5 rounded-sm bg-slate-300"></span> Unconstrained
            </span>
            <span className="flex items-center gap-1.5 text-blue-700 font-semibold">
              <span className="w-2.5 h-2.5 rounded-sm bg-blue-600"></span> Optimized Allocation
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "12px" }}
                  formatter={(val: any, name: any) => [Number(val).toLocaleString(), name === "unconstrained" ? "Unconstrained Units" : "Optimized Units"]}
                />
                <Bar dataKey="unconstrained" fill="#cbd5e1" radius={[4, 4, 0, 0]} name="unconstrained" />
                <Bar dataKey="optimized" fill="#2563eb" radius={[4, 4, 0, 0]} name="optimized" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-400">
              Computing optimal allocation...
            </div>
          )}
        </div>
      </div>

      {/* Optimized Order Plan Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Procurement Optimization Schedule</h2>
            <p className="text-xs text-slate-500">
              Discrete pack-size allocations prioritized by ROI, demand urgency, and strategic tier
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Product Name &amp; SKU</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Priority Tier</th>
                <th className="px-4 py-3 text-right">Unit Cost</th>
                <th className="px-4 py-3 text-right">Ideal Need</th>
                <th className="px-4 py-3 text-right">Allocated Qty</th>
                <th className="px-4 py-3 text-right">Total Cost</th>
                <th className="px-4 py-3">Fulfillment</th>
                <th className="px-4 py-3 text-right">Coverage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {optimizationResult?.items.map((item) => (
                <tr key={item.product_id} className="hover:bg-slate-50/80 transition">
                  <td className="px-5 py-3.5">
                    <div className="font-semibold text-slate-900">{item.product_name}</div>
                    <div className="text-[11px] text-slate-400 font-mono">
                      {item.product_id} &bull; Pack: {item.pack_size} &bull; MOQ: {item.min_order_quantity}
                    </div>
                  </td>
                  <td className="px-4 py-3.5">{item.category}</td>
                  <td className="px-4 py-3.5">
                    <select
                      value={customPriorities[item.product_id] || item.priority_level}
                      onChange={(e) => handlePriorityChange(item.product_id, e.target.value)}
                      className={`text-[11px] font-bold px-2 py-0.5 rounded border focus:outline-none cursor-pointer ${
                        (customPriorities[item.product_id] || item.priority_level) === "HIGH"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : (customPriorities[item.product_id] || item.priority_level) === "MEDIUM"
                          ? "bg-blue-50 text-blue-700 border-blue-200"
                          : "bg-slate-100 text-slate-600 border-slate-200"
                      }`}
                    >
                      <option value="HIGH">HIGH (4x)</option>
                      <option value="MEDIUM">MEDIUM (2x)</option>
                      <option value="LOW">LOW (1x)</option>
                    </select>
                  </td>
                  <td className="px-4 py-3.5 text-right font-medium">${item.unit_cost.toFixed(2)}</td>
                  <td className="px-4 py-3.5 text-right text-slate-400">{item.unconstrained_order_qty.toFixed(0)}</td>
                  <td className="px-4 py-3.5 text-right font-bold text-slate-900">
                    {item.optimized_order_qty > 0 ? (
                      <span className="text-blue-700 font-bold">+{item.optimized_order_qty.toFixed(0)}</span>
                    ) : (
                      <span className="text-slate-400">0</span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 text-right font-bold text-slate-900">
                    ${item.item_total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="w-24">
                      <div className="flex justify-between text-[10px] text-slate-500 mb-0.5">
                        <span>{item.replenishment_fulfillment_pct}%</span>
                        {item.unmet_units > 0 && <span className="text-rose-500 font-bold">-{item.unmet_units.toFixed(0)}</span>}
                      </div>
                      <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                        <div
                          style={{ width: `${item.replenishment_fulfillment_pct}%` }}
                          className={`h-full ${item.replenishment_fulfillment_pct >= 100 ? "bg-emerald-500" : item.replenishment_fulfillment_pct > 0 ? "bg-amber-500" : "bg-slate-300"}`}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-right font-medium text-slate-800">
                    {item.expected_days_coverage} days
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
