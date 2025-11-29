"""Feature engineering pipelines for model training (must sync with streaming_processor)."""
import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureEngineeringPipeline:
    """
    Feature engineering pipeline for model training.
    
    Must remain synchronized with streaming_processor/processors/feature_processor.py
    """

    def __init__(self):
        """Initialize feature engineering pipeline."""
        self.feature_names = [
            "transaction_amount",
            "transaction_count_1h",
            "transaction_count_24h",
            "avg_amount_1h",
            "unique_merchants_1h",
            "transaction_velocity",
            "geographic_risk_score",
            "customer_account_age",
            "is_weekend",
            "is_night_time"
        ]
        self.scaler = None

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from raw transaction data.
        
        Args:
            df: Raw transaction dataframe
            
        Returns:
            Dataframe with engineered features
        """
        try:
            df = df.copy()

            # Time-based features
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6]).astype(int)
            df['is_night_time'] = (
                (df['timestamp'].dt.hour >= 22) |
                (df['timestamp'].dt.hour < 6)
            ).astype(int)

            # Customer age feature
            df['customer_account_age'] = (
                df['timestamp'] - df['customer_created_date']
            ).dt.days
            df['customer_account_age'] = df['customer_account_age'].clip(lower=0)

            # Time window aggregations
            df = self._add_time_window_features(df)

            # Geographic and merchant features
            df = self._add_categorical_features(df)

            logger.info(f"Features engineered: {df.shape[1]} features")
            return df

        except Exception as e:
            logger.error(f"Error engineering features: {e}")
            raise

    def _add_time_window_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time window aggregation features."""
        df['transaction_count_1h'] = 0
        df['transaction_count_24h'] = 0
        df['avg_amount_1h'] = 0
        df['unique_merchants_1h'] = 0

        # Group by customer and aggregate
        df = df.copy()
        for idx, row in df.iterrows():
            customer_id = row['customer_id']
            timestamp = row['timestamp']

            # 1-hour window
            mask_1h = (
                (df['customer_id'] == customer_id) &
                (df['timestamp'] >= timestamp - pd.Timedelta(hours=1)) &
                (df['timestamp'] <= timestamp)
            )
            df.loc[idx, 'transaction_count_1h'] = int(mask_1h.sum())  # type: ignore
            avg_amt = df.loc[mask_1h, 'amount'].mean()  # type: ignore
            df.loc[idx, 'avg_amount_1h'] = float(avg_amt) if pd.notna(avg_amt) else 0.0  # type: ignore
            unique_merch = df.loc[mask_1h, 'merchant_id'].nunique()  # type: ignore
            df.loc[idx, 'unique_merchants_1h'] = int(unique_merch) if pd.notna(unique_merch) else 0  # type: ignore

            # 24-hour window
            mask_24h = (
                (df['customer_id'] == customer_id) &
                (df['timestamp'] >= timestamp - pd.Timedelta(hours=24)) &
                (df['timestamp'] <= timestamp)
            )
            df.loc[idx, 'transaction_count_24h'] = int(mask_24h.sum())  # type: ignore

        return df

    def _add_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add categorical and geographic features."""
        # Geographic risk score
        high_risk_countries = {'XX', 'YY', 'ZZ'}
        df['geographic_risk_score'] = df['country'].apply(
            lambda x: 0.8 if x in high_risk_countries else (0.5 if pd.isna(x) else 0.2)
        )

        # Transaction velocity
        df['transaction_velocity'] = df.groupby('customer_id')['transaction_id'].transform('count')

        return df

    def prepare_training_data(
        self,
        df: pd.DataFrame,
        target_column: str = 'is_fraud'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for model training.
        
        Args:
            df: Engineered features dataframe
            target_column: Name of target column
            
        Returns:
            Tuple of (features, labels)
        """
        try:
            X = df[self.feature_names].values
            y = df[target_column].values.astype(np.float64)

            # Scale features
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(X)

            logger.info(f"Training data prepared: X.shape={X.shape}, y.shape={y.shape}")
            return X, y  # type: ignore

        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise


class DataValidator:
    """Validate data quality for training."""

    @staticmethod
    def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality metrics.
        
        Args:
            df: Dataframe to validate
            
        Returns:
            Dictionary of validation results
        """
        results = {
            "total_rows": len(df),
            "null_counts": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "columns": list(df.columns)
        }

        return results

    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = "mean") -> pd.DataFrame:
        """
        Handle missing values in dataframe.
        
        Args:
            df: Input dataframe
            strategy: Strategy to use ("mean", "median", "drop")
            
        Returns:
            Dataframe with missing values handled
        """
        df = df.copy()

        if strategy == "mean":
            df = df.fillna(df.mean())
        elif strategy == "median":
            df = df.fillna(df.median())
        elif strategy == "drop":
            df = df.dropna()

        return df

    @staticmethod
    def detect_outliers(df: pd.DataFrame, columns: Optional[list] = None, method: str = "iqr") -> pd.DataFrame:
        """
        Detect outliers in numeric columns.
        
        Args:
            df: Input dataframe
            columns: Columns to check (all numeric if None)
            method: Detection method ("iqr" or "zscore")
            
        Returns:
            Dataframe with outlier flag
        """
        df = df.copy()

        if columns is None:
            columns = list(df.select_dtypes(include=['number']).columns)  # type: ignore

        df['is_outlier'] = False

        if method == "iqr":
            for col in columns:  # type: ignore
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                df.loc[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR), 'is_outlier'] = True  # type: ignore

        elif method == "zscore":
            from scipy import stats
            for col in columns:  # type: ignore
                z_scores = np.abs(stats.zscore(df[col].dropna()))  # type: ignore
                df.loc[z_scores > 3, 'is_outlier'] = True  # type: ignore

        return df
