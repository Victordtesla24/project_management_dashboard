"""Test configuration and fixtures."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest  # type: ignore

from dashboard import create_app
from dashboard.config import init_config


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return str(Path(__file__).parent.parent)


@pytest.fixture(scope="session")
def config_dir(project_root):
    """Get the configuration directory."""
    return os.path.join(project_root, "config")


@pytest.fixture(scope="session")
def metrics_dir(project_root):
    """Get the metrics directory."""
    return os.path.join(project_root, "metrics")


@pytest.fixture(scope="session")
def logs_dir(project_root):
    """Get the logs directory."""
    return os.path.join(project_root, "logs")


@pytest.fixture
def test_config(test_data_dir):
    """Create a test configuration file."""
    config_path = os.path.join(test_data_dir, "test_config.json")
    # Create test config directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    # Write test configuration
    import json

    test_config = {
        "metrics": {
            "collection_interval": 1,
            "enabled_metrics": ["cpu", "memory"],
            "thresholds": {"cpu": 80, "memory": 85, "disk": 90},
            "retention": {"days": 7, "max_datapoints": 1000},
            "alert_rules": [
                {
                    "metric": "cpu",
                    "threshold": 80,
                    "duration": 300,
                    "severity": "warning",
                },
            ],
            "aggregation": {"interval": 300, "functions": ["avg", "max", "min"]},
        },
        "websocket": {
            "host": "localhost",
            "port": 8766,
            "ssl": False,
        },  # Different port for tests
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "dashboard_test",
            "user": "test_user",
            "password": "test_password",
        },
        "logging": {
            "level": "DEBUG",
            "file": "test.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "ui": {
            "theme": "light",
            "refresh_interval": 10,
            "max_datapoints": 100,
            "layout": {"sidebar": True, "charts": ["cpu", "memory", "disk"]},
        },
    }
    with open(config_path, "w") as f:
        json.dump(test_config, f, indent=4)
    return config_path


@pytest.fixture
def app(test_config):
    """Create a test Flask application."""
    # Initialize config with test configuration
    init_config(test_config)
    # Create app with test config
    test_flask_config = {
        "TESTING": True,
        "SECRET_KEY": "test_key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    # Create app instance
    app = create_app(test_flask_config)
    # Ensure app context is available for tests
    ctx = app.app_context()
    ctx.push()
    yield app
    # Clean up
    ctx.pop()


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, test_data_dir):
    """Set up the test environment."""
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("TEST_DATA_DIR", test_data_dir)
    yield
