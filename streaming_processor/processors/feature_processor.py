"""Feature engineering processor for real-time stream."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class FeatureProcessor:
    """Processes transactions and engineers features."""

    def __init__(self):
        """Initialize feature processor."""
        self.state_store = {}
        self.feature_config = self._load_feature_config()

    def _load_feature_config(self) -> dict:
        """Load feature engineering configuration."""
        return {
            "time_windows": ["1h", "24h", "7d"],
            "aggregations": ["sum", "count", "avg", "min", "max"],
            "feature_names": [
                "transaction_amount",
                "transaction_count_1h",
                "transaction_count_24h",
                "avg_amount_1h",
                "unique_merchants_1h",
                "customer_age_days",
                "account_velocity",
                "geographic_risk_score"
            ]
        }

    def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a transaction and extract features.
        
        Args:
            transaction: Transaction data
            
        Returns:
            Dictionary of engineered features
        """
        try:
            customer_id: Optional[str] = transaction.get("customer_id")

            # Update state store with transaction
            if customer_id:
                self._update_customer_state(customer_id, transaction)
                # Extract features
                features = self._extract_features(customer_id, transaction)
                logger.debug(f"Features extracted for {transaction.get('transaction_id')}")
                return features
            else:
                logger.warning("Transaction missing customer_id")
                return {}

        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            raise

    def _update_customer_state(self, customer_id: Optional[str], transaction: Dict):
        """Update customer state with new transaction."""
        if customer_id not in self.state_store:
            self.state_store[customer_id] = {
                "transactions": [],
                "last_update": datetime.utcnow()
            }

        self.state_store[customer_id]["transactions"].append(transaction)
        self.state_store[customer_id]["last_update"] = datetime.utcnow()

        # Keep only recent transactions (last 7 days)
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        self.state_store[customer_id]["transactions"] = [
            t for t in self.state_store[customer_id]["transactions"]
            if t.get("timestamp", datetime.utcnow()) > cutoff_time
        ]

    def _extract_features(self, customer_id: Optional[str], transaction: Dict) -> Dict[str, Any]:
        """Extract features for a transaction."""
        if not customer_id:
            return {}
        features = {}

        # Transaction amount feature
        features["transaction_amount"] = transaction.get("amount", 0)

        # Time window aggregations
        features.update(self._calculate_time_window_features(customer_id))

        # Velocity features
        features["transaction_velocity"] = self._calculate_velocity(customer_id)

        # Geographic features
        features["geographic_risk_score"] = self._calculate_geographic_risk(transaction)

        return features

    def _calculate_time_window_features(self, customer_id: str) -> Dict[str, float]:
        """Calculate features based on time windows."""
        features = {}
        now = datetime.utcnow()

        if customer_id not in self.state_store:
            return {
                "transaction_count_1h": 0,
                "transaction_count_24h": 0,
                "avg_amount_1h": 0,
                "unique_merchants_1h": 0
            }

        transactions = self.state_store[customer_id]["transactions"]

        # 1-hour window
        one_hour_ago = now - timedelta(hours=1)
        txns_1h = [t for t in transactions if t.get("timestamp", now) > one_hour_ago]
        features["transaction_count_1h"] = len(txns_1h)
        features["avg_amount_1h"] = (
            sum(t.get("amount", 0) for t in txns_1h) / len(txns_1h)
            if txns_1h else 0
        )
        features["unique_merchants_1h"] = len(set(
            t.get("merchant_id") for t in txns_1h
        ))

        # 24-hour window
        one_day_ago = now - timedelta(days=1)
        txns_24h = [t for t in transactions if t.get("timestamp", now) > one_day_ago]
        features["transaction_count_24h"] = len(txns_24h)

        return features

    def _calculate_velocity(self, customer_id: str) -> float:
        """Calculate transaction velocity (transactions per hour)."""
        if customer_id not in self.state_store:
            return 0.0

        transactions = self.state_store[customer_id]["transactions"]
        if len(transactions) < 2:
            return 0.0

        first_tx_time = min(t.get("timestamp", datetime.utcnow()) for t in transactions)
        last_tx_time = max(t.get("timestamp", datetime.utcnow()) for t in transactions)

        hours_elapsed = max((last_tx_time - first_tx_time).total_seconds() / 3600, 0.01)
        velocity = len(transactions) / hours_elapsed

        return velocity

    def _calculate_geographic_risk(self, transaction: Dict) -> float:
        """Calculate geographic risk score."""
        # Simplified geographic risk calculation
        country = transaction.get("country", "")

        # High-risk countries (example)
        high_risk_countries = {"XX", "YY", "ZZ"}

        if country in high_risk_countries:
            return 0.8
        elif country == "":
            return 0.5  # Unknown country is medium risk
        else:
            return 0.2

    def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """Get customer profile from state."""
        if customer_id not in self.state_store:
            return {}

        state = self.state_store[customer_id]
        transactions = state.get("transactions", [])

        return {
            "customer_id": customer_id,
            "transaction_count": len(transactions),
            "total_amount": sum(t.get("amount", 0) for t in transactions),
            "last_transaction": state.get("last_update"),
            "unique_merchants": len(set(t.get("merchant_id") for t in transactions))
        }
