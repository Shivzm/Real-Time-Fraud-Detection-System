"""
Shared Pydantic and SQLAlchemy models for the fraud detection system.

This module contains data models used across all services including Transaction,
FraudEvent, and other domain models.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(BaseModel):
    """Transaction request schema."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    customer_id: str = Field(..., description="Customer ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant_id: str = Field(..., description="Merchant ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    merchant_category: Optional[str] = None
    country: Optional[str] = None
    ip_address: Optional[str] = None
    device_id: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response schema with prediction."""
    transaction_id: str
    is_fraud: bool
    fraud_probability: float = Field(..., ge=0, le=1)
    risk_level: str  # "low", "medium", "high"
    explanation: Optional[dict] = None


class FraudEvent(BaseModel):
    """Fraud event schema."""
    transaction_id: str
    customer_id: str
    amount: float
    timestamp: datetime
    model_version: str
    fraud_probability: float
    detection_method: str  # "model", "rules", "hybrid"
    raw_features: Optional[dict] = None


class ModelMetadata(BaseModel):
    """Model metadata for versioning and tracking."""
    model_version: str
    model_type: str  # "xgboost", "lightgbm", "neural_network"
    training_date: datetime
    performance_metrics: Optional[dict] = None
    feature_names: Optional[list[str]] = None
    threshold: float = 0.5


class DataDrift(BaseModel):
    """Data drift detection result."""
    feature_name: str
    drift_detected: bool
    drift_score: float
    timestamp: datetime
    historical_mean: Optional[float] = None
    current_mean: Optional[float] = None


# SQLAlchemy ORM Models
class TransactionORM(Base):
    """Transaction ORM model."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    merchant_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_fraud = Column(Boolean, default=False)
    fraud_probability = Column(Float, default=None)
    model_version = Column(String, default=None)


class FraudEventORM(Base):
    """Fraud event ORM model."""
    __tablename__ = "fraud_events"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    detection_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    fraud_probability = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)
    detection_method = Column(String, nullable=False)
