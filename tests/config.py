"""Test configuration."""

import os
from typing import Any, Dict

# Test database URL - using SQLite for testing
TEST_DB_URL = os.environ.get("TEST_DB_URL", "sqlite:///:memory:")

# Test configuration
TEST_CONFIG = {
    "database": {"url": TEST_DB_URL, "echo": False},
    "metrics": {"collection_interval": 60, "storage_path": "tests/data/metrics"},
    "monitor": {"enabled": True, "log_level": "INFO"},
}


# Test requirements
class Requirements:
    def __init__(self) -> None:
        self.python = ">=3.8"
        self.packages = {
            "sqlalchemy": ">=1.4.0",
            "pytest": ">=7.0.0",
            "numpy": ">=1.20.0",
            "psutil": ">=5.8.0",
            "streamlit": ">=1.0.0",
        }
        self.optional_packages = {
            "mypy": ">=0.900",
            "black": ">=21.0",
            "isort": ">=5.0.0",
            "flake8": ">=3.9.0",
        }

    def __getattr__(self, name):
        # Return a decorator function for feature flags
        def decorator(func):
            return func

        return decorator


requirements = Requirements()


def get_test_config() -> Dict[str, Any]:
    """Get test configuration with environment overrides."""
    config = TEST_CONFIG.copy()

    # Allow environment variables to override config
    if db_url := os.environ.get("TEST_DB_URL"):
        config["database"]["url"] = db_url

    if log_level := os.environ.get("TEST_LOG_LEVEL"):
        config["monitor"]["log_level"] = log_level

    return config


def get_requirements() -> Dict[str, Any]:
    """Get test requirements."""
    return requirements
