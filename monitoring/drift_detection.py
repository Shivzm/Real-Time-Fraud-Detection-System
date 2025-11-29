"""Data drift detection using ADWIN algorithm."""
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ADWIN:
    """
    Adaptive Windowing algorithm for drift detection.
    
    Detects concept drift in streaming data by maintaining a sliding window
    and comparing statistics of different parts of the window.
    """

    def __init__(self, delta: float = 0.002, min_window_size: int = 10):
        """
        Initialize ADWIN detector.
        
        Args:
            delta: Significance level for change detection
            min_window_size: Minimum window size to maintain
        """
        self.delta = delta
        self.min_window_size = min_window_size
        self.window = deque()
        self.width = 0
        self.variance_sum = 0.0
        self.total_sum = 0.0

    def add_element(self, value: float) -> bool:
        """
        Add new element and check for drift.
        
        Args:
            value: New value to add
            
        Returns:
            True if drift detected, False otherwise
        """
        self.window.append(value)
        self.width += 1
        self.total_sum += value

        # Check for drift
        if self.width > self.min_window_size:
            # Split window into two parts
            n1 = self.width // 2
            n2 = self.width - n1

            # Calculate statistics for each part
            window_list = list(self.window)
            part1 = window_list[:n1]
            part2 = window_list[n1:]

            mean1 = np.mean(part1)
            mean2 = np.mean(part2)

            # Check for significant difference
            if self._detect_change(part1, part2, float(mean1), float(mean2)):
                # Remove old elements
                for _ in range(n1):
                    self.window.popleft()
                self.width = n2
                return True

        return False

    def _detect_change(self, part1: list, part2: list, mean1: float, mean2: float) -> bool:
        """Check if change is statistically significant."""
        n1 = len(part1)
        n2 = len(part2)

        if n1 < 1 or n2 < 1:
            return False

        # Calculate variance
        var1 = np.var(part1) if len(part1) > 1 else 0
        var2 = np.var(part2) if len(part2) > 1 else 0

        # Use Hoeffding bound for drift detection
        m = (n1 * n2) / (n1 + n2)
        epsilon = np.sqrt((1 / (2 * m)) * np.log(2 / self.delta))

        # Detect drift if means differ more than epsilon
        return abs(mean1 - mean2) > epsilon


class DriftDetector:
    """
    Comprehensive drift detection system for fraud detection models.
    """

    def __init__(self, features: List[str], window_size: int = 1000):
        """
        Initialize drift detector.
        
        Args:
            features: List of feature names to monitor
            window_size: Size of sliding window for tracking
        """
        self.features = features
        self.window_size = window_size
        self.detectors = {feat: ADWIN() for feat in features}
        self.drift_history = []
        self.feature_statistics = {feat: {"mean": 0, "std": 0} for feat in features}

    def check_drift(self, X: np.ndarray, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check for data drift in new data.
        
        Args:
            X: New data samples (batch or single)
            feature_names: Names of features (if different from initialization)
            
        Returns:
            Dictionary with drift detection results
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        drift_results = {
            "timestamp": datetime.utcnow(),
            "drifts_detected": [],
            "feature_stats": {}
        }

        # Process each feature
        for i, feature_name in enumerate(self.features):
            if feature_name not in self.detectors:
                self.detectors[feature_name] = ADWIN()

            # Add samples from this feature
            for sample in X[:, i]:
                is_drift = self.detectors[feature_name].add_element(float(sample))

                if is_drift:
                    drift_results["drifts_detected"].append({
                        "feature": feature_name,
                        "timestamp": datetime.utcnow()
                    })
                    logger.warning(f"Drift detected in feature: {feature_name}")

            # Update statistics
            drift_results["feature_stats"][feature_name] = {
                "mean": np.mean(X[:, i]),
                "std": np.std(X[:, i]),
                "min": np.min(X[:, i]),
                "max": np.max(X[:, i])
            }

        # Log drift history
        if drift_results["drifts_detected"]:
            self.drift_history.append(drift_results)

        return drift_results

    def get_drift_report(self) -> Dict[str, Any]:
        """Generate comprehensive drift report."""
        return {
            "total_drift_events": len(self.drift_history),
            "recent_drifts": self.drift_history[-10:] if self.drift_history else [],
            "features_with_drift": list(set(
                drift["feature"] for event in self.drift_history
                for drift in event["drifts_detected"]
            ))
        }


class ModelDriftMonitor:
    """Monitor model performance drift."""

    def __init__(self, baseline_metrics: Dict[str, float]):
        """
        Initialize model drift monitor.
        
        Args:
            baseline_metrics: Baseline model performance metrics
        """
        self.baseline_metrics = baseline_metrics
        self.current_metrics = None
        self.metric_history = []

    def update_metrics(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Update current metrics and check for performance drift.
        
        Args:
            metrics: Current model metrics
            
        Returns:
            Drift detection results
        """
        self.current_metrics = metrics

        drift_detected = False
        degraded_metrics = []

        # Compare with baseline
        for metric_name, baseline_value in self.baseline_metrics.items():
            if metric_name in metrics:
                current_value = metrics[metric_name]

                # Allow 10% degradation
                threshold = baseline_value * 0.9 if baseline_value > 0 else 0

                if current_value < threshold:
                    drift_detected = True
                    degraded_metrics.append({
                        "metric": metric_name,
                        "baseline": baseline_value,
                        "current": current_value,
                        "degradation_pct": ((baseline_value - current_value) / baseline_value * 100)
                    })

        result = {
            "timestamp": datetime.utcnow(),
            "drift_detected": drift_detected,
            "degraded_metrics": degraded_metrics,
            "current_metrics": metrics
        }

        self.metric_history.append(result)

        if drift_detected:
            logger.warning(f"Model performance drift detected: {degraded_metrics}")

        return result

    def should_retrain(self) -> bool:
        """Determine if model should be retrained."""
        if not self.metric_history:
            return False

        # Retrain if 3 consecutive checks show degradation
        recent = self.metric_history[-3:]
        consecutive_drift = all(r["drift_detected"] for r in recent)

        return consecutive_drift
