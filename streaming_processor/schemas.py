"""Streaming processor data models and schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionEvent(BaseModel):
    """Transaction event from Kafka source."""
    transaction_id: str
    customer_id: str
    amount: float
    merchant_id: str
    timestamp: datetime
    merchant_category: Optional[str] = None
    country: Optional[str] = None
    ip_address: Optional[str] = None
    device_id: Optional[str] = None


class FeatureEvent(BaseModel):
    """Feature engineered event for model."""
    transaction_id: str
    customer_id: str
    features: dict
    computed_at: datetime
    window_duration: str  # e.g., "1h", "24h"


class AggregateEvent(BaseModel):
    """Aggregated customer metrics."""
    customer_id: str
    transaction_count_1h: int
    transaction_count_24h: int
    total_amount_1h: float
    total_amount_24h: float
    avg_transaction_amount: float
    unique_merchants_1h: int
    unique_merchants_24h: int
    aggregated_at: datetime
