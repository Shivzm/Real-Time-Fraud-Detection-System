"""Automated training and evaluation pipeline."""
import logging
import pickle
from datetime import datetime
from typing import Any, Dict

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train fraud detection models."""

    def __init__(self, model_type: str = "xgboost"):
        """
        Initialize model trainer.
        
        Args:
            model_type: Type of model to train
        """
        self.model_type = model_type
        self.model = None
        self.training_history = None

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train model on provided data.
        
        Args:
            X_train: Training features
            y_train: Training labels
            **kwargs: Model-specific hyperparameters
            
        Returns:
            Training results dictionary
        """
        try:
            if self.model_type == "xgboost":
                self.model = self._train_xgboost(X_train, y_train, **kwargs)
            elif self.model_type == "lightgbm":
                self.model = self._train_lightgbm(X_train, y_train, **kwargs)
            elif self.model_type == "logistic_regression":
                self.model = self._train_logistic_regression(X_train, y_train, **kwargs)
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")

            logger.info(f"Model trained: {self.model_type}")
            return {
                "status": "success",
                "model_type": self.model_type,
                "training_date": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise

    def _train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs):
        """Train XGBoost model."""
        try:
            import xgboost as xgb

            params = {
                "objective": "binary:logistic",
                "max_depth": kwargs.get("max_depth", 6),
                "learning_rate": kwargs.get("learning_rate", 0.1),
                "n_estimators": kwargs.get("n_estimators", 100),
                "random_state": 42
            }

            model = xgb.XGBClassifier(**params)
            model.fit(X_train, y_train)

            return model
        except ImportError:
            logger.error("XGBoost not installed")
            raise

    def _train_lightgbm(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs):
        """Train LightGBM model."""
        try:
            import lightgbm as lgb

            params = {
                "objective": "binary",
                "max_depth": kwargs.get("max_depth", 6),
                "learning_rate": kwargs.get("learning_rate", 0.1),
                "n_estimators": kwargs.get("n_estimators", 100),
                "random_state": 42
            }

            model = lgb.LGBMClassifier(**params)
            model.fit(X_train, y_train)

            return model
        except ImportError:
            logger.error("LightGBM not installed")
            raise

    def _train_logistic_regression(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs):
        """Train Logistic Regression model."""
        from sklearn.linear_model import LogisticRegression

        params = {
            "max_iter": kwargs.get("max_iter", 1000),
            "random_state": 42
        }

        model = LogisticRegression(**params)
        model.fit(X_train, y_train)

        return model

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate model on test data.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Evaluation metrics
        """
        try:
            if self.model is None:
                raise RuntimeError("Model not trained")

            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]  # type: ignore

            metrics = {
                "accuracy": float((y_pred == y_test).mean()),  # type: ignore
                "classification_report": classification_report(y_test, y_pred, output_dict=True),  # type: ignore
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),  # type: ignore
            }

            # Add ROC-AUC if available
            try:
                from sklearn.metrics import roc_auc_score
                metrics["roc_auc"] = roc_auc_score(y_test, y_pred_proba)
            except:
                pass

            logger.info(f"Model evaluation complete. Accuracy: {metrics['accuracy']:.4f}")
            return metrics

        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            raise

    def save_model(self, path: str):
        """Save model to disk."""
        try:
            if self.model is None:
                raise RuntimeError("Model not trained")

            with open(path, 'wb') as f:
                pickle.dump(self.model, f)

            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Model save failed: {e}")
            raise

    def load_model(self, path: str):
        """Load model from disk."""
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)

            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise


def run_training_pipeline(
    data_path: str,
    output_model_path: str,
    model_type: str = "xgboost"
) -> Dict[str, Any]:
    """
    Run complete training pipeline.
    
    Args:
        data_path: Path to training data
        output_model_path: Path to save trained model
        model_type: Type of model to train
        
    Returns:
        Pipeline results
    """
    try:
        import pandas as pd

        from model_training.pipelines import FeatureEngineeringPipeline

        # Load data
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)

        # Engineer features
        logger.info("Engineering features")
        pipeline = FeatureEngineeringPipeline()
        df = pipeline.engineer_features(df)

        # Prepare training data
        logger.info("Preparing training data")
        X, y = pipeline.prepare_training_data(df)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train model
        logger.info(f"Training {model_type} model")
        trainer = ModelTrainer(model_type=model_type)
        train_results = trainer.train(X_train, y_train)

        # Evaluate model
        logger.info("Evaluating model")
        eval_results = trainer.evaluate(X_test, y_test)

        # Save model
        logger.info(f"Saving model to {output_model_path}")
        trainer.save_model(output_model_path)

        return {
            "status": "success",
            "training_results": train_results,
            "evaluation_results": eval_results,
            "model_path": output_model_path
        }

    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        raise


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 3:
        print("Usage: python train_model.py <data_path> <output_model_path> [model_type]")
        sys.exit(1)

    data_path = sys.argv[1]
    output_path = sys.argv[2]
    model_type = sys.argv[3] if len(sys.argv) > 3 else "xgboost"

    result = run_training_pipeline(data_path, output_path, model_type)
    print(f"Training completed: {result}")
