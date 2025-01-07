#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Save original progress values
_ORIG_CURRENT_STEP=$CURRENT_STEP
_ORIG_TOTAL_STEPS=$TOTAL_STEPS

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=3
init_progress $TOTAL_STEPS

# Install mypy
run_with_spinner "Installing mypy" "
    pip install -q mypy || { echo 'Error: Failed to install mypy' >&2; exit 1; }
"

# Install type stubs for dependencies
run_with_spinner "Installing type stubs" "
    pip install -q types-requests types-PyYAML types-python-dateutil || { echo 'Error: Failed to install type stubs' >&2; exit 1; }
"

# Create mypy configuration
run_with_spinner "Creating mypy configuration" "
    if [ ! -f mypy.ini ]; then
        cat > mypy.ini << 'EOL' || { echo 'Error: Failed to create mypy.ini' >&2; exit 1; }
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True

[mypy.plugins.numpy.*]
ignore_missing_imports = True

[mypy.plugins.pandas.*]
ignore_missing_imports = True
EOL
    fi
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS
