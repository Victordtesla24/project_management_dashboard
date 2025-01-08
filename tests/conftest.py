import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Any

import pytest
from dashboard.config import init_config


@pytest.fixture(autouse=True, scope="session")
def setup_test_config(tmp_path_factory):
    """Initialize test configuration."""
    # Create a temporary config file
    config_dir = tmp_path_factory.mktemp("config")
    config_file = config_dir / "test_config.json"
    test_config = {
            "metrics": {
                "collection_interval": 60,
                "retention_days": 7,
                "retention": {
                    "data": 30,
                    "logs": 7,
                    "reports": 90,
                    "days": 30,
                    "max_datapoints": 1000
                },
                "enabled_metrics": ["cpu", "memory", "disk"],
                "thresholds": {
                    "cpu": 80,
                    "memory": 90,
                    "disk": 85
                },
                "aggregation": {
                    "interval": 300,
                    "functions": ["avg", "max", "min"]
                },
                "alert_rules": [
                    {
                        "metric": "cpu",
                        "threshold": 80,
                        "duration": 300,
                        "severity": "warning"
                    },
                    {
                        "metric": "memory",
                        "threshold": 90,
                        "duration": 300,
                        "severity": "critical"
                    },
                    {
                        "metric": "disk",
                        "threshold": 85,
                        "duration": 600,
                        "severity": "warning"
                    }
                ]
            },
        "websocket": {
            "host": "localhost",
            "port": 8765,
            "ssl": False
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "dashboard_test",
            "user": "test_user",
            "password": "test_pass"
        },
        "logging": {
            "level": "INFO",
            "file": "test.log",
            "format": "%(asctime)s [%(levelname)s] %(message)s"
        },
        "ui": {
            "theme": "light",
            "refresh_interval": 5000,
            "max_datapoints": 100,
            "layout": {}
        }
    }
    
    # Write config to temporary file
    config_file.write_text(json.dumps(test_config))
    
    # Initialize config with temp file
    init_config(str(config_file))

@pytest.fixture
def mock_metrics() -> Dict[str, Any]:
    """Provide mock metrics data."""
    return {
        "system": {
            "cpu_usage": 45.5,
            "memory_usage": 60.2,
            "disk_usage": 75.8
        },
        "test": {
            "coverage": 85.5,
            "passing_tests": 95.0
        },
        "errors": {
            "error_count": 2,
            "error_rate": 0.5
        }
    }

@pytest.fixture
def mock_session_state():
    """Provide mock session state."""
    state = SimpleNamespace()
    state.metrics_history = []
    state.last_update = None
    return state

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "app": {
            "debug": True,
            "secret_key": "test-key"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_pass"
        }
    }

@pytest.fixture
def temp_dir():
    """Provide temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data():
    return {
        "metrics": {"cpu_usage": 45.2, "memory_usage": 78.5, "disk_usage": 62.1},
        "tests": {"total": 150, "passed": 142, "failed": 8},
        "coverage": {"lines": 85.4, "branches": 78.9, "functions": 92.3},
    }


@pytest.fixture(scope="function")
def temp_test_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
