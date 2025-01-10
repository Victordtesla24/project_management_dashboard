import json
from pathlib import Path


def test_dashboard_config(project_root):
config_file = Path(project_root) / "config" / "dashboard.json"
assert config_file.exists()
assert config_file.is_file()

def test_metrics_integration(test_data, temp_test_dir):
"""\1"""
# Create test metrics file
metrics_file = temp_test_dir / "metrics.json"
metrics_file.write_text(json.dumps(test_data))
# Verify metrics file exists
assert metrics_file.exists()
assert metrics_file.is_file()
# Load and verify metrics
with open(metrics_file) as f:
loaded_data = json.load(f)
assert loaded_data == test_data

def test_coverage_report(project_root):
coverage_dir = Path(project_root) / "tests" / "reports" / "coverage"
assert coverage_dir.exists()
assert coverage_dir.is_dir()
# Check for coverage files
coverage_files = list(coverage_dir.glob("*.html"))
assert len(coverage_files) > 0
