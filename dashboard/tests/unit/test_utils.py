from datetime import datetime, timezone

import pytest

from dashboard.utils import (
    create_response,
    format_bytes,
    load_config,
    parse_duration,
    parse_timestamp,
    sanitize_metric_name,
    setup_logging,
    validate_config,
    validate_metrics,
)


def test_validate_config_valid(config_file):
    """Test config validation with valid config."""
    result = validate_config(config_file)
    assert result is True


def test_validate_config_invalid():
    """Test config validation with invalid config."""
    result = validate_config("nonexistent.json")
    assert result is False


def test_format_bytes():
    """Test byte formatting."""
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1024 * 1024) == "1.00 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"


def test_parse_duration():
    """Test duration parsing."""
    assert parse_duration("1s") == 1
    assert parse_duration("1m") == 60
    assert parse_duration("1h") == 3600
    assert parse_duration("1d") == 86400


def test_sanitize_metric_name():
    """Test metric name sanitization."""
    assert sanitize_metric_name("CPU Usage") == "cpu_usage"
    assert sanitize_metric_name("Memory %") == "memory_percent"
    assert sanitize_metric_name("Disk I/O") == "disk_io"


def test_load_config(config_file):
    """Test config loading."""
    config = load_config(config_file)
    assert isinstance(config, dict)
    assert "metrics" in config
    assert "websocket" in config


def test_setup_logging():
    """Test logging setup."""
    setup_logging("INFO", "test.log")
    # Verify log file was created
    import os

    assert os.path.exists("test.log")
    os.remove("test.log")


def test_create_response():
    """Test response creation."""
    response = create_response({"data": "test"}, 200)
    assert response.status_code == 200
    assert response.json == {"data": "test"}


def test_parse_timestamp():
    """Test timestamp parsing."""
    dt = parse_timestamp("2024-01-08T12:00:00Z")
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 8


def test_validate_metrics():
    """Test metrics validation."""
    sample_metrics = {
        "cpu_percent": 45.5,
        "disk_percent": 75.8,
        "memory_percent": 60.2,
        "timestamp": "2024-01-08T06:51:19.703677+00:00",
    }
    assert validate_metrics(sample_metrics)


def test_format_bytes_error():
    """Test byte formatting error."""
    with pytest.raises(ValueError):
        format_bytes(-1)


def test_parse_duration_error():
    """Test duration parsing error."""
    with pytest.raises(ValueError):
        parse_duration("1x")  # Invalid unit


def test_setup_logging_error():
    """Test logging setup error."""
    with pytest.raises(ValueError):
        setup_logging("INVALID_LEVEL", "test.log")


if __name__ == "__main__":
    pytest.main([__file__])
