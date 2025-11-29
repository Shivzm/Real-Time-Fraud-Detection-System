"""Main FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api_service.dependencies import DependencyContainer
from api_service.routers import prediction
from api_service.schemas import HealthStatusResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: startup and shutdown."""
    # Startup
    logger.info("Starting Fraud Detection API Service")
    try:
        container = DependencyContainer.get_instance()
        await container.initialize(
            db_connection_string="postgresql://localhost/fraud_db",
            kafka_servers=["localhost:9092"],
            model_path="./models/fraud_model.pkl"
        )
    except Exception as e:
        logger.error(f"Failed to initialize dependencies: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Fraud Detection API Service")
    try:
        await container.shutdown()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="Low-latency transaction prediction and fraud detection endpoint",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prediction.router)


@app.get("/health", response_model=HealthStatusResponse)
async def health_check() -> HealthStatusResponse:
    """Health check endpoint."""
    return HealthStatusResponse(
        status="healthy",
        service="fraud-detection-api",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real-Time Fraud Detection API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_service.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
