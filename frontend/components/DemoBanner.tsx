"use client";

import { Info, RefreshCw, Database } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { apiClient } from "@/lib/api";

interface DemoBannerProps {
  onDataReloaded?: () => void;
}

export function DemoBanner({ onDataReloaded }: DemoBannerProps) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleReload = async () => {
    setLoading(true);
    try {
      await apiClient.loadDemoData();
      setMessage("Deterministic synthetic demo dataset (15 products, 180 days) reloaded.");
      if (onDataReloaded) onDataReloaded();
      setTimeout(() => setMessage(null), 4000);
    } catch (err: any) {
      alert(`Error reloading demo data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/80 rounded-xl p-4 shadow-2xs">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 rounded-lg text-blue-700 shrink-0 mt-0.5 sm:mt-0">
            <Info className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-800 bg-blue-100/80 px-2 py-0.5 rounded">
                Synthetic Demo Environment
              </span>
              <span className="text-xs text-slate-500 font-medium">Deterministic Retail Simulation</span>
            </div>
            <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">
              This instance is preloaded with synthetic multi-category retail history (15 products, 180 days) featuring weekly seasonality, marketing promotion lifts, and simulated stockouts. Generated results are simulation benchmarks, never presented as actual commercial records.
            </p>
            {message && <p className="text-xs font-semibold text-emerald-700 mt-1">{message}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
          <button
            onClick={handleReload}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 transition shadow-2xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-blue-600 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Reloading..." : "Reset Demo Data"}
          </button>
          <Link
            href="/data-management"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition shadow-xs shadow-blue-500/20"
          >
            <Database className="w-3.5 h-3.5" />
            Upload CSV/XLSX
          </Link>
        </div>
      </div>
    </div>
  );
}
