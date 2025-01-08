import pytest
from dashboard.config.schema import ConfigManager, ValidationResult, ConfigurationError, SchemaValidationError
import json
from pathlib import Path
import tempfile

@pytest.fixture
def valid_config():
    return {
        "environment": "dev",
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "dashboard"
        },
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "test-token",
            "org": "test-org",
            "bucket": "test-bucket"
        },
        "websocket": {
            "host": "localhost",
            "port": 8765,
            "ssl": False
        }
    }

@pytest.fixture
def config_file(valid_config, tmp_path):
    config_path = tmp_path / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(valid_config, f)
    return str(config_path)

class TestConfigManager:
    def test_init_with_valid_config(self, config_file):
        manager = ConfigManager(config_file)
        assert isinstance(manager.get_config(), dict)

    def test_init_with_invalid_path(self):
        with pytest.raises(ConfigurationError):
            ConfigManager("nonexistent/path.json")

    def test_validate_valid_config(self, valid_config, config_file):
        manager = ConfigManager(config_file)
        result = manager.validate_config(valid_config)
        assert result.is_valid
        assert not result.errors
        
    def test_validate_invalid_config(self, valid_config, config_file):
        invalid_config = valid_config.copy()
        del invalid_config["database"]["port"]
        
        manager = ConfigManager(config_file)
        result = manager.validate_config(invalid_config)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_update_config(self, config_file):
        manager = ConfigManager(config_file)
        updates = {"environment": "staging"}
        
        result = manager.update_config(updates)
        assert result.is_valid
        assert manager.get_config()["environment"] == "staging"

    def test_update_invalid_config(self, config_file):
        manager = ConfigManager(config_file)
        invalid_updates = {"environment": "invalid"}
        
        with pytest.raises(SchemaValidationError):
            manager.update_config(invalid_updates)

    def test_environment_specific_validation(self, valid_config, config_file):
        prod_config = valid_config.copy()
        prod_config["environment"] = "prod"
        
        manager = ConfigManager(config_file)
        result = manager.validate_config(prod_config)
        assert len(result.warnings) > 0  # Should warn about missing logging config in prod

    def test_get_config_returns_copy(self, config_file):
        manager = ConfigManager(config_file)
        config = manager.get_config()
        config["new_key"] = "new_value"
        
        assert "new_key" not in manager.get_config()

def test_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("DB_PORT", "5433")
    
    from dashboard.config.schema import get_environment_overrides
    overrides = get_environment_overrides()
    
    assert overrides["environment"] == "staging"
    assert overrides["database"]["port"] == 5433
