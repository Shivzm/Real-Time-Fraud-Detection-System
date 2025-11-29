"""Main entry point for the fraud detection system."""
import asyncio
import logging

from api_service.dependencies import DependencyContainer

logger = logging.getLogger(__name__)


async def initialize_system():
    """Initialize the entire fraud detection system."""
    try:
        logger.info("Initializing Fraud Detection System...")

        # Initialize API dependencies
        container = DependencyContainer.get_instance()
        await container.initialize(
            db_connection_string="postgresql://fraud_user:fraud_password@localhost/fraud_db",
            kafka_servers=["localhost:9092"],
            model_path="./models/fraud_model.pkl"
        )

        logger.info("System initialization complete")
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        raise


async def shutdown_system():
    """Shutdown the fraud detection system."""
    try:
        logger.info("Shutting down Fraud Detection System...")

        container = DependencyContainer.get_instance()
        await container.shutdown()

        logger.info("System shutdown complete")
    except Exception as e:
        logger.error(f"System shutdown error: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Initialize system
        asyncio.run(initialize_system())

        # System is ready - can run services
        logger.info("Fraud Detection System ready for use")

        # Keep running
        asyncio.run(asyncio.sleep(float('inf')))

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    finally:
        # Cleanup
        asyncio.run(shutdown_system())
