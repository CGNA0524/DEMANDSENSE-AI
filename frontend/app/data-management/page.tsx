"use client";

import { useState, useEffect } from "react";
import { 
  Database, 
  Upload, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertTriangle, 
  Download, 
  RefreshCw, 
  ArrowRight,
  Sparkles,
  History,
  FileCheck
} from "lucide-react";

import { apiClient } from "@/lib/api";
import { DatasetPreviewResponse, ValidationSummary, DatasetImportHistoryItem } from "@/types";

export default function DataManagementPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<DatasetPreviewResponse | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [validationResult, setValidationResult] = useState<ValidationSummary | null>(null);
  const [history, setHistory] = useState<DatasetImportHistoryItem[]>([]);
  
  const [uploading, setUploading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      const hist = await apiClient.getImportHistory();
      setHistory(hist);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setSelectedFile(file);
    setPreview(null);
    setValidationResult(null);
    setErrorMessage(null);
    setStatusMessage(null);

    setUploading(true);
    try {
      const res = await apiClient.uploadDataset(file);
      setPreview(res);
      // Initialize mapping with suggested mapping
      const initMap: Record<string, string> = {};
      Object.entries(res.suggested_mapping).forEach(([canon, val]) => {
        if (val) initMap[canon] = val;
      });
      setMapping(initMap);
      setStatusMessage(`File '${file.name}' parsed. Please review and confirm column mappings below.`);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to parse file.");
    } finally {
      setUploading(false);
    }
  };

  const handleCommitImport = async () => {
    if (!preview) return;
    setImporting(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const res = await apiClient.commitImport(preview.filename, mapping);
      setValidationResult(res);
      if (res.is_valid) {
        setStatusMessage(`Successfully imported ${res.valid_rows.toLocaleString()} records across ${res.detected_products_count} products.`);
        fetchHistory();
      } else {
        setErrorMessage("Dataset validation found errors. Please correct the mappings and try again.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to commit import.");
    } finally {
      setImporting(false);
    }
  };

  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const res = await apiClient.loadDemoData();
      setValidationResult(res);
      setStatusMessage(`Synthetic demo dataset (15 products, 180 days) generated and loaded into SQLite.`);
      fetchHistory();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load demo data.");
    } finally {
      setLoadingDemo(false);
    }
  };

  const canonicalFields = [
    { key: "date", label: "Date (Required)", req: true },
    { key: "product_id", label: "Product ID / SKU (Required)", req: true },
    { key: "units_sold", label: "Units Sold / Quantity (Required)", req: true },
    { key: "product_name", label: "Product Name", req: false },
    { key: "category", label: "Category", req: false },
    { key: "store_id", label: "Store ID", req: false },
    { key: "unit_price", label: "Unit Price ($)", req: false },
    { key: "unit_cost", label: "Unit Cost ($)", req: false },
    { key: "inventory_on_hand", label: "Inventory On Hand", req: false },
    { key: "supplier_lead_time_days", label: "Supplier Lead Time (Days)", req: false },
    { key: "promotion", label: "Promotion Active (0/1)", req: false },
    { key: "discount", label: "Discount Rate", req: false },
    { key: "stockout_indicator", label: "Stockout Event Indicator", req: false },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-600" />
              Dataset Management &amp; Ingestion Hub
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Upload CSV/XLSX files, configure canonical schema mappings, preview records, and inspect validation reports
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <a
              href={apiClient.getTemplateDownloadUrl()}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition border border-slate-200"
            >
              <Download className="w-3.5 h-3.5" /> Download Template (.CSV)
            </a>

            <button
              onClick={handleLoadDemo}
              disabled={loadingDemo}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-xs font-semibold transition border border-indigo-200 disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              {loadingDemo ? "Generating..." : "Load Synthetic Demo Data"}
            </button>
          </div>
        </div>
      </div>

      {statusMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          {statusMessage}
        </div>
      )}

      {errorMessage && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-medium flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          {errorMessage}
        </div>
      )}

      {/* Upload Dropzone */}
      <div className="bg-white p-6 rounded-xl border-2 border-dashed border-slate-300 hover:border-blue-500 transition text-center">
        <Upload className="w-8 h-8 text-blue-600 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-slate-900">Upload Historical Sales &amp; Inventory Dataset</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Upload a CSV or Excel (.xlsx) file. Columns will be auto-recognized and matched against canonical fields.
        </p>

        <label className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg cursor-pointer shadow-xs shadow-blue-500/20 transition">
          <FileSpreadsheet className="w-4 h-4" />
          {uploading ? "Analyzing..." : "Choose File to Upload"}
          <input
            type="file"
            accept=".csv, .xlsx, .xls, .txt"
            onChange={handleFileChange}
            disabled={uploading}
            className="hidden"
          />
        </label>
        {selectedFile && (
          <p className="mt-2 text-xs font-mono text-slate-600">
            Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </p>
        )}
      </div>

      {/* Column Mapping Section */}
      {preview && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Canonical Column Mapping &amp; Alignment</h2>
              <p className="text-xs text-slate-500">
                Confirm which file columns correspond to the DemandSense canonical schema
              </p>
            </div>
            <button
              onClick={handleCommitImport}
              disabled={importing}
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold transition shadow-xs disabled:opacity-50"
            >
              <FileCheck className="w-4 h-4" />
              {importing ? "Validating & Importing..." : "Validate & Import Dataset"}
            </button>
          </div>

          <div className="p-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {canonicalFields.map((field) => (
              <div key={field.key} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {field.label} {field.req && <span className="text-rose-500">*</span>}
                </label>
                <select
                  value={mapping[field.key] || ""}
                  onChange={(e) => setMapping(prev => ({ ...prev, [field.key]: e.target.value }))}
                  className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-xs text-slate-800 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">(Not Mapped / Default)</option>
                  {preview.detected_columns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          {/* Data Preview Table */}
          <div className="border-t border-slate-200 p-5">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">First 10 Rows Raw Preview</h3>
            <div className="max-h-56 overflow-auto border border-slate-200 rounded-lg">
              <table className="w-full text-left text-[11px] text-slate-600">
                <thead className="bg-slate-100 text-slate-700 font-semibold sticky top-0">
                  <tr>
                    {preview.detected_columns.map((c) => (
                      <th key={c} className="px-3 py-2 border-b border-slate-200 whitespace-nowrap">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {preview.preview_data.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      {preview.detected_columns.map((c) => (
                        <td key={c} className="px-3 py-1.5 whitespace-nowrap">{String(row[c] ?? "")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Validation Summary Report */}
      {validationResult && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Data Quality &amp; Ingestion Audit Summary
              </h2>
              <p className="text-xs text-slate-500">Summary of verified records and validation checks</p>
            </div>
            <span
              className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                validationResult.is_valid ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
              }`}
            >
              {validationResult.is_valid ? "PASSED" : "FAILED"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Valid Rows</span>
              <span className="text-lg font-bold text-slate-900">{validationResult.valid_rows.toLocaleString()}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Unique Products</span>
              <span className="text-lg font-bold text-slate-900">{validationResult.detected_products_count}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Date Range</span>
              <span className="text-xs font-bold text-slate-900 block mt-1">
                {validationResult.date_min || "—"} to {validationResult.date_max || "—"}
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Warnings &amp; Cleanups</span>
              <span className="text-lg font-bold text-amber-700">{validationResult.warning_count}</span>
            </div>
          </div>

          {validationResult.issues.length > 0 && (
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
              <span className="font-bold text-slate-700 block mb-1">Validation Notes:</span>
              {validationResult.issues.map((issue, idx) => (
                <div key={idx} className="text-slate-600 flex items-start gap-1.5">
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded uppercase ${issue.issue_type === "ERROR" ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-700"}`}>
                    {issue.issue_type}
                  </span>
                  <span>{issue.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Ingestion History Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <History className="w-4 h-4 text-slate-500" />
              Dataset Ingestion History &amp; Audit Trail
            </h2>
            <p className="text-xs text-slate-500">Historical records of uploaded and committed datasets</p>
          </div>
          <button
            onClick={fetchHistory}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Import Date</th>
                <th className="px-4 py-3">Filename</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3 text-right">Valid Rows</th>
                <th className="px-4 py-3 text-right">Warnings</th>
                <th className="px-4 py-3 text-center">Environment</th>
                <th className="px-5 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {history.map((h) => (
                <tr key={h.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 text-slate-900 font-mono">
                    {new Date(h.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 font-semibold text-slate-900">{h.filename}</td>
                  <td className="px-4 py-3 uppercase text-slate-500">{h.file_type}</td>
                  <td className="px-4 py-3 text-right font-bold text-slate-900">{h.valid_row_count.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-amber-600">{h.warning_count}</td>
                  <td className="px-4 py-3 text-center">
                    {h.is_demo ? (
                      <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded-full">
                        Synthetic Demo
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded-full">
                        User Upload
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-center">
                    <span className="text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full text-[10px]">
                      {h.status}
                    </span>
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
