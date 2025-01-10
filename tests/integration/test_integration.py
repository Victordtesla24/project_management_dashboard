"""Integration tests for system components."""

import pytest
from pathlib import Path
import json

def test_metrics_collection():
    """Test metrics collection integration."""
    from src.metrics import collect_metrics
    
    # Collect metrics
    metrics = collect_metrics()
    
    # Verify metrics structure
    assert isinstance(metrics, dict)
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert "disk_usage" in metrics
    assert "network_traffic" in metrics

def test_metrics_processing():
    """Test metrics processing integration."""
    from src.metrics import process_metrics
    
    # Sample metrics data
    test_metrics = {
        "cpu_usage": 45.2,
        "memory_usage": 68.7,
        "disk_usage": 72.1,
        "network_traffic": {
            "incoming": 1024,
            "outgoing": 2048
        }
    }
    
    # Process metrics
    processed = process_metrics(test_metrics)
    
    # Verify processing results
    assert isinstance(processed, list)
    assert len(processed) > 0
    assert all(isinstance(item, dict) for item in processed)

def test_metrics_storage():
    """Test metrics storage integration."""
    from src.metrics import store_metrics
    
    # Sample processed metrics
    test_data = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "metric": "cpu_usage",
            "value": 45.2
        },
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "metric": "memory_usage",
            "value": 68.7
        }
    ]
    
    # Store metrics (should not raise exceptions)
    store_metrics(test_data)

def test_end_to_end_flow():
    """Test complete metrics flow from collection to storage."""
    from src.metrics import collect_metrics, process_metrics, store_metrics
    
    # Collect metrics
    raw_metrics = collect_metrics()
    assert raw_metrics is not None
    
    # Process metrics
    processed_metrics = process_metrics(raw_metrics)
    assert processed_metrics is not None
    assert len(processed_metrics) > 0
    
    # Store metrics
    store_metrics(processed_metrics)  # Should not raise exceptions
