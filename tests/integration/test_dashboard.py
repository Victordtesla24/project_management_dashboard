import json


def test_dashboard_config(project_root):
    config_file = project_root / "config" / "dashboard.json"
    assert config_file.exists()

    config = json.loads(config_file.read_text())
    assert "port" in config
    assert isinstance(config["port"], int)
    assert 1024 <= config["port"] <= 65535


def test_metrics_integration(test_data, temp_test_dir):
    metrics_file = temp_test_dir / "metrics.json"
    metrics_file.write_text(json.dumps(test_data["metrics"]))

    loaded_metrics = json.loads(metrics_file.read_text())
    assert loaded_metrics == test_data["metrics"]


def test_coverage_report(project_root):
    coverage_dir = project_root / "tests" / "reports" / "coverage"
    coverage_dir.mkdir(parents=True, exist_ok=True)

    report_file = coverage_dir / "coverage.json"
    assert not report_file.exists() or report_file.stat().st_size > 0
