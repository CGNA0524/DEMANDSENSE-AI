"use client";

import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  Calendar, 
  Layers, 
  Cpu, 
  Download, 
  Award, 
  CheckCircle2, 
  Sparkles,
  RefreshCw,
  Info
} from "lucide-react";
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from "recharts";

import { apiClient } from "@/lib/api";
import { Product, Store, ForecastResponse } from "@/types";

export default function ForecastingPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string>("");
  const [selectedStoreId, setSelectedStoreId] = useState<string>("ALL");
  const [horizonDays, setHorizonDays] = useState<number>(30);
  const [selectedModel, setSelectedModel] = useState<string>("AUTO");

  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial product list
  useEffect(() => {
    async function initCatalog() {
      try {
        const [prods, strList] = await Promise.all([
          apiClient.getProducts(),
          apiClient.getStores()
        ]);
        setProducts(prods);
        setStores(strList);
        if (prods.length > 0) {
          setSelectedProductId(prods[0].product_id);
        }
      } catch (err: any) {
        console.error("Failed to load catalog:", err);
      }
    }
    initCatalog();
  }, []);

  // Run forecast automatically when product changes or on generate click
  const runForecast = async () => {
    if (!selectedProductId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.generateForecast({
        product_id: selectedProductId,
        store_id: selectedStoreId !== "ALL" ? selectedStoreId : undefined,
        horizon_days: horizonDays,
        selected_model: selectedModel
      });
      setForecastResult(res);
    } catch (err: any) {
      setError(err.message || "Forecasting failed.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProductId) {
      runForecast();
    }
  }, [selectedProductId, horizonDays]);

  // Combine historical and forecast points for chart
  const chartData = forecastResult
    ? [
        ...forecastResult.historical_points.map((hp) => ({
          date: hp.date,
          actual: hp.units_sold,
          predicted: null,
          lower: null,
          upper: null,
          isForecast: false,
        })),
        ...forecastResult.forecast_points.map((fp) => ({
          date: fp.date,
          actual: null,
          predicted: fp.predicted_units,
          lower: fp.lower_bound,
          upper: fp.upper_bound,
          isForecast: true,
        })),
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Control Banner */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Machine Learning Demand Forecasting
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Multi-model tournament (Seasonal-Naive, Moving Avg, Ridge Regression, Random Forest, XGBoost) with chronological validation
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Product Selector */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <span className="font-semibold text-slate-500">Product:</span>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="bg-transparent font-medium text-slate-800 focus:outline-none cursor-pointer max-w-xs truncate"
              >
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_name} ({p.product_id})
                  </option>
                ))}
              </select>
            </div>

            {/* Store Selector */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <span className="font-semibold text-slate-500">Store:</span>
              <select
                value={selectedStoreId}
                onChange={(e) => setSelectedStoreId(e.target.value)}
                className="bg-transparent font-medium text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Stores</option>
                {stores.map((s) => (
                  <option key={s.store_id} value={s.store_id}>
                    {s.store_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Horizon Selector */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={horizonDays}
                onChange={(e) => setHorizonDays(Number(e.target.value))}
                className="bg-transparent font-medium text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value={7}>7 Days</option>
                <option value={14}>14 Days</option>
                <option value={30}>30 Days</option>
                <option value={60}>60 Days</option>
              </select>
            </div>

            {/* Model Override */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <Cpu className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-transparent font-medium text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value="AUTO">Auto Tournament (Best WAPE)</option>
                <option value="XGBoost">XGBoost Regressor</option>
                <option value="Random Forest">Random Forest</option>
                <option value="Ridge">Ridge Regression</option>
                <option value="Seasonal-Naive">Seasonal-Naive (7d)</option>
                <option value="Moving Average">Moving Average</option>
              </select>
            </div>

            <button
              onClick={runForecast}
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition shadow-xs shadow-blue-500/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              {loading ? "Computing..." : "Run Forecast"}
            </button>

            {selectedProductId && (
              <a
                href={apiClient.getExportForecastUrl(selectedProductId, horizonDays)}
                download
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition border border-slate-200"
              >
                <Download className="w-3.5 h-3.5" />
                Export CSV
              </a>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-medium">
          {error}
        </div>
      )}

      {/* Selected Model & KPI Highlight */}
      {forecastResult && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Tournament Winner</span>
            <div className="mt-2 flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" />
              <span className="text-sm font-bold text-slate-900">{forecastResult.selected_model}</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Selected based on chronological holdout WAPE</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Forecast Horizon</span>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-xl font-bold text-slate-900">{forecastResult.horizon_days}</span>
              <span className="text-xs text-slate-500 font-medium">Days ahead</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">{forecastResult.forecast_start_date} to {forecastResult.forecast_end_date}</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Avg Daily Projected</span>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-xl font-bold text-blue-700">{forecastResult.avg_predicted_daily}</span>
              <span className="text-xs text-slate-500 font-medium">units / day</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Expected run rate during horizon</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Projected Demand</span>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-xl font-bold text-slate-900">{forecastResult.total_predicted_units.toLocaleString()}</span>
              <span className="text-xs text-slate-500 font-medium">units</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Cumulative required volume</p>
          </div>
        </div>
      )}

      {/* Main Forecast Chart */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              Demand Forecast Trajectory &amp; 95% Confidence Interval
            </h2>
            <p className="text-xs text-slate-500">
              Historical observed sales (gray) transitioning into model predictions (blue) with empirical uncertainty bounds
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-2.5 h-0.5 bg-slate-400"></span> Actual Sales
            </span>
            <span className="flex items-center gap-1.5 text-blue-700 font-semibold">
              <span className="w-2.5 h-0.5 bg-blue-600"></span> Predicted
            </span>
            <span className="flex items-center gap-1.5 text-indigo-600">
              <span className="w-2.5 h-2 bg-indigo-100 border border-indigo-300 rounded-2xs"></span> 95% Bounds
            </span>
          </div>
        </div>

        <div className="h-80 w-full">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 11, fill: "#64748b" }}
                  tickFormatter={(val) => val.slice(5)} 
                />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "12px" }}
                  formatter={(val: any, name: any) => [
                    val !== null ? Number(val).toFixed(1) : "—",
                    name === "actual" ? "Actual Units" : name === "predicted" ? "Forecasted Units" : name
                  ]}
                />
                {/* Confidence band */}
                <Area type="monotone" dataKey="upper" stroke="none" fill="#e0e7ff" fillOpacity={0.6} name="Upper Bound 95%" />
                <Area type="monotone" dataKey="lower" stroke="none" fill="#ffffff" fillOpacity={1.0} name="Lower Bound 95%" />
                
                {/* Actual historical line */}
                <Line type="monotone" dataKey="actual" stroke="#94a3b8" strokeWidth={2} dot={false} name="Actual Units" />
                
                {/* Predicted future line */}
                <Line type="monotone" dataKey="predicted" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3, fill: "#2563eb" }} name="Predicted Units" />
              </ComposedChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-400">
              Generating time-series predictions...
            </div>
          )}
        </div>
      </div>

      {/* Model Tournament Evaluation Table */}
      {forecastResult && forecastResult.validation_metrics.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-200">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-500" />
              Chronological Holdout Validation Leaderboard
            </h2>
            <p className="text-xs text-slate-500">
              Evaluated strictly on the latest 14-day holdout validation window. Never evaluated on future lookahead data.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3">Rank</th>
                  <th className="px-5 py-3">Candidate Model</th>
                  <th className="px-4 py-3">WAPE</th>
                  <th className="px-4 py-3">MAE</th>
                  <th className="px-4 py-3">RMSE</th>
                  <th className="px-4 py-3">MAPE</th>
                  <th className="px-5 py-3">Selection Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {forecastResult.validation_metrics.map((m) => (
                  <tr key={m.model_name} className={m.is_selected ? "bg-blue-50/50 font-semibold" : "hover:bg-slate-50/80"}>
                    <td className="px-5 py-3 text-slate-900 font-bold">#{m.rank}</td>
                    <td className="px-5 py-3 text-slate-900 flex items-center gap-2">
                      {m.model_name}
                      {m.is_selected && (
                        <span className="text-[10px] font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                          Selected
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-blue-700 font-bold">{(m.wape * 100).toFixed(2)}%</td>
                    <td className="px-4 py-3">{m.mae.toFixed(2)} units</td>
                    <td className="px-4 py-3">{m.rmse.toFixed(2)} units</td>
                    <td className="px-4 py-3">{typeof m.mape === "number" ? `${m.mape.toFixed(2)}%` : "N/A (zeros)"}</td>
                    <td className="px-5 py-3">
                      {m.is_selected ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700 text-xs font-semibold">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Optimal Holdout Fit
                        </span>
                      ) : (
                        <span className="text-slate-400">Baseline</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Forecast Details Table */}
      {forecastResult && forecastResult.forecast_points.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Projected Daily Demands</h2>
              <p className="text-xs text-slate-500">Day-by-day forecast figures with 95% confidence intervals</p>
            </div>
            <a
              href={apiClient.getExportForecastUrl(selectedProductId, horizonDays)}
              download
              className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              <Download className="w-3.5 h-3.5" /> Download Full Schedule (.CSV)
            </a>
          </div>

          <div className="max-h-64 overflow-y-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-500 font-semibold sticky top-0 border-b border-slate-200">
                <tr>
                  <th className="px-5 py-2.5">Date</th>
                  <th className="px-5 py-2.5">Predicted Units</th>
                  <th className="px-5 py-2.5">Lower Bound (95%)</th>
                  <th className="px-5 py-2.5">Upper Bound (95%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {forecastResult.forecast_points.map((p) => (
                  <tr key={p.date} className="hover:bg-slate-50/80">
                    <td className="px-5 py-2 text-slate-900 font-mono">{p.date}</td>
                    <td className="px-5 py-2 font-bold text-blue-700">{p.predicted_units.toFixed(1)}</td>
                    <td className="px-5 py-2 text-slate-500">{p.lower_bound.toFixed(1)}</td>
                    <td className="px-5 py-2 text-slate-500">{p.upper_bound.toFixed(1)}</td>
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
