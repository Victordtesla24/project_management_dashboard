import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class ValidationResult:
    """Validation result with errors and warnings."""
    is_valid: bool
    errors: List[str] = None

    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []

class ConfigurationError(Exception):
    """Configuration related error."""
    pass

class SchemaValidationError(ConfigurationError):
    """Schema validation error."""
    pass

class ConfigManager:
    """Configuration manager."""
    
    REQUIRED_SECTIONS = {
        'metrics': {
            'collection_interval': int,
            'enabled_metrics': list,
            'thresholds': dict,
            'retention': dict,
            'alert_rules': list,
            'aggregation': dict
        },
        'websocket': {
            'host': str,
            'port': int,
            'ssl': bool
        },
        'database': {
            'host': str,
            'port': int,
            'name': str,
            'user': str,
            'password': str
        },
        'logging': {
            'level': str,
            'file': str,
            'format': str
        },
        'ui': {
            'theme': str,
            'refresh_interval': int,
            'max_datapoints': int,
            'layout': dict
        }
    }
    
    def __init__(self, config_path: str):
        """Initialize configuration manager."""
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config_structure(self.config)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        import os
        import yaml
        import json
        
        if not os.path.exists(self.config_path):
            raise ConfigurationError("Configuration file not found")
        
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except yaml.YAMLError:
            raise ConfigurationError("Invalid YAML in configuration file")
        except json.JSONDecodeError:
            raise ConfigurationError("Invalid JSON in configuration file")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        """Validate configuration structure."""
        for section, schema in self.REQUIRED_SECTIONS.items():
            if section not in config:
                raise SchemaValidationError(f"Missing required section: {section}")
            
            section_data = config[section]
            for field, field_type in schema.items():
                if field not in section_data:
                    raise SchemaValidationError(f"Missing required field in {section}: {field}")
                if not isinstance(section_data[field], field_type):
                    raise SchemaValidationError(
                        f"Invalid type for {section}.{field}: expected {field_type.__name__}"
                    )
            
            # Additional validation for metrics section
            if section == 'metrics':
                # Validate retention
                retention = section_data.get('retention', {})
                if not isinstance(retention, dict):
                    raise SchemaValidationError("Metrics retention must be a dictionary")
                if 'days' not in retention:
                    raise SchemaValidationError("Missing required field in metrics.retention: days")
                if not isinstance(retention['days'], int):
                    raise SchemaValidationError("metrics.retention.days must be an integer")
                if 'max_datapoints' not in retention:
                    raise SchemaValidationError("Missing required field in metrics.retention: max_datapoints")
                if not isinstance(retention['max_datapoints'], int):
                    raise SchemaValidationError("metrics.retention.max_datapoints must be an integer")
                
                # Validate alert rules
                alert_rules = section_data.get('alert_rules', [])
                if not isinstance(alert_rules, list):
                    raise SchemaValidationError("Alert rules must be a list")
                for rule in alert_rules:
                    if not isinstance(rule, dict):
                        raise SchemaValidationError("Each alert rule must be a dictionary")
                    required_fields = ['metric', 'threshold', 'duration', 'severity']
                    for field in required_fields:
                        if field not in rule:
                            raise SchemaValidationError(f"Missing required field in alert rule: {field}")
                
                # Validate aggregation
                aggregation = section_data.get('aggregation', {})
                if not isinstance(aggregation, dict):
                    raise SchemaValidationError("Metrics aggregation must be a dictionary")
                if 'interval' not in aggregation:
                    raise SchemaValidationError("Missing required field in metrics.aggregation: interval")
                if 'functions' not in aggregation:
                    raise SchemaValidationError("Missing required field in metrics.aggregation: functions")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> ValidationResult:
        """Update configuration with new values."""
        import json
        
        # Create a copy of current config
        new_config = self.config.copy()
        new_config.update(updates)
        
        try:
            self._validate_config_structure(new_config)
        except SchemaValidationError as e:
            return ValidationResult(False, [str(e)])
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(new_config, f, indent=4)
            self.config = new_config
            return ValidationResult(True)
        except Exception as e:
            return ValidationResult(False, [f"Failed to save configuration: {e}"])
    
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration."""
        try:
            self._validate_config_structure(config)
            return ValidationResult(True)
        except SchemaValidationError as e:
            return ValidationResult(False, [str(e)])
    
    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get alert rules configuration."""
        return self.config.get('alert_rules', [])
    
    def update_alert_rules(self, rules: List[Dict[str, Any]]) -> ValidationResult:
        """Update alert rules configuration."""
        for rule in rules:
            if not all(k in rule for k in ['metric', 'threshold', 'duration', 'severity']):
                return ValidationResult(False, ["Missing required fields in alert rule: severity, threshold, duration"])
            
            if not isinstance(rule['threshold'], (int, float)):
                return ValidationResult(False, ["Threshold must be a number"])
            
            if rule['severity'] not in ['info', 'warning', 'critical']:
                return ValidationResult(False, ["Invalid severity level"])
        
        self.config['alert_rules'] = rules
        return self.update_config({'alert_rules': rules})

def get_environment_overrides() -> Dict[str, Any]:
    """Get configuration overrides from environment variables."""
    overrides = {}
    
    # Environment
    if env := os.getenv('APP_ENV'):
        overrides['environment'] = env

    # Metrics
    if interval := os.getenv('METRICS_INTERVAL'):
        overrides.setdefault('metrics', {})['collection_interval'] = int(interval)

    # WebSocket
    if ws_port := os.getenv('WS_PORT'):
        overrides.setdefault('websocket', {})['port'] = int(ws_port)

    # InfluxDB
    if influx_url := os.getenv('INFLUXDB_URL'):
        overrides.setdefault('influxdb', {})['url'] = influx_url
    if influx_token := os.getenv('INFLUXDB_TOKEN'):
        overrides.setdefault('influxdb', {})['token'] = influx_token

    return overrides

def apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration."""
    overrides = get_environment_overrides()
    
    def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    return deep_update(config, overrides)
