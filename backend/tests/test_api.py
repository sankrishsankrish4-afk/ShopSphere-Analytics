from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_recommendations_shape():
    response = client.post("/api/recommendations", json={"cart_items": [1], "customer_id": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["product_id"] == 2
    assert {"product_id", "name", "confidence", "lift", "reason"}.issubset(payload[0])


def test_rules_filters_shape():
    response = client.get("/api/rules?algorithm=apriori&min_lift=1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["rules"][0]["algorithm"] == "apriori"
