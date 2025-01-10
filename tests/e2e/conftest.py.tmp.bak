from pathlib import Path

import pytest


@pytest.fixture
def test_data():
"""\1"""
return {
"metrics": {
"cpu": {"percent": 50.0, "count": 8, "frequency": 2.4},
"memory": {"percent": 60.0, "total": 16000, "used": 9600},
"disk": {"percent": 70.0, "total": 500000, "used": 350000},
},
"timestamp": "2024-03-21T12:00:00",
"uptime": 3600,
}


@pytest.fixture
def temp_test_dir(tmp_path):
"""\1"""
test_dir = tmp_path / "test_dir"
test_dir.mkdir()
return test_dir


@pytest.fixture
def metrics_dir(project_root):
"""\1"""
metrics_dir = Path(project_root) / "metrics" / "data"
metrics_dir.mkdir(parents=True, exist_ok=True)
return metrics_dir


@pytest.fixture
def logs_dir(project_root):
"""\1"""
logs_dir = Path(project_root) / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
return logs_dir


@pytest.fixture(autouse=True)
def setup_monitor_env(metrics_dir, logs_dir):
"""\1"""
# Create default config
config_dir = metrics_dir.parent
config_file = config_dir / "monitor_config.json"
config_file.write_text(
"""{
"collection_interval": 1,
"metrics": {
"cpu": true,
"memory": true,
"disk": true,
"network": true,
"load": true
},
"processes": [
{
"name": "python",
"pattern": "python",
"metrics": ["cpu", "memory", "threads"]
}
]
}""",
)
