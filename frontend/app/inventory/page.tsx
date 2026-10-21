"use client";

import { useState, useEffect } from "react";
import { 
  Boxes, 
  Search, 
  Filter, 
  Download, 
  Sliders, 
  Info, 
  X, 
  CheckCircle, 
  AlertCircle,
  HelpCircle,
  DollarSign,
  PackageCheck
} from "lucide-react";

import { apiClient } from "@/lib/api";
import { InventorySummaryResponse, InventoryItemRecommendation } from "@/types";
import { StatusBadge } from "@/components/StatusBadge";
import { KpiCard } from "@/components/KpiCard";

export default function InventoryPlannerPage() {
  const [summary, setSummary] = useState<InventorySummaryResponse | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedStore, setSelectedStore] = useState<string>("ALL");
  const [serviceLevel, setServiceLevel] = useState<number>(0.95);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [loading, setLoading] = useState(false);

  // Selected item modal for detailed calculation inspection
  const [inspectItem, setInspectItem] = useState<InventoryItemRecommendation | null>(null);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const [res, cats] = await Promise.all([
        apiClient.getInventorySummary(serviceLevel, selectedCategory, selectedStore),
        apiClient.getCategories()
      ]);
      setSummary(res);
      setCategories(cats);
    } catch (err) {
      console.error("Failed to load inventory summary:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, [serviceLevel, selectedCategory, selectedStore]);

  // Filter items by search
  const filteredItems = summary?.items.filter((item) => {
    const matchesSearch =
      item.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.product_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Boxes className="w-5 h-5 text-blue-600" />
              Inventory Optimization &amp; Replenishment Planner
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Service-level driven safety stock, reorder point thresholds, and pack-size constrained replenishment
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search Box */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search SKU or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 w-44"
              />
            </div>

            {/* Category Filter */}
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

            {/* Service Level Selector */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <Sliders className="w-3.5 h-3.5 text-slate-400" />
              <span className="font-semibold text-slate-500">Service Level:</span>
              <select
                value={serviceLevel}
                onChange={(e) => setServiceLevel(Number(e.target.value))}
                className="bg-transparent font-bold text-blue-700 focus:outline-none cursor-pointer"
              >
                <option value={0.90}>90% (Z = 1.28)</option>
                <option value={0.95}>95% (Z = 1.64)</option>
                <option value={0.98}>98% (Z = 2.05)</option>
                <option value={0.99}>99% (Z = 2.33)</option>
              </select>
            </div>

            {/* Export buttons */}
            <div className="flex items-center gap-1.5">
              <a
                href={apiClient.getExportInventoryUrl("csv", serviceLevel)}
                download
                className="flex items-center gap-1 px-3 py-1.5 bg-white hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold border border-slate-200 transition"
              >
                <Download className="w-3.5 h-3.5" /> CSV
              </a>
              <a
                href={apiClient.getExportInventoryUrl("xlsx", serviceLevel)}
                download
                className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" /> Excel
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Aggregate KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Inventory On Hand"
          value={summary ? `${summary.total_inventory_units.toLocaleString()} units` : "—"}
          subtitle={`Valued at $${(summary?.total_inventory_value ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          icon={Boxes}
        />
        <KpiCard
          title="Replenishment Orders Reqd"
          value={summary?.replenishment_needed_skus ?? "—"}
          subtitle={`${summary?.total_recommended_order_units.toLocaleString() ?? 0} replenishment units`}
          icon={PackageCheck}
          badge={{ text: "Purchase Reqd", variant: "warning" }}
        />
        <KpiCard
          title="Total Reorder Capital"
          value={summary ? `$${summary.total_estimated_reorder_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "—"}
          subtitle="Wholesale expenditure required"
          icon={DollarSign}
        />
        <KpiCard
          title="Target Service Level"
          value={`${(serviceLevel * 100).toFixed(0)}%`}
          subtitle={`Normal Distribution Z = ${summary?.items[0]?.z_score.toFixed(2) ?? "1.64"}`}
          icon={Sliders}
          badge={{ text: "Configured", variant: "info" }}
        />
      </div>

      {/* Main Inventory Items Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Inventory Planning Ledger</h2>
            <p className="text-xs text-slate-500">
              Showing {filteredItems.length} products. Click any item to inspect exact safety stock and ROP mathematical calculations.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Product Name &amp; SKU</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3 text-right">Current Stock</th>
                <th className="px-4 py-3 text-right">Avg Demand</th>
                <th className="px-4 py-3 text-right">Lead Time</th>
                <th className="px-4 py-3 text-right">Safety Stock</th>
                <th className="px-4 py-3 text-right">Reorder Pt</th>
                <th className="px-4 py-3 text-right">Order Qty</th>
                <th className="px-4 py-3 text-right">Est. Cost</th>
                <th className="px-4 py-3 text-center">Status</th>
                <th className="px-5 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredItems.map((item) => (
                <tr key={item.product_id} className="hover:bg-slate-50/80 transition">
                  <td className="px-5 py-3.5">
                    <div className="font-semibold text-slate-900">{item.product_name}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{item.product_id} &bull; Pack: {item.pack_size} &bull; MOQ: {item.min_order_quantity}</div>
                  </td>
                  <td className="px-4 py-3.5">{item.category}</td>
                  <td className="px-4 py-3.5 text-right font-semibold text-slate-900">{item.current_stock.toFixed(0)}</td>
                  <td className="px-4 py-3.5 text-right">{item.avg_daily_demand.toFixed(1)}/d</td>
                  <td className="px-4 py-3.5 text-right">{item.supplier_lead_time_days}d</td>
                  <td className="px-4 py-3.5 text-right font-medium text-slate-700">{item.safety_stock.toFixed(0)}</td>
                  <td className="px-4 py-3.5 text-right font-bold text-slate-900">{item.reorder_point.toFixed(0)}</td>
                  <td className="px-4 py-3.5 text-right">
                    {item.recommended_order_qty > 0 ? (
                      <span className="font-bold text-blue-700">+{item.recommended_order_qty.toFixed(0)}</span>
                    ) : (
                      <span className="text-slate-400">0</span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 text-right font-medium text-slate-800">
                    ${item.estimated_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <StatusBadge status={item.inventory_status} />
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => setInspectItem(item)}
                      className="px-2.5 py-1 text-xs font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 rounded-md transition"
                    >
                      Audit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Formula Audit Modal */}
      {inspectItem && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-xl border border-slate-200 space-y-5 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-bold uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                  Mathematical Audit &amp; Explanation
                </span>
                <h3 className="text-base font-bold text-slate-900 mt-1">{inspectItem.product_name}</h3>
                <p className="text-xs text-slate-500 font-mono">{inspectItem.product_id} &bull; Category: {inspectItem.category}</p>
              </div>
              <button
                onClick={() => setInspectItem(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
              <div>
                <span className="text-[11px] text-slate-500">Current Stock</span>
                <p className="text-sm font-bold text-slate-900">{inspectItem.current_stock.toFixed(0)} units</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-500">Days Coverage</span>
                <p className="text-sm font-bold text-slate-900">{inspectItem.days_of_coverage.toFixed(1)} days</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-500">Lead Time</span>
                <p className="text-sm font-bold text-slate-900">{inspectItem.supplier_lead_time_days} days</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-500">Status</span>
                <div className="mt-0.5"><StatusBadge status={inspectItem.inventory_status} /></div>
              </div>
            </div>

            {/* Calculations Breakdown */}
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-white border border-slate-200 rounded-lg space-y-1">
                <span className="font-bold text-slate-800">1. Expected Lead-Time Demand (LTD)</span>
                <p className="text-slate-600 font-mono">
                  LTD = L &times; &mu;<sub>d</sub> = {inspectItem.supplier_lead_time_days} days &times; {inspectItem.avg_daily_demand} units/day = <strong>{inspectItem.lead_time_demand} units</strong>
                </p>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded-lg space-y-1">
                <span className="font-bold text-slate-800">2. Safety Stock Buffer (SS)</span>
                <p className="text-slate-600 font-mono">
                  SS = Z &times; &sigma;<sub>d</sub> &times; &radic;L = {inspectItem.z_score} &times; {inspectItem.demand_std} &times; &radic;{inspectItem.supplier_lead_time_days} = <strong>{inspectItem.safety_stock} units</strong>
                </p>
                <p className="text-[11px] text-slate-500">Target service level {inspectItem.service_level * 100}% yields Z-factor of {inspectItem.z_score}.</p>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded-lg space-y-1">
                <span className="font-bold text-slate-800">3. Reorder Point (ROP)</span>
                <p className="text-slate-600 font-mono">
                  ROP = LTD + SS = {inspectItem.lead_time_demand} + {inspectItem.safety_stock} = <strong>{inspectItem.reorder_point} units</strong>
                </p>
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded-lg space-y-1">
                <span className="font-bold text-slate-800">4. Recommended Order Calculation</span>
                <p className="text-slate-600">
                  Net Deficit = ROP ({inspectItem.reorder_point}) - Stock ({inspectItem.current_stock}) = {Math.max(0, inspectItem.reorder_point - inspectItem.current_stock).toFixed(1)} units.
                  Enforcing MOQ ({inspectItem.min_order_quantity}) and pack size multiple of {inspectItem.pack_size}: 
                  <strong className="text-blue-700 ml-1">+{inspectItem.recommended_order_qty} units</strong> 
                  (${inspectItem.estimated_cost.toFixed(2)} cost).
                </p>
              </div>
            </div>

            <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900">
              <span className="font-bold block mb-0.5">Operational Recommendation:</span>
              {inspectItem.recommended_action}
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setInspectItem(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition"
              >
                Close Audit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
