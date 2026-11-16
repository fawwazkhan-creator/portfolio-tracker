from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.config import Settings
from app.db import Base
from app.main import create_app

from .conftest import add


def test_health_reports_database_and_cache(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up", "cache": "up"}
    assert response.headers["X-Request-ID"]


def test_create_and_list_transactions_normalises_symbol(client: TestClient):
    created = add(client, " aapl ", "buy", "10", "100.25", "2025-01-02", fee="1.5")
    assert created.status_code == 201
    body = created.json()
    assert body["symbol"] == "AAPL"
    assert body["price"] == "100.2500"
    listed = client.get("/api/transactions").json()
    assert [t["id"] for t in listed] == [body["id"]]


def test_rejects_sale_larger_than_holding(client: TestClient):
    add(client, "NVDA", "buy", "5", "100", "2025-01-02")
    response = add(client, "NVDA", "sell", "6", "120", "2025-02-02")
    assert response.status_code == 422
    assert "only 5 held" in response.json()["detail"]


def test_rejects_future_dates_and_bad_input(client: TestClient):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert add(client, "AAPL", "buy", "1", "10", tomorrow).status_code == 422
    assert add(client, "AAPL", "hold", "1", "10", "2025-01-01").status_code == 422
    assert add(client, "AAPL", "buy", "-1", "10", "2025-01-01").status_code == 422
    assert add(client, "BAD SYMBOL!", "buy", "1", "10", "2025-01-01").status_code == 422


def test_deleting_a_buy_that_a_later_sale_depends_on_is_blocked(client: TestClient):
    buy = add(client, "MSFT", "buy", "5", "300", "2025-01-02").json()
    add(client, "MSFT", "sell", "5", "320", "2025-02-02")
    response = client.delete(f"/api/transactions/{buy['id']}")
    assert response.status_code == 409
    assert client.delete("/api/transactions/9999").status_code == 404


def test_positions_and_summary_use_latest_price(client: TestClient):
    add(client, "AAPL", "buy", "10", "100", "2025-01-02")
    add(client, "AAPL", "sell", "4", "150", "2025-02-02")
    assert client.put("/api/prices/aapl", json={"price": "90"}).status_code == 200

    positions = client.get("/api/positions").json()
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["market_value"] == "540.00"

    summary = client.get("/api/summary").json()
    assert summary["realized_pl"] == "200.00"
    assert summary["unrealized_pl"] == "-60.00"
    assert summary["total_pl"] == "140.00"


def test_price_update_invalidates_cached_price(client: TestClient):
    add(client, "VOO", "buy", "1", "400", "2025-01-02")
    client.put("/api/prices/VOO", json={"price": "410"})
    assert client.get("/api/positions").json()[0]["market_price"] == "410.0000"
    client.put("/api/prices/VOO", json={"price": "420"})
    assert client.get("/api/positions").json()[0]["market_price"] == "420.0000"


def test_write_routes_require_api_key_when_configured(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'auth.db'}", api_key="s3cret-key")
    app = create_app(settings)
    Base.metadata.create_all(app.state.db.engine)
    with TestClient(app) as client:
        assert add(client, "AAPL", "buy", "1", "10", "2025-01-01").status_code == 401
        allowed = client.post(
            "/api/transactions",
            headers={"X-API-Key": "s3cret-key"},
            json={
                "symbol": "AAPL",
                "side": "buy",
                "quantity": "1",
                "price": "10",
                "executed_at": "2025-01-01",
            },
        )
        assert allowed.status_code == 201
        assert client.get("/api/summary").status_code == 200
