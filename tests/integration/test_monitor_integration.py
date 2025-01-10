"""Integration tests for monitoring system."""

import pytest
from pathlib import Path
import json

def test_monitor_initialization():
    """Test monitor system initialization."""
    from src.monitor import system
    
    # Initialize monitor
    monitor = system.initialize_monitor()
    
    # Verify monitor state
    assert monitor is not None
    assert hasattr(monitor, 'collect_metrics')
    assert hasattr(monitor, 'process_data')

def test_monitor_data_collection():
    """Test monitor data collection."""
    from src.monitor import system
    
    # Initialize and collect data
    monitor = system.initialize_monitor()
    data = monitor.collect_metrics()
    
    # Verify collected data structure
    assert isinstance(data, dict)
    assert 'timestamp' in data
    assert 'metrics' in data
    assert isinstance(data['metrics'], dict)

def test_monitor_data_processing():
    """Test monitor data processing."""
    from src.monitor import system
    
    # Sample data
    test_data = {
        'timestamp': '2024-01-01T00:00:00Z',
        'metrics': {
            'cpu': 45.2,
            'memory': 68.7,
            'disk': 72.1
        }
    }
    
    # Process data
    monitor = system.initialize_monitor()
    processed = monitor.process_data(test_data)
    
    # Verify processing
    assert isinstance(processed, dict)
    assert 'processed_timestamp' in processed
    assert 'metrics' in processed
    assert processed['metrics'] == test_data['metrics']

def test_monitor_integration_flow():
    """Test complete monitoring flow."""
    from src.monitor import system
    
    # Initialize monitor
    monitor = system.initialize_monitor()
    
    # Collect data
    data = monitor.collect_metrics()
    assert data is not None
    
    # Process data
    processed = monitor.process_data(data)
    assert processed is not None
    
    # Store data (if applicable)
    if hasattr(monitor, 'store_data'):
        monitor.store_data(processed)
