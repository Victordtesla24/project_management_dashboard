import json
import os
from unittest.mock import mock_open, patch

import pytest

from dashboard.config.config import (
    ConfigManager,
    ConfigurationError,
    get_alert_rules,
    get_config,
    init_config,
    update_alert_rules,
    update_config,
)
from dashboard.config.schema import SchemaValidationError


@pytest.fixture
def sample_config():
    """Sample configuration data."""
    return {
        "environment": "test",
        "metrics": {
            "collection_interval": 60,
            "enabled_metrics": ["cpu", "memory", "disk"],
            "thresholds": {"cpu": 80, "memory": 90, "disk": 85},
            "retention_days": 30,
        },
        "websocket": {"host": "localhost", "port": 8765, "ssl": False},
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "test-token",
            "org": "test-org",
            "bucket": "test-bucket",
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_pass",
        },
        "logging": {
            "level": "INFO",
            "file": "test.log",
            "format": "%(asctime)s [%(levelname)8s] %(message)s",
        },
        "ui": {"theme": "light", "refresh_interval": 5000, "max_datapoints": 100, "layout": {}},
        "alert_rules": [
            {"metric": "cpu", "threshold": 80, "duration": "5m", "severity": "warning"}
        ],
    }


@pytest.fixture
def config_file(tmp_path, sample_config):
    """Create a temporary config file."""
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(sample_config, f)
    return str(config_file)


def test_config_manager_init(config_file):
    """Test ConfigManager initialization."""
    manager = ConfigManager(config_file)
    assert manager.config is not None
    assert "metrics" in manager.config
    assert "websocket" in manager.config
    assert "database" in manager.config
    assert "logging" in manager.config
    assert "ui" in manager.config


def test_config_manager_load_config(config_file):
    """Test loading configuration from file."""
    manager = ConfigManager(config_file)
    config = manager.get_config()
    assert config["metrics"]["collection_interval"] == 60
    assert config["metrics"]["retention_days"] == 30
    assert len(config["metrics"]["enabled_metrics"]) == 3


def test_config_manager_save_config(config_file):
    """Test saving configuration to file."""
    manager = ConfigManager(config_file)
    config = manager.get_config()
    config["metrics"]["collection_interval"] = 30
    manager.save_config(config)

    # Reload and verify
    new_manager = ConfigManager(config_file)
    new_config = new_manager.get_config()
    assert new_config["metrics"]["collection_interval"] == 30


def test_config_manager_save_config_error(config_file):
    """Test error handling when saving invalid config."""
    manager = ConfigManager(config_file)
    invalid_config = {"invalid": "config"}
    with pytest.raises(SchemaValidationError):
        manager.save_config(invalid_config)


def test_config_manager_get_config(config_file):
    """Test getting configuration."""
    manager = ConfigManager(config_file)
    config = manager.get_config()
    assert isinstance(config, dict)


def test_config_manager_update_config(config_file):
    """Test updating configuration."""
    manager = ConfigManager(config_file)
    updates = {"metrics": {"collection_interval": 30, "retention_days": 60}}
    manager.update_config(updates)
    config = manager.get_config()
    assert config["metrics"]["collection_interval"] == 30
    assert config["metrics"]["retention_days"] == 60


def test_config_manager_alert_rules(config_file):
    """Test alert rules configuration."""
    manager = ConfigManager(config_file)
    alert_rules = [
        {"metric": "cpu_usage", "threshold": 80, "duration": "5m", "severity": "warning"}
    ]
    manager.update_config({"alert_rules": alert_rules})
    config = manager.get_config()
    assert len(config["alert_rules"]) == 1
    assert config["alert_rules"][0]["metric"] == "cpu_usage"


def test_config_manager_alert_rules_validation(config_file):
    """Test alert rules validation."""
    manager = ConfigManager(config_file)
    invalid_rules = [{"metric": "cpu_usage", "threshold": "invalid", "condition": "invalid"}]
    with pytest.raises(SchemaValidationError):
        manager.update_config({"alert_rules": invalid_rules})


def test_global_config_functions(config_file):
    """Test global configuration functions."""
    init_config(config_file)
    config = get_config()
    assert config is not None
    assert "metrics" in config


@pytest.fixture(autouse=True)
def reset_config_manager():
    """Reset global config manager before each test."""
    import sys

    if "dashboard.config.config" in sys.modules:
        del sys.modules["dashboard.config.config"]
    yield
    if "dashboard.config.config" in sys.modules:
        del sys.modules["dashboard.config.config"]


def test_global_config_functions_error(reset_config_manager):
    """Test global configuration functions without initialization."""
    # Re-import after module reset
    from dashboard.config.config import (
        ConfigurationError,
        get_alert_rules,
        get_config,
        update_alert_rules,
        update_config,
    )

    error_msg = "Configuration manager not initialized"

    with pytest.raises(ConfigurationError, match=error_msg):
        get_config()

    with pytest.raises(ConfigurationError, match=error_msg):
        update_config({})

    with pytest.raises(ConfigurationError, match=error_msg):
        get_alert_rules()

    with pytest.raises(ConfigurationError, match=error_msg):
        update_alert_rules([])


if __name__ == "__main__":
    pytest.main([__file__])
