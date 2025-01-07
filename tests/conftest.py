import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data():
    return {
        "metrics": {"cpu_usage": 45.2, "memory_usage": 78.5, "disk_usage": 62.1},
        "tests": {"total": 150, "passed": 142, "failed": 8},
        "coverage": {"lines": 85.4, "branches": 78.9, "functions": 92.3},
    }


@pytest.fixture(scope="function")
def temp_test_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
