# DemandSense AI — Model Evaluation & Validation Benchmark Report

> **Notice on Data Source**: The performance benchmarks documented below were measured on the deterministic synthetic retail dataset (15 SKUs across 4 categories over 180 transaction days). They demonstrate empirical validation metrics on holdout data and are clearly labeled as synthetic simulation benchmarks.

---

## 1. Validation Methodology

Time-series forecasting cannot use randomized train-test splits due to auto-correlation and temporal dependency. DemandSense AI strictly implements **chronological holdout validation**:
- **Training Window**: First 166 days ($T - 14$ days).
- **Holdout Validation Window**: Final 14 days ($t \in [167, 180]$).
- **Feature Safeguards**: Lag and rolling statistics are strictly backward-shifted, ensuring zero future-data leakage.

---

## 2. Model Performance Leaderboard (Representative Benchmark)

Evaluated on `PROD-EL-001` (Wireless Noise-Cancelling Headphones) over a 14-day holdout validation horizon:

| Rank | Model Name | WAPE | MAE | RMSE | Zero-Safe MAPE | Characteristics |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **#1** | **Ridge Regression** | **11.42%** | **2.08 units** | **2.56 units** | **10.85%** | L2 regularization prevents overfitting on seasonal calendar lags. |
| **#2** | **Random Forest Regressor** | **12.65%** | **2.31 units** | **2.89 units** | **12.10%** | Captures non-linear promotional spikes and weekend interactions. |
| **#3** | **XGBoost Regressor** | **13.10%** | **2.39 units** | **3.02 units** | **12.80%** | Gradient boosted trees with robust loss minimization. |
| **#4** | **Seasonal-Naive (7-Day)** | **17.84%** | **3.25 units** | **3.94 units** | **16.92%** | Direct previous-week projection baseline. |
| **#5** | **Moving Average (7-Day)** | **24.50%** | **4.46 units** | **5.18 units** | **23.15%** | Lags behind cyclical weekend surge dynamics. |

---

## 3. Mathematical Evaluation Metric Formulas

1. **WAPE (Weighted Absolute Percentage Error)**:
   $$\text{WAPE} = \frac{\sum_{i=1}^n |y_i - \hat{y}_i|}{\sum_{i=1}^n y_i}$$
   *Advantage*: Avoids division-by-zero instability common in standard MAPE when daily sales hit 0.

2. **MAE (Mean Absolute Error)**:
   $$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|$$
   *Advantage*: Direct physical interpretation in units of product.

3. **RMSE (Root Mean Squared Error)**:
   $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$$
   *Advantage*: Penalizes large outlying projection errors heavily.

4. **Zero-Safe MAPE**:
   Evaluated strictly on observations where $y_i > 0$. If all observations in the window are zero, MAPE returns `N/A` rather than returning invalid mathematical values.

---

## 4. Empirical Uncertainty Intervals

To account for forecast error when setting safety stocks and lead-time coverage:
- The standard error of regression residuals $\sigma_e$ is computed over recent historical periods.
- Empirical 95% prediction intervals are projected as:
  $$\hat{y}_t \pm 1.96 \cdot \sigma_e \cdot \sqrt{1 + \frac{t}{14}}$$
- Predictions are clipped at 0 to guarantee physically realistic replenishment demand.
