# Real-Time Fraud Detection System

A comprehensive, production-ready fraud detection system built with FastAPI, Kafka, and machine learning. This system provides low-latency transaction predictions and real-time feature engineering.

## Architecture Overview

The system is split into five main components:

### 1. **API Service** (`api_service/`)

- FastAPI application for low-latency transaction ingestion and predictions
- Endpoints: `/predict`, `/predict-batch`, `/predictions/{transaction_id}`, `/health`
- Real-time model inference with sub-100ms latency
- Integration with Kafka for event publishing

### 2. **Streaming Processor** (`streaming_processor/`)

- Real-time feature engineering using Kafka Streams or Faust
- Maintains customer state using Redis and TimescaleDB
- Computes rolling aggregations and time-window features
- Handles high-throughput transaction streams

### 3. **Model Training** (`model_training/`)

- Offline model development and retraining
- Jupyter notebooks for EDA and experimentation
- Automated training pipelines with model evaluation
- Supports multiple model types (XGBoost, LightGBM, Neural Networks)

### 4. **Monitoring** (`monitoring/`)

- Prometheus configuration for metrics collection
- Grafana dashboards for visualization
- Data drift detection using ADWIN algorithm
- Model performance monitoring and alerting

### 5. **Shared Libraries** (`shared_libs/`)

- Common Pydantic/SQLAlchemy models
- Utility functions and helpers
- ML utilities (SHAP explainer, threshold adaptation)
- Shared across all services

## Key Features

✅ **Low-Latency Predictions**: Sub-100ms inference using optimized models  
✅ **Real-Time Feature Engineering**: Streaming aggregations with Redis/TimescaleDB  
✅ **Adaptive Thresholds**: Dynamic fraud detection thresholds based on business costs  
✅ **Model Explainability**: SHAP-based feature importance explanations  
✅ **Drift Detection**: ADWIN algorithm for concept and data drift detection  
✅ **Production Ready**: Docker, monitoring, logging, error handling  
✅ **Scalable**: Kafka-based streaming, distributed processing

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- PostgreSQL / TimescaleDB
- Kafka
- Redis

### Installation

```bash
# Clone repository
git clone <repo-url>
cd fraud-detection-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/fraud_db
TIMESCALEDB_URL=postgresql://user:password@localhost/timescale_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Model
MODEL_PATH=./models/fraud_model.pkl
MODEL_VERSION=1.0.0
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### API Usage

#### Single Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_123456",
    "customer_id": "cust_789",
    "amount": 99.99,
    "merchant_id": "merchant_001",
    "country": "US"
  }'
```

Response:

```json
{
  "transaction_id": "txn_123456",
  "is_fraud": false,
  "fraud_probability": 0.12,
  "risk_level": "low",
  "explanation": {
    "method": "SHAP",
    "amount_contribution": 0.3,
    "merchant_contribution": 0.2
  },
  "model_version": "1.0.0"
}
```

#### Batch Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict-batch \
  -H "Content-Type: application/json" \
  -d '[...]'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

## Model Training

### Prepare Training Data

```bash
# Format: CSV with columns: transaction_id, customer_id, amount, merchant_id, is_fraud, ...
```

### Train Model

```bash
python model_training/scripts/train_model.py \
  data/transactions.csv \
  models/fraud_model.pkl \
  xgboost
```

### Evaluate Model

The training pipeline automatically evaluates on test set and generates metrics.

## Monitoring

### Prometheus Metrics

Available at `http://localhost:9090`

### Grafana Dashboards

Available at `http://localhost:3000`

Dashboards include:

- API request latency and throughput
- Model predictions and fraud detection rate
- Data drift detection results
- System health metrics

### Drift Detection

Run drift detection script:

```bash
python monitoring/drift_detection.py --lookback 7d
```

## Testing

### Run Tests

```bash
# All tests
pytest

# API tests
pytest tests/api_tests/

# Streaming tests
pytest tests/streaming_tests/

# Unit tests
pytest tests/unit_tests/

# With coverage
pytest --cov=. tests/
```

## Project Structure

```
fraud-detection-system/
├── api_service/                    # FastAPI application
│   ├── app.py                      # Main entry point
│   ├── dependencies.py             # DB/Kafka/Model connections
│   ├── schemas.py                  # Request/response models
│   ├── routers/
│   │   └── prediction.py           # Prediction endpoints
│   └── services/
│       └── prediction_service.py   # Business logic
├── streaming_processor/            # Kafka streaming
│   ├── app.py                      # Stream processor entry point
│   ├── schemas.py                  # Stream data models
│   ├── processors/
│   │   └── feature_processor.py   # Feature engineering
│   └── state_stores/
│       └── state_store.py          # Redis/TimescaleDB management
├── model_training/                 # Model development
│   ├── pipelines.py               # Feature engineering for training
│   ├── notebooks/                 # Jupyter notebooks (EDA, experiments)
│   └── scripts/
│       └── train_model.py         # Training pipeline
├── monitoring/                     # Observability
│   ├── prometheus.yml             # Prometheus config
│   ├── drift_detection.py         # Drift detection
│   └── grafana_dashboards/        # Dashboard JSON files
├── shared_libs/                    # Common code
│   ├── models.py                  # Pydantic/SQLAlchemy models
│   ├── utils.py                   # Logging, env vars
│   └── ml_utils.py               # ML utilities (SHAP, threshold adaptation)
├── tests/                          # Test suite
│   ├── api_tests/                # API integration tests
│   ├── streaming_tests/          # Streaming processor tests
│   └── unit_tests/               # Unit tests
├── .env                            # Environment variables
├── .env.example                    # Example env file
├── docker-compose.yml             # Docker composition
├── Dockerfile.api                 # API service Dockerfile
├── Dockerfile.streaming           # Streaming processor Dockerfile
├── pyproject.toml                 # Project metadata & dependencies
├── requirements.txt               # Python dependencies
└── README.md                       # This file
```

## Performance Characteristics

- **API Latency**: < 100ms p99 for single predictions
- **Throughput**: 10,000+ predictions/second (horizontal scaling possible)
- **Feature Latency**: < 1s from transaction ingestion to feature availability
- **Model Retraining**: Automatically triggered when drift detected
- **State Store**: Redis for real-time access, TimescaleDB for historical queries

## Security Considerations

- API authentication via API keys (implement as needed)
- Database connections use encrypted credentials
- Kafka SSL/TLS support
- Model serving with model validation
- Input validation and sanitization

## Troubleshooting

### Service Won't Start

1. Check environment variables in `.env`
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check Docker services are running: `docker ps`
4. Review logs: `docker-compose logs <service-name>`

### Predictions Taking Too Long

1. Check model file is loaded properly
2. Verify Redis connectivity for state access
3. Monitor system resources (CPU, memory)
4. Check for database connection issues

### High False Positive Rate

1. Review threshold settings in config
2. Run model retraining with latest data
3. Check for data drift using drift detection
4. Analyze prediction explanations (SHAP values)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:

- Check existing issues
- Review documentation in `/docs`
- Contact the team

---

Built with ❤️ for real-time fraud detection.
