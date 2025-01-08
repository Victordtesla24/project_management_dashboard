import json
import os
from typing import Dict, Any, List, Optional
from .schema import ValidationResult, SchemaValidationError

class ConfigurationError(Exception):
    """Base exception for configuration errors."""
    pass

ConfigError = ConfigurationError  # For backwards compatibility

class ConfigManager:
    def __init__(self, config_path: str):
        """Initialize configuration manager."""
        self.config_path = config_path
        self.config: Optional[Dict[str, Any]] = None
        self._schema = self._init_schema()
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            # Set default values for metrics configuration
            if 'metrics' not in self.config:
                self.config['metrics'] = {}
            
            metrics = self.config['metrics']
            metrics.setdefault('collection_interval', 60)
            metrics.setdefault('retention_days', 30)
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {str(e)}")

    def _init_schema(self) -> Any:
        """Initialize schema validator."""
        from .schema import ConfigManager as SchemaManager
        return SchemaManager(self.config_path)

    def save_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Save configuration to file."""
        # Validate new configuration
        validation = self._schema.validate_config(config)
        if not validation.is_valid:
            return validation

        try:
            self.config = config
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return ValidationResult(True)
        except Exception as e:
            return ValidationResult(False, [f"Failed to save configuration: {str(e)}"])

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        if self.config is None:
            self.load_config()
        return self.config

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration."""
        try:
            return self._schema.validate_config(config)
        except Exception as e:
            return ValidationResult(False, [str(e)])

    def update_config(self, new_config: Dict[str, Any]) -> ValidationResult:
        """Update configuration with new values."""
        try:
            # Create a deep copy of current config
            updated_config = self.config.copy()
            
            # Deep update the configuration
            def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
                for k, v in u.items():
                    if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                        d[k] = deep_update(d[k].copy(), v)
                    else:
                        d[k] = v
                return d
            
            updated_config = deep_update(updated_config, new_config)
            
            # Validate the updated config
            validation = self.validate_config(updated_config)
            if not validation.is_valid:
                return validation
            
            # Save the validated config
            return self.save_config(updated_config)
        except Exception as e:
            return ValidationResult(False, [str(e)])

    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get alert rules from configuration."""
        return self.get_config().get('alert_rules', [])

    def update_alert_rules(self, rules: List[Dict[str, Any]]) -> ValidationResult:
        """Update alert rules in configuration."""
        try:
            # Validate rules
            validation = self._schema.validate_config({
                'alert_rules': rules,
                'metrics': self.config.get('metrics', {}),
                'websocket': self.config.get('websocket', {}),
                'database': self.config.get('database', {}),
                'logging': self.config.get('logging', {}),
                'ui': self.config.get('ui', {})
            })
            if not validation.is_valid:
                return validation
            
            # Update and save config
            self.config['alert_rules'] = rules
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return ValidationResult(True)
        except Exception as e:
            return ValidationResult(False, [str(e)])

# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None

def init_config(config_path: str) -> None:
    """Initialize global configuration manager."""
    global _config_manager
    _config_manager = ConfigManager(config_path)

def get_config() -> Dict[str, Any]:
    """Get current configuration."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.get_config()

def update_config(new_config: Dict[str, Any]) -> ValidationResult:
    """Update configuration with new values."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.update_config(new_config)

def get_alert_rules() -> List[Dict[str, Any]]:
    """Get alert rules from configuration."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.get_alert_rules()

def update_alert_rules(rules: List[Dict[str, Any]]) -> ValidationResult:
    """Update alert rules in configuration."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.update_alert_rules(rules)
