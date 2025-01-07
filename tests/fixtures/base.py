from pathlib import Path

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load test environment variables."""
    env_file = Path(__file__).parent.parent / ".env.test"
    load_dotenv(env_file)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_metrics():
    """Mock metrics data for tests."""
    return {
        "system": {"cpu_usage": 45.5, "memory_usage": 60.2, "disk_usage": 75.8},
        "test": {"coverage": 85.5, "passing_tests": 95.0},
        "errors": {"error_count": 2, "error_rate": 0.5},
    }
