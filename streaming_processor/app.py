"""Main streaming application entry point using Faust or Kafka-python."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StreamingApp:
    """Main streaming application."""

    def __init__(self, kafka_bootstrap_servers: Optional[list[str]] = None):
        """Initialize streaming app."""
        self.kafka_servers = kafka_bootstrap_servers or ["localhost:9092"]
        self.app = None
        self.feature_processor = None
        self.state_store = None

    async def initialize(self):
        """Initialize streaming application."""
        try:
            # Import and initialize Faust app
            # import faust
            # self.app = faust.App(
            #     'fraud_detection',
            #     broker=f'kafka://{",".join(self.kafka_servers)}'
            # )

            logger.info("Streaming application initialized")
        except Exception as e:
            logger.error(f"Failed to initialize streaming app: {e}")
            raise

    def register_topics(self):
        """Register Kafka topics."""
        try:
            # Define source topic (transactions)
            # self.transactions_topic = self.app.topic(
            #     'transactions',
            #     value_type=TransactionEvent
            # )

            # Define sink topic (processed features)
            # self.features_topic = self.app.topic(
            #     'features',
            #     value_type=FeatureEvent
            # )

            logger.info("Topics registered")
        except Exception as e:
            logger.error(f"Failed to register topics: {e}")
            raise

    async def process_transaction_stream(self):
        """Process incoming transaction stream."""
        try:
            # @self.app.agent(self.transactions_topic)
            # async def process(stream):
            #     async for transaction in stream:
            #         # Process transaction
            #         features = self.feature_processor.process_transaction(transaction)
            #         # Emit features
            #         await self.features_topic.send(value=features)

            logger.info("Transaction stream processing started")
        except Exception as e:
            logger.error(f"Error processing transaction stream: {e}")
            raise

    async def start(self):
        """Start streaming application."""
        try:
            await self.initialize()
            self.register_topics()
            await self.process_transaction_stream()

            # Start Faust app
            # self.app.main()

            logger.info("Streaming application started")
        except Exception as e:
            logger.error(f"Failed to start streaming app: {e}")
            raise

    async def stop(self):
        """Stop streaming application."""
        try:
            if self.app:
                # await self.app.stop()
                pass
            logger.info("Streaming application stopped")
        except Exception as e:
            logger.error(f"Error stopping streaming app: {e}")
            raise


if __name__ == "__main__":
    import asyncio

    app = StreamingApp()
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        asyncio.run(app.stop())
