# DemandSense AI — Technical Architecture Specification

## 1. Architectural Philosophy

DemandSense AI is built as a modular, decoupled full-stack platform separating machine learning and operations research from web presentation:
- **Presentation Layer**: Next.js 16 (React 19, TypeScript, Tailwind CSS, Recharts) providing responsive enterprise dashboard UI with sub-second client-side interaction.
- **Application & API Layer**: FastAPI REST service with Pydantic request/response schema validation and CORS security.
- **Computational Core**:
  - `forecasting`: Time-series lag engineering, anti-leakage safeguards, baseline algorithms, Scikit-learn regressors, and XGBoost.
  - `inventory`: Normal inverse CDF service-level calculations, dynamic safety stocks, reorder points, MOQ/pack-size logic, and risk telemetry.
  - `optimization`: Priority-weighted bounded knapsack solver for budget-constrained purchasing.
- **Persistence Layer**: SQLAlchemy ORM with SQLite for zero-dependency local development and production readiness for PostgreSQL.

---

## 2. Component Diagram

```
[ User Browser / Device ]
           │
           ▼
[ Next.js 16 Enterprise Frontend ]
  ├── App Router (8 Functional Pages)
  ├── Typed API Client (lib/api.ts)
  └── Interactive Recharts Visualizations
           │
           ▼ HTTP / JSON (REST API V1)
[ FastAPI Backend Service (:8000) ]
  ├── Routers: Health, Ingestion, Catalog, Forecasting, Inventory, Optimization, Simulator, Reports
  ├── Service Layer: DatasetService, KpiService, ForecastEngine, BudgetOptimizer
  └── SQLAlchemy ORM
           │
           ▼
[ SQLite / PostgreSQL Database ]
  ├── Products, Stores, SalesRecords
  ├── DatasetImports & Audit Logs
  └── ForecastRuns, Details, Scenarios
```

---

## 3. Data Ingestion Architecture & Safeguards

1. **Upload Sanitation**:
   - File extensions are restricted to `.csv`, `.xlsx`, `.xls`, `.txt`.
   - File size capped at 50MB.
   - Filenames are randomized with UUID prefixes to eliminate path traversal vulnerabilities.
2. **Schema Normalization**:
   - Normalized fuzzy-matching maps user column variants (e.g., `Qty_Sold`, `Sales`, `Volume` &rarr; `units_sold`).
   - Missing required keys (`date`, `product_id`, `units_sold`) block commits and return structured error diagnostics.
3. **Data Quality Cleansing**:
   - Dates parsed with ISO fallback.
   - Negative sales clipped to zero with logged audit warnings.
   - Duplicate records on `(date, product_id, store_id)` deduplicated to preserve latest state.

---

## 4. Security & Deployment

- **CORS**: Restricted via `BACKEND_CORS_ORIGINS` to trusted frontend origins.
- **Input Validation**: Strict Pydantic typing rejects malformed numbers, negative horizons, and invalid service levels.
- **Stateless Services**: All ML and optimization engines operate statelessly, allowing multi-worker scaleout behind load balancers.
