#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Logging function
log_message() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message"
}

# Error handling
handle_error() {
    log_message "ERROR" "$1"
    exit 1
}

# Verify pytest installation
if ! python3 -c "import pytest" 2>/dev/null; then
    log_message "ERROR" "pytest not found. Please install requirements-dev.txt first"
    exit 1
fi

# Check write permissions
if [ ! -w "${PROJECT_ROOT}" ]; then
    handle_error "No write permission in project directory"
fi

# Clean up old test artifacts with error checking
log_message "INFO" "Cleaning up old test artifacts..."
cleanup_artifacts() {
    local path=$1
    if [ -d "$path" ]; then
        rm -rf "$path" || log_message "WARN" "Failed to remove $path"
    fi
}

cleanup_artifacts "${PROJECT_ROOT}/tests/reports"
cleanup_artifacts "${PROJECT_ROOT}/tests/.pytest_cache"
cleanup_artifacts "${PROJECT_ROOT}/tests/__pycache__"

# Clean up .pyc files
find "${PROJECT_ROOT}/tests" -name "*.pyc" -delete 2>/dev/null ||
    log_message "WARN" "Failed to clean up some .pyc files"

# Create and verify test directory structure
log_message "INFO" "Creating test directory structure..."
test_dirs=(
    "unit"
    "integration"
    "e2e"
    "fixtures"
    "reports"
)

create_and_verify_dir() {
    local dir=$1
    local full_path="${PROJECT_ROOT}/tests/${dir}"

    if ! mkdir -p "$full_path"; then
        handle_error "Failed to create ${dir} directory"
    fi

    if [ ! -d "$full_path" ] || [ ! -w "$full_path" ]; then
        handle_error "Directory ${dir} is not accessible or writable"
    fi

    log_message "INFO" "Created and verified directory: tests/${dir}"
}

for dir in "${test_dirs[@]}"; do
    create_and_verify_dir "$dir"
done

# Create and verify test configuration
log_message "INFO" "Creating test configuration..."
pytest_ini="${PROJECT_ROOT}/tests/pytest.ini"
log_message "INFO" "Writing pytest.ini..."

cat > "$pytest_ini" << 'EOF' || handle_error "Failed to create pytest.ini"
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
# Verify pytest.ini was created and is valid
if [ ! -f "$pytest_ini" ] || [ ! -s "$pytest_ini" ]; then
    handle_error "pytest.ini was not created properly"
fi
log_message "INFO" "Created and verified pytest.ini"

# Create test fixtures if they don't exist
if [ ! -f "${PROJECT_ROOT}/tests/fixtures/conftest.py" ]; then
    echo "Creating test fixtures..."
    echo "Writing conftest.py..."
    cat > "${PROJECT_ROOT}/tests/fixtures/conftest.py" << 'EOF' || handle_error "Failed to create conftest.py"
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
    echo "✓ Created conftest.py"
fi

# Create sample test if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/tests/unit/test_sample.py" ]; then
    echo "Creating sample test..."
    echo "Writing test_sample.py..."
    cat > "${PROJECT_ROOT}/tests/unit/test_sample.py" << 'EOF' || handle_error "Failed to create test_sample.py"
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
    echo "✓ Created test_sample.py"
fi

# Create test data directory
echo "Creating test data directory..."
mkdir -p "${PROJECT_ROOT}/tests/fixtures/data" || handle_error "Failed to create test data directory"
echo "✓ Created test data directory"

# Create .gitkeep to preserve empty directories
echo "Creating .gitkeep file..."
touch "${PROJECT_ROOT}/tests/fixtures/data/.gitkeep" || handle_error "Failed to create .gitkeep"
echo "✓ Created .gitkeep file"

echo "✓ Test environment setup completed"
exit 0
