#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Save original progress values
_ORIG_CURRENT_STEP=$CURRENT_STEP
_ORIG_TOTAL_STEPS=$TOTAL_STEPS

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=5
init_progress $TOTAL_STEPS

echo "🧪 Setting up test environment..."

# Create test directories
run_with_spinner "Creating test directories" "
    mkdir -p \"${PROJECT_ROOT}/tests/unit\" &&
    mkdir -p \"${PROJECT_ROOT}/tests/integration\" &&
    mkdir -p \"${PROJECT_ROOT}/tests/e2e\" &&
    mkdir -p \"${PROJECT_ROOT}/tests/fixtures\" &&
    mkdir -p \"${PROJECT_ROOT}/tests/reports\"
"

# Create test configuration
run_with_spinner "Creating test configuration" "
    cat > \"${PROJECT_ROOT}/tests/pytest.ini\" << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=html --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
EOF
"

# Create test fixtures
run_with_spinner "Creating test fixtures" "
    cat > \"${PROJECT_ROOT}/tests/fixtures/conftest.py\" << 'EOF'
import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture(scope='session')
def test_data_dir():
    return Path(__file__).parent / 'data'

@pytest.fixture(scope='function')
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture(scope='session')
def test_config():
    return {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'test_db',
            'user': 'test_user',
            'password': 'test_password'
        },
        'api': {
            'host': 'localhost',
            'port': 8000,
            'debug': True
        },
        'metrics': {
            'collection_interval': 60,
            'retention_days': 30,
            'enabled_metrics': ['cpu', 'memory', 'disk']
        },
        'auth': {
            'secret_key': 'test_secret_key',
            'token_expiry': 3600,
            'algorithm': 'HS256'
        }
    }

@pytest.fixture(scope='function')
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
EOF
"

# Create sample test
run_with_spinner "Creating sample test" "
    cat > \"${PROJECT_ROOT}/tests/unit/test_sample.py\" << 'EOF'
import pytest

def test_sample():
    assert True

@pytest.mark.unit
def test_addition():
    assert 1 + 1 == 2

@pytest.mark.integration
def test_with_fixture(test_config):
    assert test_config['database']['host'] == 'localhost'

@pytest.mark.e2e
@pytest.mark.slow
def test_with_temp_dir(temp_dir):
    assert temp_dir.exists()
    test_file = temp_dir / 'test.txt'
    test_file.write_text('Hello, World!')
    assert test_file.read_text() == 'Hello, World!'
EOF
"

# Set permissions
run_with_spinner "Setting permissions" "
    chmod 644 \"${PROJECT_ROOT}/tests/pytest.ini\" &&
    chmod 644 \"${PROJECT_ROOT}/tests/fixtures/conftest.py\" &&
    chmod 644 \"${PROJECT_ROOT}/tests/unit/test_sample.py\"
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

exit 0
