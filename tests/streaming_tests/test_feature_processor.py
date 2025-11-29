"""Streaming processor tests."""
import pytest

from streaming_processor.processors.feature_processor import FeatureProcessor


@pytest.fixture
def feature_processor():
    """Create feature processor instance."""
    return FeatureProcessor()


class TestFeatureProcessor:
    """Test feature processor."""

    def test_process_transaction(self, feature_processor):
        """Test transaction processing."""
        transaction = {
            "transaction_id": "txn_001",
            "customer_id": "cust_001",
            "amount": 100.0,
            "merchant_id": "merch_001",
            "timestamp": None,
            "country": "US"
        }

        features = feature_processor.process_transaction(transaction)
        assert isinstance(features, dict)
        assert "transaction_amount" in features

    def test_time_window_features(self, feature_processor):
        """Test time window feature extraction."""
        customer_id = "cust_001"

        # Add multiple transactions
        for i in range(5):
            transaction = {
                "transaction_id": f"txn_{i}",
                "customer_id": customer_id,
                "amount": 50.0 + i,
                "merchant_id": f"merch_{i}",
                "timestamp": None
            }
            feature_processor.process_transaction(transaction)

        # Verify state is maintained
        profile = feature_processor.get_customer_profile(customer_id)
        assert profile["transaction_count"] == 5

    def test_geographic_risk_calculation(self, feature_processor):
        """Test geographic risk scoring."""
        transaction_us = {
            "transaction_id": "txn_us",
            "customer_id": "cust_us",
            "amount": 100.0,
            "merchant_id": "merch",
            "country": "US"
        }

        features = feature_processor.process_transaction(transaction_us)
        assert 0 <= features["geographic_risk_score"] <= 1


class TestStateManagement:
    """Test state management."""

    def test_customer_state_update(self, feature_processor):
        """Test customer state updates."""
        customer_id = "cust_state_test"

        transaction = {
            "transaction_id": "txn_state",
            "customer_id": customer_id,
            "amount": 75.0,
            "merchant_id": "merch",
            "timestamp": None
        }

        feature_processor.process_transaction(transaction)
        profile = feature_processor.get_customer_profile(customer_id)

        assert profile["customer_id"] == customer_id
        assert profile["transaction_count"] >= 1
