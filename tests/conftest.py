"""Common test fixtures."""

import os
import json
import tempfile
import pytest
import subprocess
import time
import requests
import threading
from pathlib import Path
from urllib.parse import urljoin


@pytest.fixture
def project_root():
    """Get project root directory."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def test_config(tmp_path):
    """Create a temporary test config file."""
    config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db"
        },
        "metrics": {
            "retention": {
                "days": 30
            }
        }
    }
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return str(config_file)


@pytest.fixture
def test_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_metrics():
    """Fixture for mocked metrics data."""
    return {
        "cpu_usage": 45.2,
        "memory_usage": 68.7,
        "disk_usage": 72.1,
        "network_traffic": {
            "incoming": 1024,
            "outgoing": 2048
        }
    }


@pytest.fixture
def mock_session_state():
    """Fixture for mocked Streamlit session state."""
    class MockState:
        def __init__(self):
            self.metrics_history = []
            self.last_update = None
    return MockState()


@pytest.fixture
def mock_make_subplots(mocker):
    """Mock for plotly make_subplots."""
    return mocker.patch("plotly.subplots.make_subplots")


@pytest.fixture
def mock_go(mocker):
    """Mock for plotly graph objects."""
    return mocker.patch("plotly.graph_objects")


@pytest.fixture
def mock_st(mocker):
    """Mock for streamlit."""
    mock = mocker.patch("streamlit")
    mock.plotly_chart = mocker.Mock()
    return mock


def read_server_output(process, stop_event):
    """Read and print server output."""
    while not stop_event.is_set():
        line = process.stdout.readline()
        if line:
            print(f"Server output: {line.decode().strip()}")


@pytest.fixture(scope="session")
def server():
    """Start and stop the server for e2e tests."""
    # Start server
    server_process = subprocess.Popen(
        ["streamlit", "run", "src/run.py", "--server.port=8000", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    
    # Start thread to read server output
    stop_event = threading.Event()
    output_thread = threading.Thread(
        target=lambda: [print(f"Server output: {line}") for line in iter(server_process.stdout.readline, "")]
    )
    output_thread.daemon = True
    output_thread.start()
    
    # Wait for server to start and verify it's running
    base_url = "http://localhost:8000"
    max_retries = 30
    retry_delay = 1
    
    for _ in range(max_retries):
        try:
            response = requests.get(urljoin(base_url, "_stcore/health"))
            if response.status_code == 200:
                print("Server started successfully")
                time.sleep(5)  # Give extra time for app to fully initialize
                break
        except requests.exceptions.ConnectionError:
            print("Waiting for server to start...")
            time.sleep(retry_delay)
    else:
        print("Server failed to start")
        server_process.terminate()
        server_process.wait()
        raise RuntimeError("Failed to start Streamlit server")
    
    yield server_process
    
    # Stop server and output thread
    stop_event.set()
    server_process.terminate()
    server_process.wait(timeout=5)
    output_thread.join(timeout=1)
