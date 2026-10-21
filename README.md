# DemandSense AI — Demand Forecasting & Inventory Optimization Platform

**DemandSense AI** is an intelligent enterprise retail analytics platform that empowers businesses to forecast product demand, calculate statistical safety stock, identify stockouts before they happen, and generate budget-constrained replenishment orders using machine learning and discrete optimization.

---

## 1. Project Overview & Business Problem

Retail and supply chain operations frequently suffer from two costly extremes:
1. **Stockouts ($Loss of Revenue & Customer Churn)**: Running out of fast-moving products due to unexpected demand surges or supplier lead-time delays.
2. **Overstock ($Tied-Up Working Capital & Spoilage)**: Over-purchasing slow-moving items, resulting in warehouse congestion and depreciation.
3. **Budget Trade-Off Conflicts**: When procurement capital is limited, traditional systems lack algorithmic optimization to allocate scarce dollars where they prevent the highest margin or revenue risk.

DemandSense AI bridges the gap between historical sales data and operational procurement by combining:
- Multi-model time-series forecasting (Seasonal-Naive, Moving Averages, Ridge Regression, Random Forest, XGBoost)
- Dynamic lead-time safety stock calculations ($SS = Z \times \sigma_d \times \sqrt{L}$)
- Early-warning stockout risk intelligence
- A priority-weighted bounded integer knapsack solver for budget-constrained purchasing
- Real-time what-if scenario simulations

---

## 2. Technology Stack

### Frontend
- **Framework**: Next.js 16 (App Router, Turbopack, React 19, TypeScript)
- **Styling**: Tailwind CSS (Clean enterprise SaaS theme, neutral grays, deep navy typography)
- **Charts**: Recharts (Responsive area charts, confidence intervals, multi-series comparison bars)
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.14 / 3.12+ compatible)
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & Database**: SQLAlchemy with SQLite (local development) and modular PostgreSQL support

### Data Science & Machine Learning
- **Data Manipulation**: Pandas & NumPy
- **Machine Learning**: Scikit-learn (Ridge Regression, Random Forest Regressor)
- **Gradient Boosting**: XGBoost (or Scikit-learn GradientBoosting fallback)
- **Optimization & Statistics**: SciPy (`scipy.stats.norm.ppf` for normal inverse CDF)
- **Spreadsheets**: OpenPyXL for Excel (.xlsx) generation

### Quality Assurance
- **Backend Tests**: Pytest (23 unit and integration tests passing with 100% success)
- **Frontend Verification**: TypeScript compilation, ESLint, Next.js Turbopack production build, and automated browser end-to-end testing

---

## 3. System Architecture & Folder Structure

```
DEMANDSENSE AI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entry point, lifespan, CORS, error handling
│   │   ├── core/
│   │   │   ├── config.py            # Platform configuration & settings
│   │   ├── db/
│   │   │   ├── session.py           # SQLAlchemy engine & session factory
│   │   │   ├── models.py            # SQLite / PostgreSQL declarative tables
│   │   ├── schemas/
│   │   │   ├── common.py            # Standard ApiResponse schemas
│   │   │   ├── dataset.py           # Ingestion, validation, preview schemas
│   │   │   ├── forecast.py          # Forecast requests, points, metrics
│   │   │   ├── inventory.py         # Inventory planning & risk schemas
│   │   │   ├── optimization.py      # Knapsack purchasing schemas
│   │   │   ├── scenario.py          # What-if simulation schemas
│   │   │   └── analytics.py         # KPI telemetry & trend schemas
│   │   ├── services/
│   │   │   └── dataset_service.py   # Schema mapping, CSV/XLSX parser, synthetic generator
│   │   ├── forecasting/
│   │   │   ├── feature_engineering.py # Leakage-safe lag & rolling features
│   │   │   ├── models.py            # Baselines, Ridge, Random Forest, XGBoost
│   │   │   ├── evaluation.py        # WAPE, MAE, RMSE, zero-safe MAPE
│   │   │   └── engine.py            # Chronological holdout tournament orchestrator
│   │   ├── inventory/
│   │   │   ├── calculations.py      # Lead-time demand, SS, ROP, MOQ/pack size
│   │   │   └── risk_intelligence.py # Risk scoring (0-100) & actionable alert engine
│   │   ├── optimization/
│   │   │   └── budget_optimizer.py  # Priority-weighted bounded knapsack solver
│   │   ├── analytics/
│   │   │   └── kpi_service.py       # Aggregated dashboard telemetry service
│   │   └── api/
│   │       ├── router.py            # API V1 router registration
│   │       └── endpoints/
│   │           ├── health.py        # Health probe endpoint
│   │           ├── datasets.py      # Upload, import, preview, demo data
│   │           ├── products.py      # Product catalog, categories, stores
│   │           ├── forecasting.py   # Forecast run & history endpoints
│   │           ├── inventory.py     # Inventory summary, single item, risk alerts
│   │           ├── optimization.py  # Budget optimization endpoint
│   │           ├── scenarios.py     # What-if simulation endpoint
│   │           ├── analytics.py     # Dashboard KPIs and trends
│   │           └── reports.py       # CSV and Excel export endpoints
│   ├── tests/
│   │   ├── conftest.py              # Test database session fixture
│   │   ├── test_ingestion.py        # Ingestion, mapping & synthetic demo tests
│   │   ├── test_forecasting.py      # Leakage safeguards, evaluation & models tests
│   │   ├── test_inventory.py        # Safety stock, ROP & status tests
│   │   ├── test_optimization.py     # Knapsack budget constraint & MOQ tests
│   │   └── test_api.py              # End-to-end FastAPI endpoint integration tests
│   ├── requirements.txt             # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout with enterprise Navbar
│   │   ├── globals.css              # Custom styling & scrollbars
│   │   ├── page.tsx                 # Page A: Overview Dashboard
│   │   ├── forecasting/page.tsx     # Page B: Demand Forecasting Engine
│   │   ├── inventory/page.tsx       # Page C: Inventory Replenishment Planner
│   │   ├── stockout-risk/page.tsx   # Page D: Stockout Risk Center
│   │   ├── optimization/page.tsx    # Page E: Budget Optimizer
│   │   ├── simulator/page.tsx       # Page F: What-If Scenario Simulator
│   │   ├── data-management/page.tsx # Page G: Ingestion & Schema Hub
│   │   └── settings/page.tsx        # Page H: Reports & Platform Settings
│   ├── components/
│   │   ├── Navbar.tsx               # Enterprise top navigation & status pill
│   │   ├── KpiCard.tsx              # Telemetry metric cards
│   │   ├── StatusBadge.tsx          # Critical, Low Stock, Healthy, Overstocked badges
│   │   └── DemoBanner.tsx           # Synthetic simulation disclosure & reset control
│   ├── lib/
│   │   └── api.ts                   # Centralized typed API client
│   ├── types/
│   │   └── index.ts                 # TypeScript data contracts
│   └── package.json                 # Next.js & React dependencies
├── docs/
│   ├── architecture.md              # Technical architecture documentation
│   └── model_evaluation_report.md   # Model validation benchmarks report
├── .env.example                     # Environment template
└── README.md                        # Master documentation
```

---

## 4. Prerequisites & Installation

### Prerequisites
- **Python**: Version 3.10+ (tested on Python 3.14.0)
- **Node.js**: Version 18+ (tested on Node v24.12.0 with npm 11.6.2)
- **Operating System**: Windows (PowerShell), macOS, or Linux

### Installation (Windows PowerShell)

#### 1. Clone or Open Workspace
```powershell
cd "c:\Users\NC\Desktop\DEMANDSENSE AI"
```

#### 2. Backend Setup
```powershell
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install backend dependencies
python -m pip install -r backend/requirements.txt
```

#### 3. Frontend Setup
```powershell
cd frontend
npm install
cd ..
```

---

## 5. Execution Commands

### Run the FastAPI Backend Server
```powershell
# From project root with venv activated:
.\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000/api/v1`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

### Run the Next.js Frontend Application
In a second PowerShell terminal:
```powershell
cd "c:\Users\NC\Desktop\DEMANDSENSE AI\frontend"
npm run dev
```
Open **`http://localhost:3000`** in any web browser.

---

## 6. Running the Test Suites

### Backend Unit & Integration Tests (Pytest)
```powershell
.\venv\Scripts\pytest -v backend/tests
```
**Test Results**: 23 passed in 13.14s:
- `test_ingestion.py`: Fuzzy column recognition, date validation, negative clipping, deduplication, synthetic dataset generation.
- `test_forecasting.py`: Time-series lookahead leakage safeguards, WAPE/MAE/RMSE/zero-safe MAPE, multi-step recursive forecasting, model tournament selection.
- `test_inventory.py`: Lead-time demand, normal CDF Z-score, safety stock, reorder point, MOQ/pack size multiples, status classification.
- `test_optimization.py`: Budget ceiling strict compliance, pack-size integer multiples, priority-weight ROI ranking, zero-budget edge cases.
- `test_api.py`: FastAPI endpoints for health, demo loading, catalog, inventory summaries, stockout alerts, forecasting, budget optimization, and what-if simulation.

### Frontend TypeScript Verification & Production Build
```powershell
cd frontend
npm run build
```
**Build Result**: Next.js 16 (Turbopack) successfully compiled and statically generated all 8 routes in 1.4s with 0 TypeScript or lint errors.

---

## 7. Data Ingestion & Canonical Schema

DemandSense AI supports both CSV and Excel (.xlsx) file uploads with automatic fuzzy column detection and manual column mapping overrides.

### Canonical Schema Fields
| Field Name | Type | Required | Description / Example |
| :--- | :--- | :--- | :--- |
| `date` | Date (YYYY-MM-DD) | **Yes** | Date of transaction or daily aggregate (e.g., `2026-03-15`) |
| `product_id` | String | **Yes** | Unique identifier or SKU (e.g., `PROD-EL-001`) |
| `units_sold` | Float / Int | **Yes** | Daily sales volume (clipped to &ge; 0) |
| `product_name` | String | No | Human-readable product name |
| `category` | String | No | Merchandise department (e.g., `Electronics`, `Apparel`) |
| `store_id` | String | No | Retail store or warehouse identifier |
| `unit_price` | Float | No | Retail selling price per unit |
| `unit_cost` | Float | No | Wholesale purchase cost per unit |
| `inventory_on_hand` | Float | No | Ending daily inventory units on shelf |
| `supplier_lead_time_days` | Integer | No | Supplier delivery time in days (defaults to 7) |
| `promotion` | Boolean (0/1) | No | Marketing promotion active indicator |
| `discount` | Float | No | Discount fraction (e.g., `0.15` for 15% off) |
| `stockout_indicator` | Boolean (0/1) | No | Out-of-stock event flag |

### Deterministic Synthetic Demo Dataset
If starting on a blank database, the platform automatically generates and populates a realistic synthetic retail dataset:
- **Scope**: 15 distinct products across 4 categories (`Electronics`, `Apparel`, `Grocery`, `Home Goods`) across 2 store locations.
- **Horizon**: 180 consecutive days (6 months of daily transactions).
- **Patterns**: Day-of-week seasonality (weekend lift), promotion events (+60% demand spikes), supplier replenishment cycles, and simulated stockouts where zero inventory clipped sales.
- **Disclosures**: Explicitly tagged with `is_demo=True` and displayed with a persistent disclosure banner.

---

## 8. Demand Forecasting Methodology

DemandSense AI generates forecasts across 7, 14, 30, and 60-day horizons.

### Strict Anti-Leakage Feature Engineering
To prevent future lookahead data leakage:
- All lag features ($t-1, t-2, t-7, t-14, t-21, t-28$) are strictly backward-shifted.
- Rolling statistics ($7\text{d}, 14\text{d}, 28\text{d}$ mean and standard deviation) are computed over $t-1$ backwards, strictly excluding current and future targets.
- Calendar features: `day_of_week`, `is_weekend`, `day_of_month`, `month`, `week_of_year`.
- Multi-step horizon projections utilize an iterative autoregressive recursive forecasting loop.

### Candidate Models in Tournament
1. **Seasonal-Naive (7-Day)**: Baseline projecting the previous week's matching day-of-week demand ($y_t = y_{t-7}$).
2. **Moving Average (7-Day & 14-Day)**: Rolling window statistical baseline.
3. **Ridge Regression**: L2-regularized linear model with StandardScaler pipeline on calendar and lag features.
4. **Random Forest Regressor**: Ensemble tree estimator capturing non-linear feature interactions and promotion boosts.
5. **XGBoost Regressor**: High-performance gradient boosted decision trees.

### Model Evaluation & Holdout Validation
- **Chronological Split**: Strictly splits history into training ($T - 14$ days) and validation holdout (last 14 days). Never uses random train-test splitting.
- **Primary Metric**: **WAPE** (Weighted Absolute Percentage Error) = $\frac{\sum |y_i - \hat{y}_i|}{\sum y_i}$.
- **Secondary Metrics**: **MAE** = $\frac{1}{N}\sum |y_i - \hat{y}_i|$ and **RMSE** = $\sqrt{\frac{1}{N}\sum (y_i - \hat{y}_i)^2}$.
- **MAPE**: Calculated strictly on non-zero demand observations with documented limitation disclosures.
- **Uncertainty Bounds**: 95% confidence intervals estimated via empirical residual variance scaled by horizon time $\sqrt{h/7}$.

---

## 9. Inventory Optimization & Mathematical Policies

### Key Formulas
1. **Average Daily Demand ($\mu_d$)**:
   $$\mu_d = \frac{1}{N} \sum_{t=1}^N y_t$$

2. **Demand Standard Deviation ($\sigma_d$)**:
   $$\sigma_d = \sqrt{\frac{1}{N-1} \sum_{t=1}^N (y_t - \mu_d)^2}$$

3. **Expected Lead-Time Demand ($LTD$)**:
   $$LTD = L \times \mu_d$$
   where $L$ is supplier lead time in days.

4. **Safety Stock Buffer ($SS$)**:
   $$SS = Z \times \sigma_d \times \sqrt{L}$$
   where $Z = \Phi^{-1}(\text{Service Level})$ is calculated using the normal distribution inverse CDF (e.g., $Z = 1.645$ for 95% service level; $Z = 2.054$ for 98%).

5. **Reorder Point ($ROP$)**:
   $$ROP = LTD + SS = (L \times \mu_d) + (Z \times \sigma_d \times \sqrt{L})$$

6. **Recommended Order Quantity ($Q$)**:
   $$Q_{\text{net}} = \max(0, ROP - I_{\text{current}})$$
   If $Q_{\text{net}} > 0$:
   $$Q = \max(Q_{\text{net}} + 7\mu_d, \text{MOQ})$$
   $$Q_{\text{final}} = \left\lceil \frac{Q}{\text{Pack Size}} \right\rceil \times \text{Pack Size}$$

### Inventory Status Classifications
- **Critical**: Current stock $\le SS$ or days of coverage $\le$ supplier lead time $L$. Stockout is imminent before fresh supplier deliveries can arrive.
- **Low Stock**: $SS < \text{Current Stock} \le ROP$. Reorder threshold triggered.
- **Healthy**: $ROP < \text{Current Stock} \le ROP + 30\mu_d$. Optimal operating inventory window.
- **Overstocked**: $\text{Current Stock} > ROP + 45\mu_d$. Excess inventory tying up working capital.

---

## 10. Budget-Constrained Optimization

When total unconstrained replenishment demand exceeds the procurement budget ceiling:
- **Optimization Formulation**: Solves a Priority-Weighted Bounded Integer Knapsack Problem:
  $$\max \sum_{i} w_i \times \text{Allocated Units}_i \times \text{Urgency Factor}_i$$
  $$\text{subject to } \sum_{i} \text{Allocated Units}_i \times \text{Unit Cost}_i \le \text{Budget}$$
  $$\text{Allocated Units}_i = k_i \times \text{Pack Size}_i \quad (k_i \in \mathbb{Z}_{\ge 0})$$
  $$\text{Allocated Units}_i \ge \text{MOQ}_i \quad (\text{if } k_i > 0)$$
- **Priority Tiers**: High ($4\times$), Medium ($2\times$), Low ($1\times$), with an urgency boost for items in critical deficit.
- **Outputs**: Discrete pack-size order schedules, budget utilization %, remaining budget, and unmet replenishment demand.

---

## 11. What-If Scenario Simulator

Enables planners to stress-test inventory resiliency under hypothetical supply chain disruptions:
- **Demand Surge**: Modulate expected demand by $-50\%$ to $+100\%$.
- **Supplier Lead Time Delays**: Simulate supplier delays from $-3$ to $+14$ days.
- **Service Level Calibration**: Adjust SLA from $80\%$ to $99\%$.
- **Inventory Disruption**: Apply instantaneous $-50\%$ to $+50\%$ stock shocks.
- **Side-by-Side Impact**: Displays delta in replenishment capital, critical stockouts, and SKU-level status transitions without modifying baseline historical data.

---

## 12. Complete API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Health status and database connectivity |
| `POST` | `/api/v1/datasets/upload` | Upload CSV/XLSX file, detect columns, return preview |
| `POST` | `/api/v1/datasets/import` | Commit dataset with column mappings |
| `POST` | `/api/v1/datasets/load-demo` | Generate & load deterministic synthetic demo data |
| `GET` | `/api/v1/datasets/history` | List import audit trail |
| `GET` | `/api/v1/datasets/template` | Download sample CSV schema template |
| `GET` | `/api/v1/catalog/products` | List catalog products with current inventory |
| `GET` | `/api/v1/catalog/categories` | List distinct merchandise categories |
| `GET` | `/api/v1/catalog/stores` | List store locations |
| `POST` | `/api/v1/forecasting/forecast` | Run multi-model forecast with holdout validation |
| `GET` | `/api/v1/inventory/summary` | Get catalog inventory metrics, SS, ROP, orders |
| `GET` | `/api/v1/inventory/item/{id}` | Detailed calculation audit for single product |
| `GET` | `/api/v1/inventory/stockout-risk` | Stockout risk intelligence early warnings |
| `POST` | `/api/v1/optimization/budget-optimizer` | Run priority-weighted knapsack budget optimizer |
| `POST` | `/api/v1/scenarios/simulate` | Stress-test scenario simulator |
| `GET` | `/api/v1/analytics/dashboard-kpis` | Overview dashboard aggregate KPIs |
| `GET` | `/api/v1/analytics/demand-trend` | Daily aggregate units and revenue trend |
| `GET` | `/api/v1/analytics/category-distribution`| Category inventory health breakdown |
| `GET` | `/api/v1/analytics/urgent-actions` | Top priority stockout action items |
| `GET` | `/api/v1/reports/export/inventory-recommendations` | Export inventory plan (.CSV or .XLSX) |
| `GET` | `/api/v1/reports/export/forecast/{id}` | Export product forecast schedule (.CSV) |

---

## 13. Deployment Considerations

- **Frontend Hosting**: Deployable to Vercel, AWS Amplify, or Docker container with `npm run build` and `npm run start`. Configure `NEXT_PUBLIC_API_URL`.
- **Backend Hosting**: Deployable to AWS ECS/EC2, GCP Cloud Run, or Render via Uvicorn/Gunicorn. Set `DATABASE_URL` for PostgreSQL production instances.
- **Persistence**: SQLite is configured for local zero-dependency development. For production multi-worker deployments, set `DATABASE_URL=postgresql://user:password@host:5432/demandsense`.
- **File Storage**: Uploaded files and exports are sandboxed in `backend/data/` with UUID-prefixed path sanitization to prevent traversal attacks.

---

## 14. License

DemandSense AI is distributed under the MIT License.
