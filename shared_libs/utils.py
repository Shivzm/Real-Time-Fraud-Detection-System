"""
Generic utility helpers for logging, configuration, and common operations.
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def setup_logging(
    name: str = "fraud_detection",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_env_variable(key: str, default: Any = None, required: bool = False) -> Any:
    """
    Get environment variable with optional defaults and validation.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Raise error if required but not found
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required variable is not found
    """
    value = os.getenv(key, default)
    if value is None and required:
        raise ValueError(f"Required environment variable '{key}' not found")
    return value


def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Path to .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    env_path = Path(env_file)

    if not env_path.exists():
        return env_vars

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')
                os.environ[key.strip()] = value.strip().strip('"\'')

    return env_vars


def format_timestamp(dt: Optional[datetime] = None, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object as string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime(format)


def parse_timestamp(ts_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse timestamp string to datetime object."""
    return datetime.strptime(ts_str, format)


def dict_to_camelcase(snake_dict: Dict) -> Dict:
    """Convert snake_case keys to camelCase."""
    camel_dict = {}
    for key, value in snake_dict.items():
        parts = key.split('_')
        camel_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
        camel_dict[camel_key] = value
    return camel_dict


def dict_to_snakecase(camel_dict: Dict) -> Dict:
    """Convert camelCase keys to snake_case."""
    import re
    snake_dict = {}
    for key, value in camel_dict.items():
        snake_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        snake_dict[snake_key] = value
    return snake_dict
