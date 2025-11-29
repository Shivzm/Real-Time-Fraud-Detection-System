"""FastAPI application schemas for request/response models."""
from typing import Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request schema for fraud prediction."""
    transaction_id: str = Field(..., description="Unique transaction ID")
    customer_id: str = Field(..., description="Customer ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant_id: str = Field(..., description="Merchant ID")
    merchant_category: Optional[str] = None
    country: Optional[str] = None
    ip_address: Optional[str] = None
    device_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_123456",
                "customer_id": "cust_789",
                "amount": 99.99,
                "merchant_id": "merchant_001",
                "merchant_category": "grocery",
                "country": "US",
                "ip_address": "192.168.1.1",
                "device_id": "device_123"
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for fraud prediction."""
    transaction_id: str
    is_fraud: bool = Field(..., description="Fraud prediction (True/False)")
    fraud_probability: float = Field(..., ge=0, le=1, description="Fraud probability score")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    explanation: Optional[dict] = Field(None, description="Feature importance explanation")
    model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None


class HealthStatusResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    transaction_id: Optional[str] = None
