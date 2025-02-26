import json

import pytest

from dashboard.config.config import ConfigManager, get_config, init_config
from dashboard.config.schema import SchemaValidationError


@pytest.fixture(autouse=True)
def setup_config(config_file):
    """Setup config for tests"""
    init_config(config_file)


@pytest.fixture
def sample_config():
    """Sample config for tests"""
    return {
        "environment": "test",
        "metrics": {
            "collection_interval": 60,
            "enabled_metrics": ["cpu", "memory", "disk"],
            "thresholds": {"cpu": 80, "memory": 90, "disk": 85},
            "retention_days": 30
        },
        "websocket": {"host": "localhost", "port": 8765, "ssl": False},
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "test-token",
            "org": "test-org",
            "bucket": "test-bucket"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_pass"
        },
        "logging": {
            "level": "INFO",
            "file": "test.log",
            "format": "%(asctime)s [%(levelname)8s] %(message)s"
        },
        "ui": {
            "theme": "light",
            "refresh_interval": 5000,
            "max_datapoints": 100,
            "layout": {}
        }
    }


@pytest.fixture
def config_file(tmp_path, sample_config):
    """\1"""
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(sample_config, f)
    return str(config_file)


def test_config_manager_init(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    assert manager.config is not None
    assert "metrics" in manager.config
    assert "websocket" in manager.config
    assert "database" in manager.config
    assert "logging" in manager.config
    assert "ui" in manager.config


def test_config_manager_load_config(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    config = manager.get_config()
    assert config["metrics"]["collection_interval"] == 60
    assert config["metrics"]["retention_days"] == 30
    assert len(config["metrics"]["enabled_metrics"]) == 3


def test_config_manager_save_config(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    config = manager.get_config()
    config["metrics"]["collection_interval"] = 30
    manager.save_config(config)
    new_manager = ConfigManager(config_file)
    new_config = new_manager.get_config()
    assert new_config["metrics"]["collection_interval"] == 30


def test_config_manager_save_config_error(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    invalid_config = {"invalid": "config"}
    with pytest.raises(SchemaValidationError):
        manager.save_config(invalid_config)


def test_config_manager_get_config(config_file):
    """\1"""
    manager = ConfigManager(config_file)    
    config = manager.get_config()
    assert isinstance(config, dict)


def test_config_manager_update_config(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    updates = {"metrics": {"collection_interval": 30, "retention_days": 60}}
    manager.update_config(updates)
    config = manager.get_config()
    assert config["metrics"]["collection_interval"] == 30
    assert config["metrics"]["retention_days"] == 60


def test_config_manager_alert_rules(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    alert_rules = [
        {
            "metric": "cpu_usage",
            "threshold": 80,
            "duration": "5m",
            "severity": "warning",
        },
    ]
    manager.update_config({"alert_rules": alert_rules})
    config = manager.get_config()
    assert len(config["alert_rules"]) == 1
    assert config["alert_rules"][0]["metric"] == "cpu_usage"


def test_config_manager_alert_rules_validation(config_file):
    """\1"""
    manager = ConfigManager(config_file)
    invalid_rules = [{"metric": "cpu_usage", "threshold": "invalid", "condition": "invalid"}]
    with pytest.raises(SchemaValidationError):
        manager.update_config({"alert_rules": invalid_rules})


def test_global_config_functions(config_file):
    """\1"""
    init_config(config_file)
    config = get_config()
    assert config is not None
    assert "metrics" in config


@pytest.fixture(autouse=True)
def reset_config_manager():
    """\1"""
    import sys

    if "dashboard.config.config" in sys.modules:
        del sys.modules["dashboard.config.config"]
    yield
    if "dashboard.config.config" in sys.modules:
        del sys.modules["dashboard.config.config"]


def test_global_config_functions_error(reset_config_manager):
    """\1"""
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
