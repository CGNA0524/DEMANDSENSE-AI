import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "DemandSense" in data["project"]

def test_load_demo_data_endpoint():
    response = client.post("/api/v1/datasets/load-demo")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["valid_rows"] > 500

def test_products_list_endpoint():
    response = client.get("/api/v1/catalog/products")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]) >= 10
    assert "product_id" in res["data"][0]

def test_dashboard_kpis_endpoint():
    response = client.get("/api/v1/analytics/dashboard-kpis")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["total_products"] > 0
    assert res["data"]["total_inventory_value"] > 0

def test_inventory_summary_endpoint():
    response = client.get("/api/v1/inventory/summary?service_level=0.95")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]["items"]) > 0
    first_item = res["data"]["items"][0]
    assert "safety_stock" in first_item
    assert "reorder_point" in first_item

def test_stockout_risk_endpoint():
    response = client.get("/api/v1/inventory/stockout-risk")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]) > 0
    assert "risk_score" in res["data"][0]

def test_forecast_endpoint():
    # Fetch a product first
    prods = client.get("/api/v1/catalog/products").json()["data"]
    target_pid = prods[0]["product_id"]

    response = client.post("/api/v1/forecasting/forecast", json={
        "product_id": target_pid,
        "horizon_days": 14,
        "selected_model": "AUTO"
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]["forecast_points"]) == 14
    assert len(res["data"]["validation_metrics"]) > 0

def test_budget_optimizer_endpoint():
    response = client.post("/api/v1/optimization/budget-optimizer", json={
        "budget": 20000.0,
        "service_level": 0.95
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["allocated_cost"] <= 20000.0

def test_scenario_simulate_endpoint():
    response = client.post("/api/v1/scenarios/simulate", json={
        "name": "Supply Chain Disruption",
        "demand_multiplier": 1.25,
        "lead_time_change_days": 4,
        "service_level": 0.98,
        "budget": 40000.0,
        "inventory_shock_pct": -0.15
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]["metric_comparisons"]) > 0
