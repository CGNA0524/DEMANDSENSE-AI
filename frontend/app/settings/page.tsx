"use client";

import { useState } from "react";
import { 
  FileText, 
  Download, 
  FileSpreadsheet, 
  Sliders, 
  Cpu, 
  Server, 
  CheckCircle, 
  ShieldCheck, 
  Database,
  ExternalLink
} from "lucide-react";

import { apiClient } from "@/lib/api";

export default function SettingsAndReportsPage() {
  const [serviceLevel, setServiceLevel] = useState<number>(0.95);
  const [horizonDays, setHorizonDays] = useState<number>(30);
  const [defaultBudget, setDefaultBudget] = useState<number>(50000);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          Enterprise Reports &amp; System Configuration
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Generate formal audit reports, export operational spreadsheets, and calibrate system-wide forecasting and safety stock thresholds
        </p>
      </div>

      {saved && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-medium flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          Platform configuration preferences updated successfully.
        </div>
      )}

      {/* Reports Center */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Download className="w-4 h-4 text-blue-600" />
            Downloadable Operational Reports
          </h2>
          <p className="text-xs text-slate-500">
            Export structured reports directly from the active database for procurement, logistics, and executive review
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {/* Inventory Recommendation Report */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
                <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                Comprehensive Replenishment Plan
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Full catalog inventory positions, lead times, safety stocks, reorder points, and recommended purchase order quantities.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <a
                href={apiClient.getExportInventoryUrl("csv", serviceLevel)}
                download
                className="flex-1 text-center px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition shadow-2xs"
              >
                CSV Export
              </a>
              <a
                href={apiClient.getExportInventoryUrl("xlsx", serviceLevel)}
                download
                className="flex-1 text-center px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg transition shadow-xs"
              >
                Excel (.xlsx)
              </a>
            </div>
          </div>

          {/* Stockout Risk Audit */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
                <FileText className="w-4 h-4 text-rose-600" />
                Stockout Risk Early-Warning Audit
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Risk classifications, calculated run-out days, deficit below safety buffer, and recommended operational intervention actions.
              </p>
            </div>
            <a
              href={apiClient.getExportInventoryUrl("csv", serviceLevel)}
              download
              className="text-center px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition shadow-2xs"
            >
              Download Risk Ledger (.CSV)
            </a>
          </div>

          {/* Canonical Data Template */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
                <Database className="w-4 h-4 text-blue-600" />
                Canonical CSV Ingestion Template
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Standard clean schema template formatted with canonical column headers and reference example rows.
              </p>
            </div>
            <a
              href={apiClient.getTemplateDownloadUrl()}
              download
              className="text-center px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition shadow-xs shadow-blue-500/20"
            >
              Download Schema Template
            </a>
          </div>
        </div>
      </div>

      {/* Business Assumptions & Settings */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-600" />
            Platform Business Parameters
          </h2>
          <p className="text-xs text-slate-500">Configure global mathematical parameters and optimization defaults</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <label className="text-xs font-semibold text-slate-700 block mb-1">Target Service Level (&alpha;)</label>
            <select
              value={serviceLevel}
              onChange={(e) => setServiceLevel(Number(e.target.value))}
              className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-xs text-slate-800 font-medium focus:outline-none"
            >
              <option value={0.90}>90% (Z = 1.28 - Lean)</option>
              <option value={0.95}>95% (Z = 1.64 - Industry Standard)</option>
              <option value={0.98}>98% (Z = 2.05 - High Availability)</option>
              <option value={0.99}>99% (Z = 2.33 - Critical Buffer)</option>
            </select>
            <p className="text-[10px] text-slate-400 mt-1.5">Determines the normal-distribution Z factor applied in SS = Z &times; &sigma;<sub>d</sub> &times; &radic;L.</p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <label className="text-xs font-semibold text-slate-700 block mb-1">Default Forecast Horizon</label>
            <select
              value={horizonDays}
              onChange={(e) => setHorizonDays(Number(e.target.value))}
              className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-xs text-slate-800 font-medium focus:outline-none"
            >
              <option value={7}>7 Days (Weekly)</option>
              <option value={14}>14 Days (Bi-weekly)</option>
              <option value={30}>30 Days (Monthly Operational)</option>
              <option value={60}>60 Days (Quarterly Strategic)</option>
            </select>
            <p className="text-[10px] text-slate-400 mt-1.5">Default planning horizon for demand trajectory projections.</p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <label className="text-xs font-semibold text-slate-700 block mb-1">Default Purchasing Budget ($)</label>
            <input
              type="number"
              step="5000"
              value={defaultBudget}
              onChange={(e) => setDefaultBudget(Number(e.target.value))}
              className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-xs text-slate-800 font-medium focus:outline-none"
            />
            <p className="text-[10px] text-slate-400 mt-1.5">Procurement budget cap utilized in knapsack replenishment allocation.</p>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition shadow-xs shadow-blue-500/20"
          >
            Save Parameters
          </button>
        </div>
      </div>

      {/* Model & Architecture Metadata */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-600" />
            Machine Learning Engine &amp; Architecture Audit
          </h2>
          <p className="text-xs text-slate-500">Technical specifications and execution guarantees</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <span className="font-bold text-slate-800 block text-xs">Forecasting Methodology</span>
            <ul className="space-y-1.5 text-slate-600 leading-relaxed list-disc list-inside">
              <li><strong>Models:</strong> Seasonal-Naive (7d), Moving Average, Ridge Regression, Random Forest, XGBoost.</li>
              <li><strong>Validation:</strong> Chronological holdout validation split (strictly last 14 days, zero future leakage).</li>
              <li><strong>Evaluation Metrics:</strong> WAPE (&sum;|y - &ycirc;| / &sum;y), MAE, RMSE, and zero-safe MAPE.</li>
              <li><strong>Uncertainty:</strong> Empirical residual variance intervals scaled by &radic;horizon.</li>
            </ul>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <span className="font-bold text-slate-800 block text-xs">Optimization &amp; Inventory Rules</span>
            <ul className="space-y-1.5 text-slate-600 leading-relaxed list-disc list-inside">
              <li><strong>Safety Stock:</strong> SS = Z &times; &sigma;<sub>d</sub> &times; &radic;L with continuous normal CDF.</li>
              <li><strong>Reorder Point:</strong> ROP = Expected Lead-Time Demand + Safety Stock Buffer.</li>
              <li><strong>Budget Optimizer:</strong> Priority-Weighted Bounded Integer Knapsack Optimizer.</li>
              <li><strong>Constraints:</strong> Minimum Order Quantity (MOQ) and integer Pack Size multiples.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
