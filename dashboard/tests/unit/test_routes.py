from unittest.mock import Mock, patch

import pytest
from flask import url_for

from dashboard.routes import (
    handle_alert_rules_update,
    handle_config_update,
    handle_dashboard_layout,
    handle_metrics_request,
    handle_theme_settings,
)


def test_handle_metrics_request_get(app_context, request_context, mock_request, sample_metrics):
    """Test GET metrics endpoint."""
    with patch("dashboard.metrics.collect_system_metrics", return_value=sample_metrics):
        response = handle_metrics_request()
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 200
        assert "metrics" in response_data
        assert response_data["metrics"]["metrics"] == sample_metrics


def test_handle_metrics_request_with_filters(
    app_context, request_context, mock_request, sample_metrics
):
    """Test metrics endpoint with filters."""
    mock_request.args = {"metrics": "cpu,memory"}
    filtered_metrics = {"cpu": sample_metrics["cpu"], "memory": sample_metrics["memory"]}

    with patch("dashboard.metrics.collect_system_metrics", return_value=filtered_metrics):
        response = handle_metrics_request()
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 200
        assert "metrics" in response_data
        metrics_data = response_data["metrics"]["metrics"]
        assert "cpu" in metrics_data
        assert "memory" in metrics_data
        assert "disk" not in metrics_data


def test_handle_config_update_valid(app_context, request_context, mock_request, sample_config):
    """Test valid configuration update."""
    mock_request.method = "POST"
    mock_request.json = sample_config

    with patch("dashboard.config.update_config") as mock_update:
        mock_update.return_value = Mock(is_valid=True, errors=[])
        response = handle_config_update(sample_config)
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 200
        assert response_data["status"] == "success"


def test_handle_config_update_invalid(app_context, request_context, mock_request):
    """Test invalid configuration update."""
    invalid_config = {"invalid": "config"}

    response = handle_config_update(invalid_config)
    assert isinstance(response, tuple)
    response_data, status_code = response
    assert status_code == 400
    assert "error" in response_data


def test_handle_alert_rules_update_valid(app_context, request_context, mock_request):
    """Test updating alert rules."""
    rules_data = {
        "rules": [{"metric": "cpu", "threshold": 80, "duration": "5m", "severity": "warning"}]
    }

    with patch("dashboard.config.update_alert_rules") as mock_update:
        mock_update.return_value = Mock(is_valid=True, errors=[])
        response = handle_alert_rules_update(rules_data)
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 200
        assert response_data["status"] == "success"


def test_handle_alert_rules_update_invalid(app_context, request_context, mock_request):
    """Test updating alert rules with invalid data."""
    invalid_rules = {"rules": [{"invalid": "rule"}]}

    response = handle_alert_rules_update(invalid_rules)
    assert isinstance(response, tuple)
    response_data, status_code = response
    assert status_code == 400
    assert "error" in response_data


def test_handle_dashboard_layout_valid(app_context, request_context, mock_request):
    """Test updating dashboard layout."""
    layout_data = {"layout": {"columns": 2, "rows": 2, "widgets": []}}

    with patch("dashboard.config.update_config") as mock_update:
        mock_update.return_value = Mock(is_valid=True, errors=[])
        response = handle_dashboard_layout(layout_data)
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 200
        assert response_data["status"] == "success"


def test_handle_dashboard_layout_invalid(app_context, request_context, mock_request):
    """Test updating dashboard layout with invalid data."""
    invalid_layout = {"layout": "invalid"}

    response = handle_dashboard_layout(invalid_layout)
    assert isinstance(response, tuple)
    response_data, status_code = response
    assert status_code == 400
    assert "error" in response_data


def test_handle_theme_settings_valid(app_context, request_context, mock_request):
    """Test updating theme settings."""
    theme_data = {"theme": "dark", "custom_colors": {"primary": "#000000"}}

    with patch("dashboard.config.update_config") as mock_update:
        mock_update.return_value = Mock(is_valid=True, errors=[])
        response = handle_theme_settings(theme_data)
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 200
        assert response_data["status"] == "success"


def test_handle_theme_settings_invalid(app_context, request_context, mock_request):
    """Test updating theme settings with invalid data."""
    invalid_theme = {"theme": "invalid"}

    response = handle_theme_settings(invalid_theme)
    assert isinstance(response, tuple)
    response_data, status_code = response
    assert status_code == 400
    assert "error" in response_data


def test_handle_metrics_request_error(app_context, request_context, mock_request):
    """Test metrics endpoint error handling."""
    with patch("dashboard.metrics.collect_system_metrics", side_effect=Exception("Test error")):
        response = handle_metrics_request()
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 500
        assert "error" in response_data


def test_handle_alert_rules_update_error(app_context, request_context, mock_request):
    """Test alert rules update error handling."""
    rules_data = {
        "rules": [{"metric": "cpu", "threshold": 80, "duration": "5m", "severity": "warning"}]
    }

    with patch("dashboard.config.update_alert_rules", side_effect=Exception("Test error")):
        response = handle_alert_rules_update(rules_data)
        assert isinstance(response, tuple)
        response_data, status_code = response
        assert status_code == 500
        assert "error" in response_data
