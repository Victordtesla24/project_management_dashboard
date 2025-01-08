import pytest
from datetime import datetime, timezone
from unittest.mock import patch, Mock
from prometheus_client import CollectorRegistry
from dashboard.metrics import (
    collect_system_metrics,
    process_metrics,
    get_metrics_summary,
    check_thresholds,
    CPU_GAUGE,
    MEMORY_GAUGE,
    DISK_GAUGE,
    REGISTRY
)

@pytest.fixture
def mock_psutil():
    """Mock psutil functions."""
    with patch('dashboard.metrics.psutil') as mock:
        # Mock CPU
        mock.cpu_percent.return_value = 45.5
        
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 60.2
        mock.virtual_memory.return_value = mock_memory
        
        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 75.8
        mock.disk_usage.return_value = mock_disk
        
        yield mock

@pytest.fixture
def sample_metrics():
    """Sample metrics data."""
    return {
        'cpu_percent': 45.5,
        'memory_percent': 60.2,
        'disk_percent': 75.8,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

def test_collect_system_metrics(mock_psutil):
    """Test collecting system metrics."""
    metrics = collect_system_metrics()
    
    assert isinstance(metrics, dict)
    assert metrics["cpu_percent"] == 45.5
    assert metrics["memory_percent"] == 60.2
    assert metrics["disk_percent"] == 75.8
    assert "timestamp" in metrics
    
    # Verify psutil calls
    mock_psutil.cpu_percent.assert_called_once_with(interval=1)
    mock_psutil.virtual_memory.assert_called_once()
    mock_psutil.disk_usage.assert_called_once_with("/")

def test_process_metrics(sample_metrics):
    """Test processing raw metrics."""
    result = process_metrics(sample_metrics)
    
    assert isinstance(result, dict)
    assert 'metrics' in result
    assert 'status' in result
    assert 'timestamp' in result
    assert 'alerts' in result
    assert result['status'] == 'processed'
    assert result['metrics'] == sample_metrics

def test_get_metrics_summary():
    """Test getting metrics summary."""
    metrics_data = [
        {'cpu_percent': 45.5, 'memory_percent': 60.2, 'disk_percent': 75.8},
        {'cpu_percent': 46.5, 'memory_percent': 61.2, 'disk_percent': 76.8}
    ]
    
    summary = get_metrics_summary(metrics_data)
    
    assert isinstance(summary, dict)
    assert summary["cpu_avg"] == 46.0
    assert summary["memory_avg"] == 60.7
    assert summary["disk_avg"] == 76.3
    assert summary["samples"] == 2

def test_check_thresholds(sample_metrics):
    """Test threshold checking."""
    alerts = check_thresholds(sample_metrics)
    assert isinstance(alerts, list)
    
    # No alerts should be generated for sample metrics
    assert len(alerts) == 0
    
    # Test with metrics above thresholds
    high_metrics = {
        'cpu_percent': 85.0,
        'memory_percent': 95.0,
        'disk_percent': 92.0,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    alerts = check_thresholds(high_metrics)
    assert len(alerts) == 3  # All metrics above threshold

def test_prometheus_registry():
    """Test Prometheus registry setup."""
    assert isinstance(REGISTRY, CollectorRegistry)
    
    # Verify gauges are registered
    assert CPU_GAUGE._name == "system_cpu_usage"
    assert MEMORY_GAUGE._name == "system_memory_usage"
    assert DISK_GAUGE._name == "system_disk_usage"

def test_collect_metrics_error_handling(mock_psutil):
    """Test error handling in metric collection."""
    # Mock CPU error
    mock_psutil.cpu_percent.side_effect = Exception("CPU Error")
    
    metrics = collect_system_metrics()
    assert metrics["cpu_percent"] == 0.0  # Should return default value
    assert metrics["memory_percent"] == 0.0
    assert metrics["disk_percent"] == 0.0
    assert "timestamp" in metrics

def test_process_metrics_error_handling():
    """Test error handling in metrics processing."""
    # Test missing fields
    with pytest.raises(ValueError, match="Missing required fields"):
        process_metrics({})
    
    # Test invalid numeric fields
    invalid_metrics = {
        'cpu_percent': 'invalid',
        'memory_percent': 60.2,
        'disk_percent': 75.8,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    with pytest.raises(ValueError, match="Field cpu_percent must be numeric"):
        process_metrics(invalid_metrics)

def test_get_metrics_summary_error_handling():
    """Test error handling in metrics summary."""
    # Test empty data
    summary = get_metrics_summary([])
    assert summary["samples"] == 0
    assert summary["cpu_avg"] == 0.0
    assert summary["memory_avg"] == 0.0
    assert summary["disk_avg"] == 0.0

def test_metrics_timestamp():
    """Test metrics timestamp generation."""
    metrics = collect_system_metrics()
    timestamp = datetime.fromisoformat(metrics["timestamp"].replace('Z', '+00:00'))
    
    assert isinstance(timestamp, datetime)
    assert timestamp.tzinfo is not None  # Should be timezone-aware
    assert abs((datetime.now(timezone.utc) - timestamp).total_seconds()) < 5  # Should be recent

if __name__ == '__main__':
    pytest.main([__file__])
