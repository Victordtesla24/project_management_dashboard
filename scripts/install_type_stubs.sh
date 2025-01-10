#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Activate virtual environment
if [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "${PROJECT_ROOT}/.venv/bin/activate"
else
    handle_error "Virtual environment not found. Please run setup.sh first."
fi

# Validate pip installation
if ! command -v pip >/dev/null 2>&1; then
    handle_error "pip not found in virtual environment"
fi

# Create stubs directory structure
echo "Setting up type stubs directory structure..."
STUBS_DIR="${PROJECT_ROOT}/dashboard/stubs"
mkdir -p "$STUBS_DIR" || handle_error "Failed to create stubs directory"

# Define required type stubs
type_stubs=(
    "types-requests"
    "types-PyYAML"
    "types-setuptools"
    "types-six"
    "types-urllib3"
    "types-redis"
    "types-Flask"
    "types-SQLAlchemy"
    "types-click"
    # Note: pytest ships with its own type hints, no need for types-pytest
)

# Install type stubs
echo "Installing type stubs..."
for stub_package in "${type_stubs[@]}"; do
    echo "Installing $stub_package..."
    pip install --upgrade "$stub_package" || {
        echo "⚠️  Warning: Failed to install $stub_package"
        continue
    }
done

# Create stub template files
echo "Creating stub templates..."

# Create __init__.py with package information
cat > "${STUBS_DIR}/__init__.py" << 'EOF' || handle_error "Failed to create __init__.py"
"""Type stubs for project-specific modules."""

from typing import Any, Dict, List, Optional, Union

# Add project-specific type definitions here
ConfigDict = Dict[str, Any]
MetricsData = Dict[str, Union[int, float, str]]
EOF

# Create py.typed file (PEP 561)
touch "${STUBS_DIR}/py.typed" || handle_error "Failed to create py.typed"

# Create custom stubs for project modules
for module in "dashboard" "metrics" "websocket"; do
    stub_file="${STUBS_DIR}/${module}.pyi"
    if [ ! -f "$stub_file" ]; then
        cat > "$stub_file" << EOF || handle_error "Failed to create ${module}.pyi"
"""Type stubs for ${module} module."""

from typing import Any, Dict, List, Optional

# Add type definitions for ${module} module here
EOF
    fi
done

# Set correct permissions
echo "Setting permissions..."
find "$STUBS_DIR" -type f -name "*.py*" -exec chmod 644 {} \;
chmod 644 "${STUBS_DIR}/py.typed"

# Verify installation
echo "Verifying type stub installation..."
missing_stubs=0
for stub_package in "${type_stubs[@]}"; do
    if ! pip show "$stub_package" >/dev/null 2>&1; then
        echo "⚠️  Warning: $stub_package not properly installed"
        missing_stubs=1
    fi
done

if [ $missing_stubs -eq 1 ]; then
    echo "⚠️  Some type stubs were not installed properly. Check the warnings above."
else
    echo "✓ All type stubs installed successfully"
fi

exit 0
