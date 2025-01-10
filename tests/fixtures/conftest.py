import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    return Path(__file__).parent / "data"


@pytest.fixture(scope="function")
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def test_config():
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_password",
        },
        "api": {"host": "localhost", "port": 8000, "debug": True},
        "metrics": {
            "collection_interval": 60,
            "retention_days": 30,
            "enabled_metrics": ["cpu", "memory", "disk"],
        },
        "auth": {"secret_key": "test_secret_key", "token_expiry": 3600, "algorithm": "HS256"},
    }


@pytest.fixture(scope="function")
async def app_context():
    """Provides an async application context for tests."""
    import asyncio

    from dashboard.app import create_app

    app = create_app(test_config())
    loop = asyncio.get_event_loop()

    yield app

    # Clean up any remaining tasks
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
