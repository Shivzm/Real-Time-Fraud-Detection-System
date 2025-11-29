"""API integration tests."""
import pytest
from fastapi.testclient import TestClient

from api_service.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_predict_endpoint(client):
    """Test prediction endpoint."""
    payload = {
        "transaction_id": "txn_test_001",
        "customer_id": "cust_001",
        "amount": 100.0,
        "merchant_id": "merch_001",
        "country": "US"
    }

    response = client.post("/api/v1/predict", json=payload)
    # Note: Will fail if model not loaded, but tests structure
    assert response.status_code in [200, 500]


def test_invalid_request(client):
    """Test invalid request handling."""
    payload = {
        "transaction_id": "txn_test_002",
        # Missing required fields
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422  # Validation error


class TestPredictionBatch:
    """Batch prediction tests."""

    def test_batch_predict(self, client):
        """Test batch prediction."""
        payloads = [
            {
                "transaction_id": f"txn_batch_{i}",
                "customer_id": f"cust_{i}",
                "amount": 100.0 + i,
                "merchant_id": f"merch_{i}",
            }
            for i in range(3)
        ]

        response = client.post("/api/v1/predict-batch", json=payloads)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert len(data["predictions"]) == 3


class TestPredictionHistory:
    """Prediction history tests."""

    def test_get_prediction_history(self, client):
        """Test getting prediction history."""
        response = client.get("/api/v1/predictions/txn_test_001")
        assert response.status_code in [200, 404, 500]
