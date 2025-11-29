"""
ML utilities including SHAP explainer setup and threshold adaptation logic.
"""
import logging
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ThresholdAdapter:
    """
    Adaptive threshold management for fraud detection model.
    
    Implements logic to dynamically adjust detection thresholds based on
    model performance and business requirements.
    """

    def __init__(self, base_threshold: float = 0.5):
        """Initialize threshold adapter."""
        self.base_threshold = base_threshold
        self.current_threshold = base_threshold
        self.history = []

    def update_threshold(
        self,
        fp_rate: float,
        fn_rate: float,
        business_cost_fp: float = 1.0,
        business_cost_fn: float = 10.0
    ) -> float:
        """
        Update threshold based on error rates and business costs.
        
        Args:
            fp_rate: False positive rate
            fn_rate: False negative rate
            business_cost_fp: Cost of false positive (inconveniencing customer)
            business_cost_fn: Cost of false negative (fraud loss)
            
        Returns:
            New threshold value
        """
        cost_ratio = business_cost_fn / business_cost_fp
        total_cost = (fp_rate * business_cost_fp) + (fn_rate * business_cost_fn)

        self.history.append({
            'threshold': self.current_threshold,
            'fp_rate': fp_rate,
            'fn_rate': fn_rate,
            'total_cost': total_cost
        })

        # Simple adjustment: increase threshold if too many false positives
        if fp_rate > 0.05 and fn_rate < 0.20:
            self.current_threshold = min(self.current_threshold + 0.05, 0.95)
        elif fn_rate > 0.20 and fp_rate < 0.02:
            self.current_threshold = max(self.current_threshold - 0.05, 0.05)

        logger.info(f"Threshold updated to {self.current_threshold}")
        return self.current_threshold

    def get_threshold(self) -> float:
        """Get current threshold."""
        return self.current_threshold

    def reset(self) -> None:
        """Reset to base threshold."""
        self.current_threshold = self.base_threshold
        self.history = []


class SHAPExplainer:
    """
    SHAP explainer wrapper for model interpretability.
    
    Provides unified interface for generating SHAP explanations.
    """

    def __init__(self, model: Any = None, explainer_type: str = "TreeExplainer"):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model to explain
            explainer_type: Type of explainer to use
        """
        self.model = model
        self.explainer_type = explainer_type
        self.explainer = None

        if model is not None:
            self._initialize_explainer()

    def _initialize_explainer(self) -> None:
        """Initialize the SHAP explainer."""
        try:
            import shap  # type: ignore

            if self.explainer_type == "TreeExplainer":
                self.explainer = shap.TreeExplainer(self.model)  # type: ignore
            elif self.explainer_type == "KernelExplainer":
                # Requires prediction function
                self.explainer = shap.KernelExplainer(  # type: ignore
                    self.model.predict,
                    shap.sample(np.random.randn(100, 10), 10)  # type: ignore
                )
            else:
                logger.warning(f"Unknown explainer type: {self.explainer_type}")
        except ImportError:
            logger.warning("SHAP not available. Install with: pip install shap")

    def explain_prediction(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Generate SHAP explanation for predictions.
        
        Args:
            X: Input features
            
        Returns:
            Dictionary containing SHAP values and metadata
        """
        if self.explainer is None:
            return {"error": "Explainer not initialized"}

        try:
            shap_values = self.explainer.shap_values(X)

            return {
                "shap_values": shap_values,
                "base_value": self.explainer.expected_value,
                "method": self.explainer_type
            }
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return {"error": str(e)}

    def get_feature_importance(self, X: np.ndarray) -> Dict[str, float]:
        """
        Calculate feature importance from SHAP values.
        
        Args:
            X: Input features
            
        Returns:
            Dictionary of feature importance scores
        """
        explanation = self.explain_prediction(X)
        if "error" in explanation:
            return {}

        shap_values = explanation["shap_values"]
        importance = np.abs(shap_values).mean(axis=0)

        return {f"feature_{i}": float(imp) for i, imp in enumerate(importance)}


class FeatureScaler:
    """Utility class for feature scaling and normalization."""

    def __init__(self, method: str = "standard"):
        """
        Initialize feature scaler.
        
        Args:
            method: Scaling method ("standard", "minmax", "robust")
        """
        self.method = method
        self.params = {}

    def fit(self, X: np.ndarray) -> None:
        """Fit scaler to data."""
        if self.method == "standard":
            self.params['mean'] = np.mean(X, axis=0)
            self.params['std'] = np.std(X, axis=0)
        elif self.method == "minmax":
            self.params['min'] = np.min(X, axis=0)
            self.params['max'] = np.max(X, axis=0)
        elif self.method == "robust":
            self.params['q1'] = np.percentile(X, 25, axis=0)
            self.params['q3'] = np.percentile(X, 75, axis=0)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data using fitted parameters."""
        if self.method == "standard":
            return (X - self.params['mean']) / (self.params['std'] + 1e-8)
        elif self.method == "minmax":
            return (X - self.params['min']) / (self.params['max'] - self.params['min'] + 1e-8)
        elif self.method == "robust":
            return (X - self.params['q1']) / (self.params['q3'] - self.params['q1'] + 1e-8)
        return X

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform data."""
        self.fit(X)
        return self.transform(X)


def calculate_model_metrics(
    y_true: List[int],
    y_pred: List[int],
    y_pred_proba: Optional[List[float]] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive model evaluation metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities (optional)
        
    Returns:
        Dictionary of metrics
    """
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
    }

    if y_pred_proba is not None:
        metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
    metrics['sensitivity'] = tp / (tp + fn) if (tp + fn) > 0 else 0

    return metrics
