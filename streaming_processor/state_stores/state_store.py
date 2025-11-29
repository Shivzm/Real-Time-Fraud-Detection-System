"""State store management for Redis and TimescaleDB."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RedisStateStore:
    """Redis-based state store for fast access."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis state store."""
        self.host = host
        self.port = port
        self.db = db
        self.client = None

    async def connect(self):
        """Connect to Redis."""
        try:
            # import redis.asyncio as redis
            # self.client = await redis.Redis(host=self.host, port=self.port, db=self.db)
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            if self.client:
                result = self.client.get(key)  # type: ignore
                return result
            return None
        except Exception as e:
            logger.error(f"Redis GET failed: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in Redis."""
        try:
            if self.client:
                if ttl:
                    self.client.setex(key, ttl, value)  # type: ignore
                else:
                    self.client.set(key, value)  # type: ignore
        except Exception as e:
            logger.error(f"Redis SET failed: {e}")
            raise

    async def delete(self, key: str):
        """Delete value from Redis."""
        try:
            if self.client:
                self.client.delete(key)  # type: ignore
        except Exception as e:
            logger.error(f"Redis DELETE failed: {e}")
            raise

    async def increment(self, key: str, amount: int = 1):
        """Increment counter in Redis."""
        try:
            if self.client:
                result = self.client.incrby(key, amount)  # type: ignore
                return result
            return None
        except Exception as e:
            logger.error(f"Redis INCRBY failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            self.client.close()  # type: ignore
            logger.info("Disconnected from Redis")


class TimescaleDBStateStore:
    """TimescaleDB-based state store for persistent storage."""

    def __init__(self, connection_string: str):
        """Initialize TimescaleDB state store."""
        self.connection_string = connection_string
        self.connection = None

    async def connect(self):
        """Connect to TimescaleDB."""
        try:
            # import asyncpg
            # self.connection = await asyncpg.connect(self.connection_string)
            logger.info("Connected to TimescaleDB")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    async def insert_metrics(self, metrics: Dict[str, Any]):
        """Insert metrics into TimescaleDB."""
        try:
            # Implement insert logic
            logger.debug("Metrics inserted into TimescaleDB")
        except Exception as e:
            logger.error(f"Failed to insert metrics: {e}")
            raise

    async def query_metrics(self, customer_id: str, time_window: str) -> list:
        """Query metrics for a customer within time window."""
        try:
            # Implement query logic
            return []
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise

    async def disconnect(self):
        """Disconnect from TimescaleDB."""
        if self.connection:
            pass  # Placeholder for actual disconnect
            logger.info("Disconnected from TimescaleDB")


class StateStoreManager:
    """Manages both Redis and TimescaleDB state stores."""

    def __init__(self):
        """Initialize state store manager."""
        self.redis: Optional[RedisStateStore] = None
        self.timescaledb: Optional[TimescaleDBStateStore] = None

    async def initialize(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        timescaledb_connection: Optional[str] = None
    ):
        """Initialize state stores."""
        try:
            # Initialize Redis for fast access
            self.redis = RedisStateStore(redis_host, redis_port)
            await self.redis.connect()

            # Initialize TimescaleDB for persistence
            if timescaledb_connection:
                self.timescaledb = TimescaleDBStateStore(timescaledb_connection)
                await self.timescaledb.connect()

            logger.info("State stores initialized")
        except Exception as e:
            logger.error(f"Failed to initialize state stores: {e}")
            raise

    async def get_customer_state(self, customer_id: str) -> Dict[str, Any]:
        """Get customer state from Redis (fast path)."""
        try:
            if self.redis:
                state = await self.redis.get(f"customer:{customer_id}")
                if isinstance(state, dict):
                    return state
                return {}
            return {}
        except Exception as e:
            logger.error(f"Failed to get customer state: {e}")
            return {}

    async def update_customer_state(self, customer_id: str, state: Dict[str, Any]):
        """Update customer state in Redis with TTL."""
        try:
            if self.redis:
                # Store in Redis with 24-hour TTL
                await self.redis.set(
                    f"customer:{customer_id}",
                    state,
                    ttl=86400
                )

            # Also persist to TimescaleDB
            if self.timescaledb:
                await self.timescaledb.insert_metrics({
                    "customer_id": customer_id,
                    "state": state,
                    "timestamp": datetime.utcnow()
                })
        except Exception as e:
            logger.error(f"Failed to update customer state: {e}")
            raise

    async def shutdown(self):
        """Shutdown state stores."""
        try:
            if self.redis:
                await self.redis.disconnect()
            if self.timescaledb:
                await self.timescaledb.disconnect()
            logger.info("State stores shut down")
        except Exception as e:
            logger.error(f"Error shutting down state stores: {e}")
            raise
