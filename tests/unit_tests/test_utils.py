"""Unit tests for utility functions."""
from datetime import datetime

import pytest

from shared_libs.utils import (
    dict_to_camelcase,
    dict_to_snakecase,
    format_timestamp,
    get_env_variable,
    setup_logging,
)


class TestLogging:
    """Test logging utilities."""

    def test_setup_logging(self):
        """Test logger setup."""
        logger = setup_logging("test_logger", "DEBUG")
        assert logger is not None
        assert logger.name == "test_logger"


class TestEnvironment:
    """Test environment utilities."""

    def test_get_env_variable(self):
        """Test getting environment variable."""
        import os
        os.environ["TEST_VAR"] = "test_value"

        value = get_env_variable("TEST_VAR")
        assert value == "test_value"

    def test_get_missing_env_variable(self):
        """Test getting missing environment variable."""
        value = get_env_variable("NONEXISTENT_VAR", default="default")
        assert value == "default"

    def test_required_env_variable(self):
        """Test required environment variable."""
        with pytest.raises(ValueError):
            get_env_variable("REQUIRED_MISSING", required=True)


class TestDateTimeUtils:
    """Test datetime utilities."""

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_timestamp(dt)
        assert "2024-01-15" in formatted

    def test_format_timestamp_default(self):
        """Test timestamp formatting with default time."""
        formatted = format_timestamp()
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestDictConversion:
    """Test dictionary conversion utilities."""

    def test_dict_to_camelcase(self):
        """Test snake_case to camelCase conversion."""
        snake_dict = {"transaction_id": 1, "customer_name": "John"}
        camel_dict = dict_to_camelcase(snake_dict)

        assert "transactionId" in camel_dict
        assert "customerName" in camel_dict

    def test_dict_to_snakecase(self):
        """Test camelCase to snake_case conversion."""
        camel_dict = {"transactionId": 1, "customerName": "John"}
        snake_dict = dict_to_snakecase(camel_dict)

        assert "transaction_id" in snake_dict
        assert "customer_name" in snake_dict
