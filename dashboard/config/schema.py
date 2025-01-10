import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Validation result class."""
    is_valid: bool
    errors: list[str] = []

    def __init__(self, is_valid: bool, errors: Optional[list[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []


class ConfigurationError(Exception):
    """Base configuration error class."""
    pass


class SchemaValidationError(ConfigurationError):
    """Schema validation error class."""
    pass


class ValidationError(Exception):
    """Validation error class."""
    pass


class ConfigManager:
    """Configuration manager class."""
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.required_fields = {
            "metrics": {
                "collection_interval": int,
                "enabled_metrics": list,
                "thresholds": dict,
            },
            "websocket": {
                "host": str,
                "port": int,
            },
            "database": {
                "host": str,
                "port": int,
                "name": str,
            },
            "logging": {
                "level": str,
                "file": str,
            },
        }

    def _validate_type(self, value: Any, expected_type: type, path: str) -> None:
        """Validate type of a value.
        
        Args:
            value: Value to validate.
            expected_type: Expected type.
            path: Path to the value in config.
        
        Raises:
            ValidationError: If type is invalid.
        """
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Invalid type for {path}: expected {expected_type.__name__}, got {type(value).__name__}",
            )

    def _validate_metrics_section(self, metrics: dict[str, Any]) -> None:
        """Validate metrics section of config.
        
        Args:
            metrics: Metrics configuration section.
            
        Raises:
            ValidationError: If validation fails.
        """
        required_metrics = {"collection_interval", "enabled_metrics", "thresholds"}
        missing = required_metrics - set(metrics.keys())
        if missing:
            raise ValidationError(f"Missing required metrics fields: {missing}")

        self._validate_type(metrics["collection_interval"], int, "metrics.collection_interval")
        self._validate_type(metrics["enabled_metrics"], list, "metrics.enabled_metrics")
        self._validate_type(metrics["thresholds"], dict, "metrics.thresholds")

        # Validate thresholds
        required_thresholds = {"cpu", "memory", "disk"}
        missing = required_thresholds - set(metrics["thresholds"].keys())
        if missing:
            raise ValidationError(f"Missing required threshold fields: {missing}")

        for key, value in metrics["thresholds"].items():
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ValidationError(f"Invalid threshold value for {key}: must be between 0 and 100")

    def _validate_websocket_section(self, websocket: dict[str, Any]) -> None:
        """Validate websocket section of config.
        
        Args:
            websocket: Websocket configuration section.
            
        Raises:
            ValidationError: If validation fails.
        """
        required_fields = {"host", "port"}
        missing = required_fields - set(websocket.keys())
        if missing:
            raise ValidationError(f"Missing required websocket fields: {missing}")

        self._validate_type(websocket["host"], str, "websocket.host")
        self._validate_type(websocket["port"], int, "websocket.port")

        if not 1 <= websocket["port"] <= 65535:
            raise ValidationError("Websocket port must be between 1 and 65535")

    def _validate_database_section(self, database: dict[str, Any]) -> None:
        """Validate database section of config.
        
        Args:
            database: Database configuration section.
            
        Raises:
            ValidationError: If validation fails.
        """
        required_fields = {"host", "port", "name"}
        missing = required_fields - set(database.keys())
        if missing:
            raise ValidationError(f"Missing required database fields: {missing}")

        self._validate_type(database["host"], str, "database.host")
        self._validate_type(database["port"], int, "database.port")
        self._validate_type(database["name"], str, "database.name")

        if not 1 <= database["port"] <= 65535:
            raise ValidationError("Database port must be between 1 and 65535")

    def _validate_logging_section(self, logging_config: dict[str, Any]) -> None:
        """Validate logging section of config.
        
        Args:
            logging_config: Logging configuration section.
            
        Raises:
            ValidationError: If validation fails.
        """
        required_fields = {"level", "file"}
        missing = required_fields - set(logging_config.keys())
        if missing:
            raise ValidationError(f"Missing required logging fields: {missing}")

        self._validate_type(logging_config["level"], str, "logging.level")
        self._validate_type(logging_config["file"], str, "logging.file")

        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if logging_config["level"].upper() not in valid_levels:
            raise ValidationError(f"Invalid logging level. Must be one of: {valid_levels}")

    def validate_config(self) -> None:
        """Validate entire configuration.
        
        Raises:
            ValidationError: If validation fails.
        """
        if not isinstance(self.config, dict):
            raise ValidationError("Configuration must be a dictionary")

        # Check for required top-level sections
        required_sections = {"metrics", "websocket", "database", "logging"}
        missing = required_sections - set(self.config.keys())
        if missing:
            raise ValidationError(f"Missing required configuration sections: {missing}")

        # Validate each section
        self._validate_metrics_section(self.config["metrics"])
        self._validate_websocket_section(self.config["websocket"])
        self._validate_database_section(self.config["database"])
        self._validate_logging_section(self.config["logging"])

    def get_config(self) -> dict[str, Any]:
        """Get validated configuration."""
        self.validate_config()
        return self.config

    def update_config(self, updates: dict[str, Any]) -> ValidationResult:
        """Update configuration with new values.
        
        Args:
            updates: New configuration values.
            
        Returns:
            ValidationResult indicating success/failure.
        """
        # Create a copy of current config
        new_config = self.config.copy()
        new_config.update(updates)

        try:
            self._validate_config_structure(new_config)
            return ValidationResult(True)
        except SchemaValidationError as e:
            return ValidationResult(False, [str(e)])

    def validate_config(self, config: dict[str, Any]) -> ValidationResult:
        """Validate configuration against schema.
        
        Args:
            config: Configuration to validate.
            
        Returns:
            ValidationResult indicating success/failure.
        """
        try:
            self._validate_config_structure(config)
            return ValidationResult(True)
        except SchemaValidationError as e:
            return ValidationResult(False, [str(e)])

    def get_alert_rules(self) -> list[dict[str, Any]]:
        """Get alert rules from configuration."""
        return self.config.get("alert_rules", [])

    def update_alert_rules(self, rules: list[dict[str, Any]]) -> ValidationResult:
        """Update alert rules in configuration.
        
        Args:
            rules: New alert rules.
            
        Returns:
            ValidationResult indicating success/failure.
        """
        for rule in rules:
            if not all(k in rule for k in ["metric", "threshold", "duration", "severity"]):
                return ValidationResult(
                    False,
                    ["Missing required fields in alert rule: severity, threshold, duration"],
                )
            if not isinstance(rule["threshold"], (int, float)):
                return ValidationResult(False, ["Threshold must be a number"])
            if rule["severity"] not in ["info", "warning", "critical"]:
                return ValidationResult(False, ["Invalid severity level"])

        self.config["alert_rules"] = rules
        return self.update_config({"alert_rules": rules})


def get_environment_overrides() -> dict[str, Any]:
    """Get configuration overrides from environment variables."""
    overrides = {}

    # Environment
    if env := os.getenv("APP_ENV"):
        overrides["environment"] = env

    # Metrics
    if interval := os.getenv("METRICS_INTERVAL"):
        overrides.setdefault("metrics", {})["collection_interval"] = int(interval)

    # WebSocket
    if ws_port := os.getenv("WS_PORT"):
        overrides.setdefault("websocket", {})["port"] = int(ws_port)

    # InfluxDB
    if influx_url := os.getenv("INFLUXDB_URL"):
        overrides.setdefault("influxdb", {})["url"] = influx_url
    if influx_token := os.getenv("INFLUXDB_TOKEN"):
        overrides.setdefault("influxdb", {})["token"] = influx_token

    return overrides


def apply_environment_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """Apply environment variable overrides to configuration.
    
    Args:
        config: Base configuration.
        
    Returns:
        Configuration with overrides applied.
    """
    overrides = get_environment_overrides()

    def deep_update(d: dict[str, Any], u: dict[str, Any]) -> dict[str, Any]:
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    return deep_update(config, overrides)
