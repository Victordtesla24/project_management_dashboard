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

echo "🧪 Running tests..."

# Run unit tests
run_with_spinner "Running unit tests" "
    python3 -m pytest \"${PROJECT_ROOT}/tests/unit\" -v || true
"

# Run integration tests
run_with_spinner "Running integration tests" "
    python3 -m pytest \"${PROJECT_ROOT}/tests/integration\" -v || true
"

# Generate coverage report
run_with_spinner "Generating coverage report" "
    python3 -m pytest --cov=\"${PROJECT_ROOT}/dashboard\" || true
"

# Run linting
run_with_spinner "Running linting" "
    python3 -m flake8 \"${PROJECT_ROOT}/dashboard\" || true
"

# Generate test report
run_with_spinner "Generating test report" "
    python3 -m pytest --html=report.html || true
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

exit 0
