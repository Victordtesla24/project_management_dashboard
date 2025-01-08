import pytest
import asyncio
import json
from datetime import datetime, timezone, timedelta
import jwt
import websockets
from websockets.exceptions import ConnectionClosed
from unittest.mock import patch, AsyncMock, Mock
from dashboard.websocket.server import MetricsWebSocket
from dashboard.config.schema import ConfigManager, SchemaValidationError
from dashboard.auth.middleware import auth_required
from contextlib import asynccontextmanager

@pytest.fixture
def config_path(tmp_path):
    config = {
        "environment": "dev",
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "dashboard"
        },
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "test-token",
            "org": "test-org",
            "bucket": "test-bucket"
        },
        "websocket": {
            "host": "localhost",
            "port": 8765
        },
        "metrics": {
            "collection_interval": 1,
            "enabled_metrics": ["cpu", "memory", "disk"]
        },
        "logging": {
            "level": "INFO",
            "file": "dashboard.log"
        }
    }
    
    config_file = tmp_path / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return str(config_file)

@pytest.fixture
def valid_token():
    payload = {
        'user_id': 1,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, 'secret', algorithm='HS256')

class MockWebSocket:
    """Custom WebSocket mock for testing."""
    def __init__(self, headers=None):
        self.headers = headers or {}
        self.messages = asyncio.Queue()
        self.closed = asyncio.Event()
        self.send = AsyncMock(side_effect=self._handle_send)
        self.wait_closed = AsyncMock(side_effect=self._handle_wait_closed)
        
    async def _handle_send(self, message):
        await self.messages.put(json.loads(message))
        
    async def _handle_wait_closed(self):
        await self.closed.wait()
        raise ConnectionClosed(None, None)
        
    async def close(self):
        self.closed.set()

@asynccontextmanager
async def websocket_connection(metrics_ws, mock_websocket):
    """Context manager for testing WebSocket connections."""
    # Start connection in background
    task = asyncio.create_task(metrics_ws.register(mock_websocket))
    
    try:
        # Wait for initial message
        initial_message = await asyncio.wait_for(mock_websocket.messages.get(), timeout=1.0)
        
        # Verify connection is registered
        assert mock_websocket in metrics_ws.connections, "WebSocket connection not registered"
        
        yield initial_message
    finally:
        # Close connection
        await mock_websocket.close()
        # Cancel registration task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
class TestDashboardIntegration:
    async def test_config_websocket_integration(self, config_path):
        """Test that WebSocket server properly loads and uses configuration"""
        with patch('dashboard.websocket.server.InfluxDBClient') as mock_influx:
            mock_client = Mock()
            mock_client.write_api.return_value = Mock()
            mock_client.query_api.return_value = Mock()
            mock_influx.return_value = mock_client
            
            metrics_ws = MetricsWebSocket(config_path)
            
            # Verify config was loaded correctly
            assert metrics_ws.config["websocket"]["port"] == 8765
            assert "cpu" in metrics_ws.enabled_metrics
            
            # Verify InfluxDB was initialized with config values
            mock_influx.assert_called_once_with(
                url="http://localhost:8086",
                token="test-token",
                org="test-org"
            )

    async def test_metric_collection_storage_flow(self, config_path):
        """Test the full flow of collecting metrics and storing them"""
        with patch('dashboard.websocket.server.InfluxDBClient') as mock_influx:
            mock_client = Mock()
            mock_write_api = Mock()
            mock_client.write_api.return_value = mock_write_api
            mock_client.query_api.return_value = Mock()
            mock_influx.return_value = mock_client
            
            metrics_ws = MetricsWebSocket(config_path)
            
            # Mock metric gathering functions
            metrics_ws.get_cpu_usage = AsyncMock(return_value=50.0)
            metrics_ws.get_memory_usage = AsyncMock(return_value=60.0)
            metrics_ws.get_disk_usage = AsyncMock(return_value=70.0)
            
            # Start metric collection
            collection_task = asyncio.create_task(metrics_ws.collect_metrics())
            
            # Wait for one collection cycle
            await asyncio.sleep(1.1)
            
            # Cancel collection task
            collection_task.cancel()
            
            # Verify metrics were stored in InfluxDB
            assert mock_write_api.write.call_count >= 3  # One call per metric
            
            # Verify the written points contain correct data
            calls = mock_write_api.write.call_args_list
            points = [call[1]['record'] for call in calls]
            
            metric_names = [p._name for p in points]
            assert 'cpu_usage' in metric_names
            assert 'memory_usage' in metric_names
            assert 'disk_usage' in metric_names

    async def test_websocket_authentication_flow(self, config_path, valid_token):
        """Test WebSocket connection with authentication."""
        with patch('dashboard.websocket.server.InfluxDBClient') as mock_influx:
            # Create mock InfluxDB client with proper query response
            mock_client = Mock()
            mock_write_api = Mock()
            mock_query_api = Mock()
            
            # Mock query response
            mock_records = [
                Mock(
                    get_measurement=lambda: "cpu_usage",
                    get_time=lambda: datetime.now(timezone.utc),
                    get_value=lambda: 50.0
                )
            ]
            mock_table = Mock(records=mock_records)
            mock_query_api.query.return_value = [mock_table]
            
            mock_client.write_api.return_value = mock_write_api
            mock_client.query_api.return_value = mock_query_api
            mock_influx.return_value = mock_client
            
            metrics_ws = MetricsWebSocket(config_path)
            
            # Create custom WebSocket mock
            mock_websocket = MockWebSocket(headers={'Authorization': valid_token})
            
            async with websocket_connection(metrics_ws, mock_websocket) as initial_message:
                # Verify initial data format
                assert initial_message["type"] == "initial_data"
                assert isinstance(initial_message["data"], dict)

    async def test_config_update_propagation(self, config_path):
        """Test that configuration updates propagate to WebSocket server"""
        with patch('dashboard.websocket.server.InfluxDBClient') as mock_influx:
            # Setup mock InfluxDB client
            mock_client = Mock()
            mock_write_api = Mock()
            mock_query_api = Mock()
            mock_client.write_api.return_value = mock_write_api
            mock_client.query_api.return_value = mock_query_api
            mock_influx.return_value = mock_client
            
            # Initialize WebSocket server
            metrics_ws = MetricsWebSocket(config_path)
            original_interval = metrics_ws.collection_interval
            original_metrics = metrics_ws.enabled_metrics.copy()
            
            # Update configuration with complete config
            new_config = {
                "environment": "dev",
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "dashboard"
                },
                "influxdb": {
                    "url": "http://localhost:8086",
                    "token": "test-token",
                    "org": "test-org",
                    "bucket": "test-bucket"
                },
                "websocket": {
                    "host": "localhost",
                    "port": 8765
                },
                "metrics": {
                    "collection_interval": 5,
                    "enabled_metrics": ["cpu", "memory"]  # Removed disk
                }
            }
            
            # Apply update and reload configuration
            update_result = metrics_ws.config_manager.update_config(new_config)
            
            # Verify update was successful
            assert update_result.is_valid
            assert len(update_result.errors) == 0
            
            # Reload configuration
            metrics_ws.reload_config()
            
            # Verify changes were propagated
            assert metrics_ws.collection_interval == 5  # New interval
            assert metrics_ws.collection_interval != original_interval
            assert metrics_ws.enabled_metrics == set(["cpu", "memory"])
            assert "disk" not in metrics_ws.enabled_metrics
            assert metrics_ws.enabled_metrics != original_metrics
            
            # Verify config file was updated
            with open(config_path) as f:
                saved_config = json.load(f)
                assert saved_config["metrics"]["collection_interval"] == 5
                assert set(saved_config["metrics"]["enabled_metrics"]) == set(["cpu", "memory"])

    async def test_error_handling_integration(self, config_path):
        """Test error handling across components"""
        with patch('dashboard.websocket.server.InfluxDBClient') as mock_influx:
            # Setup mock InfluxDB client with error behavior
            mock_client = Mock()
            mock_write_api = Mock()
            mock_query_api = Mock()
            
            # Mock write API to raise error
            mock_write_api.write.side_effect = Exception("InfluxDB Error")
            mock_client.write_api.return_value = mock_write_api
            
            # Mock query API to raise error
            mock_query_api.query.side_effect = Exception("InfluxDB Query Error")
            mock_client.query_api.return_value = mock_query_api
            
            mock_influx.return_value = mock_client
            
            metrics_ws = MetricsWebSocket(config_path)
            
            # Mock metric gathering
            metrics_ws.get_cpu_usage = AsyncMock(return_value=50.0)
            metrics_ws.get_memory_usage = AsyncMock(return_value=60.0)
            metrics_ws.get_disk_usage = AsyncMock(return_value=70.0)
            
            # Test error handling in different scenarios
            
            # 1. Test metric collection error handling
            collection_task = asyncio.create_task(metrics_ws.collect_metrics())
            await asyncio.sleep(0.1)  # Give time for one collection cycle
            collection_task.cancel()
            
            # Verify write error was handled
            mock_write_api.write.assert_called()
            
            # 2. Test WebSocket connection error handling
            mock_websocket = MockWebSocket()
            async with websocket_connection(metrics_ws, mock_websocket) as initial_message:
                assert "error" in initial_message  # Should contain error info
            
            # 3. Test configuration update error handling
            with pytest.raises(SchemaValidationError):
                await metrics_ws.config_manager.update_config({
                    "metrics": {
                        "collection_interval": -1  # Invalid value
                    }
                })
            
            # Verify server remains operational
            assert metrics_ws.influx_client is not None
            assert not metrics_ws.tasks  # No crashed tasks
            assert metrics_ws.enabled_metrics is not None

if __name__ == '__main__':
    pytest.main([__file__])
