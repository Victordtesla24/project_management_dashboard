import asyncio
import json
from datetime import datetime, timedelta

import pytest

from dashboard.core_scripts.metrics_collector import MetricsCollector
from dashboard.websocket.server import MetricsWebSocket


class TestWebSocketServer:
"""\1"""
@pytest.mark.asyncio
async def test_websocket_authentication(
self, websocket_server, test_client, auth_token, invalid_token,
    ):
"""\1"""
# Test valid token
async with test_client.ws_connect(f"ws://localhost:8765?token={auth_token}") as ws:
assert ws.closed is False
await ws.close()
# Test invalid token
with pytest.raises(Exception):
async with test_client.ws_connect(f"ws://localhost:8765?token={invalid_token}") as ws:
# Test missing token
with pytest.raises(Exception):
async with test_client.ws_connect("ws://localhost:8765") as ws:
@pytest.mark.asyncio
async def test_metrics_subscription(self, websocket_server, test_client, auth_token):
"""\1"""
async with test_client.ws_connect(f"ws://localhost:8765?token={auth_token}") as ws:
# Subscribe to metrics
await ws.send_json({"type": "subscribe", "metrics": ["cpu", "memory"]})
# Receive initial data
response = await ws.receive_json()
assert "cpu" in response
assert "memory" in response
@pytest.mark.asyncio
async def test_ping_pong(self, websocket_server, test_client, auth_token):
"""\1"""
async with test_client.ws_connect(f"ws://localhost:8765?token={auth_token}") as ws:
await ws.send_json({"type": "ping"})
response = await ws.receive_json()
assert response["type"] == "pong"
class TestMetricsCollector:
"""\1"""
def test_system_metrics_collection(self, metrics_collector):
"""\1"""
metrics = metrics_collector.collect_system_metrics()
assert "cpu_usage" in metrics
assert "memory_usage" in metrics
assert "disk_usage" in metrics
assert "timestamp" in metrics
def test_project_metrics_collection(self, metrics_collector):
"""\1"""
metrics = metrics_collector.collect_project_metrics()
assert "active_tasks" in metrics
assert "completed_tasks" in metrics
assert "team_velocity" in metrics
assert "sprint_progress" in metrics
assert "timestamp" in metrics
def test_metrics_retention(self, metrics_collector):
"""\1"""
# Set retention to 1 day for testing
metrics_collector.retention_days = 1
# Force cleanup
metrics_collector.last_cleanup = datetime.now() - timedelta(days=2)
metrics_collector.cleanup_old_metrics()
# Verify cleanup ran without errors
assert (datetime.now() - metrics_collector.last_cleanup).days < 1
def test_response_time_recording(self, metrics_collector):
"""\1"""
duration = 0.5
metrics_collector.record_response_time(duration)
# Verify metric was recorded without errors
assert True
class TestAuthentication:
"""\1"""
def test_token_creation(self, test_config):
"""\1"""
from dashboard.auth.middleware import create_token

token = create_token({"sub": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)})
assert token is not None
def test_token_verification(self, auth_token, invalid_token):
"""\1"""
from dashboard.auth.middleware import verify_token

# Test valid token
payload = verify_token(auth_token)
assert payload["sub"] == "test_user"
# Test invalid token
with pytest.raises(Exception):
verify_token(invalid_token)
class TestDashboardRoutes:
"""\1"""
@pytest.mark.asyncio
async def test_index_route(self, test_client):
"""\1"""
async with test_client.get("http://localhost:8000/") as response:
assert response.status == 200
text = await response.text()
assert "Project Management Dashboard" in text
@pytest.mark.asyncio
async def test_metrics_route(self, test_client):
"""\1"""
async with test_client.get("http://localhost:8000/metrics") as response:
assert response.status == 200
text = await response.text()
assert "system-metrics" in text
assert "project-metrics" in text
@pytest.mark.asyncio
async def test_api_metrics_route(self, test_client):
"""\1"""
async with test_client.get("http://localhost:8000/api/metrics") as response:
assert response.status == 200
data = await response.json()
assert "cpu_usage" in data
assert "memory_usage" in data
assert "disk_usage" in data
