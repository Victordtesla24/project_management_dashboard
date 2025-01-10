import pytest


@pytest.fixture
def test_data():
    """Test data fixture."""
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
    """Temporary test directory fixture."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    return test_dir
