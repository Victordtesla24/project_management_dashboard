from unittest.mock import Mock, patch

from dashboard.routes import dashboard_bp


def test_get_metrics_data(app_context, request_context, mock_request, sample_metrics):
"""\1"""
with patch(
"dashboard.metrics.collector.MetricsCollector.collect_metrics",
return_value=sample_metrics,
    ):
response = dashboard_bp.get_metrics_data()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 200
assert isinstance(response_data.json, dict)
assert "metrics" in response_data.json

def test_get_metrics_data_with_filters(app_context, request_context, mock_request, sample_metrics):
"""\1"""
mock_request.args = {"metrics": "cpu,memory"}
filtered_metrics = {
"cpu": sample_metrics["cpu"],
"memory": sample_metrics["memory"],
    }
with patch(
"dashboard.metrics.collector.MetricsCollector.collect_metrics",
return_value=filtered_metrics,
    ):
response = dashboard_bp.get_metrics_data()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 200
assert isinstance(response_data.json, dict)
metrics_data = response_data.json.get("metrics", {})
assert "cpu" in metrics_data
assert "memory" in metrics_data
assert "disk" not in metrics_data

def test_update_config_valid(app_context, request_context, mock_request, sample_config):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: sample_config
with patch("dashboard.config.get_config") as mock_get_config:
mock_config = Mock()
mock_get_config.return_value = mock_config
response = dashboard_bp.update_config()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 200
assert "message" in response_data.json

def test_update_config_invalid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: {"invalid": "config"}
response = dashboard_bp.update_config()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 400
assert "error" in response_data.json

def test_update_alert_rules_valid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: [
{"metric": "cpu", "threshold": 80, "duration": "5m", "severity": "warning"},
    ]
with patch("dashboard.config.get_config") as mock_get_config:
mock_config = Mock()
mock_get_config.return_value = mock_config
response = dashboard_bp.update_alert_rules()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 200
assert "message" in response_data.json

def test_update_alert_rules_invalid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: [{"invalid": "rule"}]
response = dashboard_bp.update_alert_rules()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 400
assert "error" in response_data.json

def test_update_layout_valid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: {
"columns": 2,
"rows": 2,
"widgets": [{"type": "chart", "position": {"x": 0, "y": 0}}],
    }
with patch("dashboard.config.get_config") as mock_get_config:
mock_config = Mock()
mock_get_config.return_value = mock_config
response = dashboard_bp.update_layout()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 200
assert "message" in response_data.json

def test_update_layout_invalid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: {"invalid": "layout"}
response = dashboard_bp.update_layout()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 400
assert "error" in response_data.json

def test_update_theme_valid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: {
"theme": "dark",
"custom_colors": {"primary": "#000000"},
    }
with patch("dashboard.config.get_config") as mock_get_config:
mock_config = Mock()
mock_get_config.return_value = mock_config
response = dashboard_bp.update_theme()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 200
assert "message" in response_data.json

def test_update_theme_invalid(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: {"theme": "invalid"}
response = dashboard_bp.update_theme()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 400
assert "error" in response_data.json

def test_get_metrics_data_error(app_context, request_context, mock_request):
"""\1"""
with patch(
"dashboard.metrics.collector.MetricsCollector.collect_metrics",
side_effect=Exception("Test error"),
    ):
response = dashboard_bp.get_metrics_data()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 500
assert "error" in response_data.json

def test_update_alert_rules_error(app_context, request_context, mock_request):
"""\1"""
mock_request.method = "POST"
mock_request.is_json = True
mock_request.get_json = lambda: [
{"metric": "cpu", "threshold": 80, "duration": "5m", "severity": "warning"},
    ]
with patch("dashboard.config.get_config", side_effect=Exception("Test error")):
response = dashboard_bp.update_alert_rules()
assert isinstance(response, tuple)
response_data, status_code = response
assert status_code == 500
assert "error" in response_data.json
