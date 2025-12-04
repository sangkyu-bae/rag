"""Basic health check endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok_status() -> None:
    """Ensure the health endpoint returns a successful status payload."""
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

