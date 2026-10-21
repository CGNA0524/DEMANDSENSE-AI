"use client";

import { useState, useEffect } from "react";
import { 
  SlidersHorizontal, 
  TrendingUp, 
  Clock, 
  ShieldCheck, 
  DollarSign, 
  AlertTriangle, 
  Play, 
  RotateCcw,
  ArrowRight,
  Info
} from "lucide-react";

import { apiClient } from "@/lib/api";
import { ScenarioSimulationResponse } from "@/types";
import { StatusBadge } from "@/components/StatusBadge";

export default function SimulatorPage() {
  const [demandMultiplier, setDemandMultiplier] = useState<number>(1.20); // +20% demand
  const [leadTimeDelta, setLeadTimeDelta] = useState<number>(3); // +3 days delay
  const [serviceLevel, setServiceLevel] = useState<number>(0.98); // 98%
  const [budget, setBudget] = useState<number>(45000);
  const [inventoryShock, setInventoryShock] = useState<number>(-0.10); // -10% stock disruption

  const [simulationResult, setSimulationResult] = useState<ScenarioSimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.simulateScenario({
        name: "Supply Chain & Demand Shock Scenario",
        demand_multiplier: demandMultiplier,
        lead_time_change_days: leadTimeDelta,
        service_level: serviceLevel,
        budget: budget,
        inventory_shock_pct: inventoryShock,
      });
      setSimulationResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to simulate scenario.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, []);

  const resetToBaseline = () => {
    setDemandMultiplier(1.0);
    setLeadTimeDelta(0);
    setServiceLevel(0.95);
    setInventoryShock(0.0);
    setBudget(50000);
  };

  return (
    <div className="space-y-6">
      {/* Simulation Controls Panel */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-5 border-b border-slate-100 pb-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5 text-blue-600" />
              What-If Scenario Simulation Engine
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Stress-test inventory resiliency, lead-time supplier delays, and surge demand without modifying baseline historical data
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={resetToBaseline}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset Baseline
            </button>
            <button
              onClick={runSimulation}
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition shadow-xs shadow-blue-500/20 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {loading ? "Simulating..." : "Run Simulation"}
            </button>
          </div>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Demand Surge Slider */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
            <div className="flex justify-between items-center text-xs mb-1">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5 text-blue-600" /> Demand Surge
              </span>
              <span className="font-bold text-blue-700">
                {demandMultiplier > 1 ? `+${((demandMultiplier - 1) * 100).toFixed(0)}%` : `${((demandMultiplier - 1) * 100).toFixed(0)}%`}
              </span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.05"
              value={demandMultiplier}
              onChange={(e) => setDemandMultiplier(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>-50% (Slump)</span>
              <span>Baseline (1.0x)</span>
              <span>+100% (Surge)</span>
            </div>
          </div>

          {/* Supplier Lead Time Delta */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
            <div className="flex justify-between items-center text-xs mb-1">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-amber-600" /> Lead Time Change
              </span>
              <span className="font-bold text-amber-700">
                {leadTimeDelta >= 0 ? `+${leadTimeDelta} days` : `${leadTimeDelta} days`}
              </span>
            </div>
            <input
              type="range"
              min="-3"
              max="14"
              step="1"
              value={leadTimeDelta}
              onChange={(e) => setLeadTimeDelta(Number(e.target.value))}
              className="w-full accent-amber-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>-3d (Faster)</span>
              <span>0d (Normal)</span>
              <span>+14d (Disruption)</span>
            </div>
          </div>

          {/* Target Service Level */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
            <div className="flex justify-between items-center text-xs mb-1">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Target Service Level
              </span>
              <span className="font-bold text-emerald-700">{(serviceLevel * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.80"
              max="0.99"
              step="0.01"
              value={serviceLevel}
              onChange={(e) => setServiceLevel(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>80% (Lenient)</span>
              <span>95% (Standard)</span>
              <span>99% (Strict)</span>
            </div>
          </div>

          {/* Stock Shock Disruption */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
            <div className="flex justify-between items-center text-xs mb-1">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600" /> Stock Disruption
              </span>
              <span className="font-bold text-rose-700">{(inventoryShock * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="-0.50"
              max="0.50"
              step="0.05"
              value={inventoryShock}
              onChange={(e) => setInventoryShock(Number(e.target.value))}
              className="w-full accent-rose-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>-50% Loss</span>
              <span>0% Normal</span>
              <span>+50% Inflow</span>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-medium">
          {error}
        </div>
      )}

      {/* Side-by-Side Comparison Metrics */}
      {simulationResult && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {simulationResult.metric_comparisons.map((m) => {
            const isNegative = m.absolute_change < 0;
            const isNeutral = m.absolute_change === 0;

            return (
              <div key={m.metric_name} className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{m.metric_name}</span>
                
                <div className="mt-2.5 flex items-baseline justify-between">
                  <div>
                    <span className="text-xl font-bold text-slate-900">
                      {m.unit === "$" ? `$${m.simulated_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : `${m.simulated_value.toLocaleString(undefined, { maximumFractionDigits: 0 })} ${m.unit}`}
                    </span>
                    <span className="text-[11px] text-slate-400 block mt-0.5">
                      Baseline: {m.unit === "$" ? `$${m.baseline_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : `${m.baseline_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
                    </span>
                  </div>

                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                      isNeutral
                        ? "bg-slate-100 text-slate-600"
                        : m.metric_name.includes("Risk") || m.metric_name.includes("Cost")
                        ? m.absolute_change > 0 ? "bg-rose-50 text-rose-700" : "bg-emerald-50 text-emerald-700"
                        : m.absolute_change > 0 ? "bg-blue-50 text-blue-700" : "bg-amber-50 text-amber-700"
                    }`}
                  >
                    {m.percentage_change > 0 ? `+${m.percentage_change}%` : `${m.percentage_change}%`}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Executive Simulation Narrative */}
      {simulationResult && (
        <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start gap-3">
          <Info className="w-4 h-4 text-blue-700 shrink-0 mt-0.5" />
          <p className="leading-relaxed font-medium">
            <strong>Simulation Impact Analysis: </strong>
            {simulationResult.executive_summary}
          </p>
        </div>
      )}

      {/* Product-by-Product Impact Comparison Table */}
      {simulationResult && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-200">
            <h2 className="text-sm font-bold text-slate-900">Product Level Scenario Differential</h2>
            <p className="text-xs text-slate-500">
              Comparing baseline recommended orders, safety stock buffers, and risk statuses against simulated scenario conditions
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3">Product Name &amp; SKU</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3 text-right">Baseline Order</th>
                  <th className="px-4 py-3 text-right">Simulated Order</th>
                  <th className="px-4 py-3 text-right">Baseline SS</th>
                  <th className="px-4 py-3 text-right">Simulated SS</th>
                  <th className="px-4 py-3 text-right">Simulated Cost</th>
                  <th className="px-5 py-3 text-center">Baseline &rarr; Simulated Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {simulationResult.product_comparisons.map((item) => (
                  <tr key={item.product_id} className="hover:bg-slate-50/80 transition">
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-slate-900">{item.product_name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{item.product_id}</div>
                    </td>
                    <td className="px-4 py-3.5">{item.category}</td>
                    <td className="px-4 py-3.5 text-right text-slate-500">{item.baseline_order_qty.toFixed(0)}</td>
                    <td className="px-4 py-3.5 text-right font-bold text-blue-700">
                      {item.simulated_order_qty > item.baseline_order_qty ? (
                        <span className="text-rose-600 font-bold">+{item.simulated_order_qty.toFixed(0)}</span>
                      ) : (
                        <span>+{item.simulated_order_qty.toFixed(0)}</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-right text-slate-500">{item.baseline_safety_stock.toFixed(0)}</td>
                    <td className="px-4 py-3.5 text-right font-bold text-slate-900">{item.simulated_safety_stock.toFixed(0)}</td>
                    <td className="px-4 py-3.5 text-right font-bold text-slate-900">
                      ${item.simulated_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        <StatusBadge status={item.baseline_status} />
                        <span className="text-slate-400 font-bold">&rarr;</span>
                        <StatusBadge status={item.simulated_status} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
