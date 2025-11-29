"""Model training tests."""
import numpy as np


class TestFeatureEngineeringPipeline:
    """Test feature engineering pipeline."""

    def test_feature_names(self):
        """Test feature name list."""
        from model_training.pipelines import FeatureEngineeringPipeline

        pipeline = FeatureEngineeringPipeline()
        assert len(pipeline.feature_names) > 0
        assert "transaction_amount" in pipeline.feature_names


class TestModelTrainer:
    """Test model training."""

    def test_trainer_initialization(self):
        """Test model trainer initialization."""
        from model_training.scripts.train_model import ModelTrainer

        trainer = ModelTrainer(model_type="logistic_regression")
        assert trainer.model_type == "logistic_regression"
        assert trainer.model is None

    def test_model_training(self):
        """Test model training with dummy data."""
        from model_training.scripts.train_model import ModelTrainer

        trainer = ModelTrainer(model_type="logistic_regression")

        # Generate dummy data
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, 100)

        result = trainer.train(X_train, y_train)
        assert result["status"] == "success"
        assert trainer.model is not None

    def test_model_evaluation(self):
        """Test model evaluation."""
        from model_training.scripts.train_model import ModelTrainer

        trainer = ModelTrainer(model_type="logistic_regression")

        # Train on dummy data
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, 100)
        trainer.train(X_train, y_train)

        # Evaluate
        X_test = np.random.randn(20, 10)
        y_test = np.random.randint(0, 2, 20)

        metrics = trainer.evaluate(X_test, y_test)
        assert "accuracy" in metrics
        assert 0 <= metrics["accuracy"] <= 1


class TestDataValidator:
    """Test data validation."""

    def test_data_validation(self):
        """Test data quality validation."""
        import pandas as pd

        from model_training.pipelines import DataValidator

        df = pd.DataFrame({
            "col1": [1, 2, None, 4],
            "col2": [5, 6, 7, 8]
        })

        results = DataValidator.validate_data_quality(df)
        assert "null_counts" in results
        assert results["total_rows"] == 4

    def test_missing_value_handling(self):
        """Test missing value handling."""
        import pandas as pd

        from model_training.pipelines import DataValidator

        df = pd.DataFrame({
            "col1": [1.0, 2.0, np.nan, 4.0],
            "col2": [5.0, 6.0, 7.0, 8.0]
        })

        df_filled = DataValidator.handle_missing_values(df, strategy="mean")
        assert df_filled.isnull().sum().sum() == 0
