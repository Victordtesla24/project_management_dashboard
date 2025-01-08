import pytest
import asyncio
import json
from dashboard.websocket.server import MetricsWebSocket

@pytest.mark.asyncio
async def test_start_server(config_file, event_loop):
    """Test starting the WebSocket server."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    assert metrics_ws.server is not None
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_register_client(config_file, event_loop):
    """Test client registration."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Simulate client connection
    client = {'id': '123', 'ws': None}
    metrics_ws.register_client(client)
    assert len(metrics_ws.clients) == 1
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_broadcast_message(config_file, event_loop):
    """Test broadcasting messages to clients."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Add test clients
    clients = [
        {'id': '1', 'ws': None},
        {'id': '2', 'ws': None}
    ]
    for client in clients:
        metrics_ws.register_client(client)
    
    # Test broadcast
    message = {'type': 'metrics', 'data': {'cpu': 50}}
    await metrics_ws.broadcast_message(message)
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_collect_metrics(config_file, event_loop):
    """Test metrics collection."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Test metrics collection
    metrics = await metrics_ws.collect_metrics()
    assert isinstance(metrics, dict)
    assert 'cpu_percent' in metrics
    assert 'memory_percent' in metrics
    assert 'disk_percent' in metrics
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_send_initial_data(config_file, event_loop):
    """Test sending initial data to client."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Simulate client
    client = {'id': '123', 'ws': None}
    metrics_ws.register_client(client)
    
    # Test sending initial data
    await metrics_ws.send_initial_data(client)
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_stop_server(config_file, event_loop):
    """Test stopping the WebSocket server."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    await metrics_ws.stop_server()
    assert metrics_ws.server is None

@pytest.mark.asyncio
async def test_error_handling(config_file, event_loop):
    """Test error handling in WebSocket server."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Test invalid message handling
    with pytest.raises(ValueError):
        await metrics_ws.handle_message(None, "invalid message")
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_metric_data_validation(config_file, event_loop):
    """Test metric data validation."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Test invalid metric data
    invalid_data = {'type': 'metrics', 'data': {'invalid': 'data'}}
    with pytest.raises(ValueError):
        await metrics_ws.validate_metric_data(invalid_data)
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_concurrent_clients(config_file, event_loop):
    """Test handling multiple concurrent clients."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Add multiple clients
    clients = [{'id': str(i), 'ws': None} for i in range(5)]
    for client in clients:
        metrics_ws.register_client(client)
    
    assert len(metrics_ws.clients) == 5
    
    await metrics_ws.stop_server()

@pytest.mark.asyncio
async def test_metric_data_creation(config_file, event_loop):
    """Test creating metric data."""
    metrics_ws = MetricsWebSocket(config_file)
    await metrics_ws.start_server()
    
    # Test metric data creation
    data = await metrics_ws.create_metric_data()
    assert isinstance(data, dict)
    assert 'metrics' in data
    assert 'timestamp' in data
    
    await metrics_ws.stop_server()
