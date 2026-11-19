"""Backend health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """GET /health returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    """GET / returns service info including health path."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Secure Open Source DevOps Platform"
    assert "/health" in body.values()
