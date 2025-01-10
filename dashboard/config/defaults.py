"""Default configuration values."""

DEFAULT_CONFIG = {
    "metrics": {
        "collection_interval": 60,
        "enabled_metrics": ["cpu", "memory", "disk"],
        "thresholds": {"cpu": 80, "memory": 85, "disk": 90},
        "retention": {"days": 30, "max_datapoints": 10000},
        "alert_rules": [{"metric": "cpu", "threshold": 80, "duration": 300, "severity": "warning"}],
        "aggregation": {"interval": 300, "functions": ["avg", "max", "min"]},
    },
    "websocket": {"host": "localhost", "port": 8765, "ssl": False},
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "dashboard",
        "user": "dashboard",
        "password": "",
    },
    "logging": {
        "level": "INFO",
        "file": "logs/dashboard.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    },
    "ui": {
        "theme": "light",
        "refresh_interval": 10,
        "max_datapoints": 100,
        "layout": {"sidebar": True, "charts": ["cpu", "memory", "disk"]},
    },
}
