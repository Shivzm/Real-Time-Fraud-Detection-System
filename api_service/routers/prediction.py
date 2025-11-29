"""API endpoint routes for fraud prediction."""
import time

from fastapi import APIRouter, Depends, HTTPException

from api_service.schemas import PredictionRequest, PredictionResponse
from api_service.services.prediction_service import PredictionService

router = APIRouter(prefix="/api/v1", tags=["predictions"])


@router.post("/predict", response_model=PredictionResponse)
async def predict_fraud(
    request: PredictionRequest,
    service: PredictionService = Depends()
) -> PredictionResponse:
    """
    Predict if a transaction is fraudulent.
    
    Args:
        request: Transaction details for prediction
        service: Prediction service dependency
        
    Returns:
        Prediction response with fraud probability and explanation
    """
    try:
        start_time = time.time()
        prediction = await service.predict(request)
        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        prediction.processing_time_ms = processing_time
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-batch")
async def predict_batch(
    requests: list[PredictionRequest],
    service: PredictionService = Depends()
) -> dict:
    """
    Batch prediction for multiple transactions.
    
    Args:
        requests: List of transaction details
        service: Prediction service dependency
        
    Returns:
        Dictionary with predictions and statistics
    """
    try:
        predictions = []
        for request in requests:
            prediction = await service.predict(request)
            predictions.append(prediction)

        fraud_count = sum(1 for p in predictions if p.is_fraud)
        return {
            "predictions": predictions,
            "total": len(predictions),
            "fraud_count": fraud_count,
            "fraud_rate": fraud_count / len(predictions) if predictions else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{transaction_id}")
async def get_prediction(
    transaction_id: str,
    service: PredictionService = Depends()
) -> dict:
    """
    Retrieve prediction history for a transaction.
    
    Args:
        transaction_id: Transaction ID to look up
        service: Prediction service dependency
        
    Returns:
        Prediction history
    """
    try:
        history = await service.get_prediction_history(transaction_id)
        if not history:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return {"transaction_id": transaction_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
