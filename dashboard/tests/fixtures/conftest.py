import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import jwt
import pytest

from dashboard.auth.middleware import create_token
from dashboard.config import get_config
from dashboard.core_scripts.metrics_collector import MetricsCollector
from dashboard.websocket.server import MetricsWebSocket


@pytest.fixture(scope="session")
def test_config() -> dict[str, Any]:
    """Provide test configuration."""
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
        "websocket": {"host": "localhost", "port": 8765, "ssl": False},
    }


@pytest.fixture(scope="function")
async def app_context(test_config):
    """Provide application context with event loop."""
    loop = asyncio.get_event_loop()

    # Create test directories
    test_dir = Path("tests/data")
    test_dir.mkdir(parents=True, exist_ok=True)

    yield {"config": test_config, "loop": loop, "test_dir": test_dir}

    # Cleanup
    for file in test_dir.glob("*"):
        file.unlink()
    test_dir.rmdir()


@pytest.fixture(scope="function")
async def metrics_collector(app_context):
    """Provide metrics collector instance."""
    collector = MetricsCollector(
        port=8001, retention_days=1  # Different port for tests  # Short retention for tests
    )
    yield collector


@pytest.fixture(scope="function")
async def websocket_server(app_context):
    """Provide WebSocket server instance."""
    server = MetricsWebSocket()
    await server.start_server()
    yield server
    await server.stop_server()


@pytest.fixture(scope="function")
def auth_token(test_config):
    """Provide valid authentication token."""
    return create_token({"sub": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)})


@pytest.fixture(scope="function")
def invalid_token():
    """Provide invalid authentication token."""
    return jwt.encode(
        {"sub": "test_user", "exp": datetime.utcnow() - timedelta(hours=1)},
        "wrong_secret",
        algorithm="HS256",
    )


@pytest.fixture(scope="function")
async def test_client(app_context, auth_token):
    """Provide test client with authentication."""
    from aiohttp import ClientSession

    async with ClientSession() as session:
        session.cookie_jar.update_cookies({"auth_token": auth_token})
        yield session
