import os
from typing import Dict, Any, Optional
from .config import ConfigManager, ConfigError as ConfigurationError
from .schema import ValidationResult

_config_manager: Optional[ConfigManager] = None

def init_config(config_path: str = None) -> None:
    """Initialize configuration manager."""
    global _config_manager
    
    if config_path is None:
        config_path = os.getenv('CONFIG_PATH', 'config.json')
    
    try:
        _config_manager = ConfigManager(config_path)
    except Exception as e:
        raise ConfigurationError(f"Failed to initialize configuration: {e}")

def get_config() -> Dict[str, Any]:
    """Get current configuration."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.get_config()

def update_config(updates: Dict[str, Any]) -> ValidationResult:
    """Update configuration with new values."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.update_config(updates)

def get_metric_thresholds() -> Dict[str, float]:
    """Get metric threshold values."""
    config = get_config()
    return config.get('metrics', {}).get('thresholds', {
        'cpu': 80.0,
        'memory': 90.0,
        'disk': 85.0
    })

def get_websocket_config() -> Dict[str, Any]:
    """Get WebSocket server configuration."""
    config = get_config()
    return config.get('websocket', {
        'host': 'localhost',
        'port': 8765,
        'ssl': False
    })

def get_influxdb_config() -> Dict[str, Any]:
    """Get InfluxDB configuration."""
    config = get_config()
    return config.get('influxdb', {
        'url': 'http://localhost:8086',
        'token': '',
        'org': '',
        'bucket': ''
    })

def get_alert_rules() -> Dict[str, Any]:
    """Get alert rules configuration."""
    config = get_config()
    return config.get('alert_rules', [])

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    config = get_config()
    return config.get('logging', {
        'level': 'INFO',
        'file': 'dashboard.log',
        'format': '%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
    })

def is_production() -> bool:
    """Check if running in production environment."""
    config = get_config()
    return config.get('environment') == 'production'

def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    config = get_config()
    return config.get('database', {
        'host': 'localhost',
        'port': 5432,
        'name': 'dashboard',
        'user': 'postgres',
        'password': ''
    })

def get_ui_config() -> Dict[str, Any]:
    """Get UI configuration."""
    config = get_config()
    return config.get('ui', {
        'theme': 'light',
        'refresh_interval': 5000,
        'max_datapoints': 100
    })

def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate configuration."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.validate_config(config)

def update_alert_rules(rules: list) -> ValidationResult:
    """Update alert rules configuration."""
    if _config_manager is None:
        raise ConfigurationError("Configuration manager not initialized")
    return _config_manager.update_alert_rules(rules)

__all__ = [
    'init_config', 'get_config', 'update_config', 'ConfigurationError',
    'get_metric_thresholds', 'get_websocket_config', 'get_influxdb_config',
    'get_alert_rules', 'get_logging_config', 'is_production',
    'get_database_config', 'get_ui_config', 'validate_config',
    'update_alert_rules'
]
