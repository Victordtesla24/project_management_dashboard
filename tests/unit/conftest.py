import pytest


@pytest.fixture
def mock_metrics():
"""\1"""
return {
"timestamp": "2024-03-21T12:00:00",
"metrics": {
"cpu": {
"percent": 50.0,
"count": 8,
"freq": {"current": 2.5, "min": 2.0, "max": 3.0},
},
"memory": {"total": 16000000000, "available": 8000000000, "percent": 50.0},
"disk": {
"total": 100000000000,
"used": 50000000000,
"free": 50000000000,
"percent": 50.0,
},
"network": {"bytes_sent": 1000000, "bytes_recv": 2000000},
},
}


@pytest.fixture
def mock_session_state():
"""\1"""
return {"metrics_history": []}


@pytest.fixture
def test_data(tmp_path):
"""\1"""
data_dir = tmp_path / "test_data"
data_dir.mkdir()

# Create sample files
(data_dir / "metrics.json").write_text('{"cpu": 50, "memory": 60}')
(data_dir / "coverage.xml").write_text('<coverage version="1.0"></coverage>')

return data_dir


@pytest.fixture
def temp_test_dir(tmp_path):
"""\1"""
test_dir = tmp_path / "temp_test_dir"
test_dir.mkdir()
return test_dir


@pytest.fixture(autouse=True)
def setup_config(tmp_path):
"""\1"""
from dashboard.config import init_config

config_file = tmp_path / "test_config.json"
config_file.write_text(
"""{
"metrics": {
"collection_interval": 60,
"enabled_metrics": ["cpu", "memory", "disk"],
"thresholds": {"cpu": 80, "memory": 90, "disk": 85},
"retention": {"days": 30, "max_datapoints": 1000},
"alert_rules": [
{
"metric": "cpu",
"threshold": 80,
"duration": 300,
"severity": "warning"
},
{
"metric": "memory",
"threshold": 90,
"duration": 300,
"severity": "critical"
}
],
"aggregation": {
"interval": 300,
"functions": ["avg", "max", "min"]
}
},
"websocket": {
"host": "localhost",
"port": 8765,
"ssl": false
},
"database": {
"host": "localhost",
"port": 5432,
"name": "dashboard_test",
"user": "test_user",
"password": "test_password"
},
"logging": {
"level": "INFO",
"file": "logs/test.log",
"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
},
"ui": {
"theme": "light",
"refresh_interval": 5,
"max_datapoints": 100,
"layout": {
"columns": 2,
"rows": 3,
"widgets": []
}
}
}""",
)
init_config(str(config_file))
return str(config_file)
