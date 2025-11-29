"""Business logic for fraud prediction service."""
import logging

from api_service.schemas import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for handling fraud predictions."""

    def __init__(
        self,
        model_manager = None,
        db = None,
        kafka = None
    ):
        """Initialize prediction service."""
        self.model_manager = model_manager
        self.db = db
        self.kafka = kafka

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        Make fraud prediction for a transaction.
        
        Args:
            request: Transaction details
            
        Returns:
            Prediction response with fraud probability
        """
        try:
            # Extract features from request
            features = self._extract_features(request)

            # Get model prediction
            fraud_probability = self.model_manager.predict(features)

            # Determine fraud classification and risk level
            is_fraud = fraud_probability > 0.5
            risk_level = self._get_risk_level(fraud_probability)

            # Generate explanation (feature importance)
            explanation = self._generate_explanation(request, fraud_probability)

            # Log prediction
            await self._log_prediction(request, fraud_probability, is_fraud)

            # Publish to Kafka for monitoring
            await self._publish_prediction_event(request, fraud_probability, is_fraud)

            return PredictionResponse(
                transaction_id=request.transaction_id,
                is_fraud=is_fraud,
                fraud_probability=float(fraud_probability),
                risk_level=risk_level,
                explanation=explanation,
                model_version=self.model_manager.model_version
            )

        except Exception as e:
            logger.error(f"Prediction failed for {request.transaction_id}: {e}")
            raise

    def _extract_features(self, request: PredictionRequest) -> list:
        """
        Extract and prepare features from request.
        
        Args:
            request: Transaction request
            
        Returns:
            Feature vector for model
        """
        # This should match the model's expected feature order
        features = [
            request.amount,
            # Add more features as needed based on model training
        ]
        return features

    def _get_risk_level(self, fraud_probability: float) -> str:
        """
        Determine risk level based on fraud probability.
        
        Args:
            fraud_probability: Fraud probability score
            
        Returns:
            Risk level string: "low", "medium", "high"
        """
        if fraud_probability < 0.3:
            return "low"
        elif fraud_probability < 0.7:
            return "medium"
        else:
            return "high"

    def _generate_explanation(
        self,
        request: PredictionRequest,
        fraud_probability: float
    ) -> dict:
        """
        Generate model explanation using SHAP or similar.
        
        Args:
            request: Transaction request
            fraud_probability: Fraud probability
            
        Returns:
            Dictionary with feature contributions
        """
        # Placeholder for SHAP integration
        explanation = {
            "method": "SHAP",
            "amount_contribution": 0.3,
            "merchant_contribution": 0.2,
            "customer_contribution": 0.15,
            "other_contribution": 0.35
        }
        return explanation

    async def _log_prediction(
        self,
        request: PredictionRequest,
        fraud_probability: float,
        is_fraud: bool
    ):
        """Log prediction to database."""
        try:
            # Implement database logging
            logger.info(
                f"Prediction logged: {request.transaction_id}, "
                f"fraud={is_fraud}, prob={fraud_probability:.4f}"
            )
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")

    async def _publish_prediction_event(
        self,
        request: PredictionRequest,
        fraud_probability: float,
        is_fraud: bool
    ):
        """Publish prediction event to Kafka for monitoring."""
        try:
            if self.kafka:
                event = {
                    "transaction_id": request.transaction_id,
                    "customer_id": request.customer_id,
                    "is_fraud": is_fraud,
                    "fraud_probability": float(fraud_probability),
                    "amount": request.amount,
                    "timestamp": request.timestamp
                }
                await self.kafka.send_message("fraud_predictions", event)
        except Exception as e:
            logger.error(f"Failed to publish prediction event: {e}")

    async def get_prediction_history(self, transaction_id: str) -> list:
        """
        Retrieve prediction history for a transaction.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            List of previous predictions
        """
        try:
            if self.db:
                # Implement database query
                history = []
                return history
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve prediction history: {e}")
            raise
