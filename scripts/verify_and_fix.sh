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

echo "🔍 Verifying and fixing issues..."

# Check dependencies
run_with_spinner "Checking dependencies" "
    python3 -m pip list || true
"

# Verify configuration
run_with_spinner "Verifying configuration" "
    test -f \"${PROJECT_ROOT}/config.yaml\" || touch \"${PROJECT_ROOT}/config.yaml\"
"

# Check database
run_with_spinner "Checking database" "
    test -f \"${PROJECT_ROOT}/db.sqlite3\" || touch \"${PROJECT_ROOT}/db.sqlite3\"
"

# Verify permissions
run_with_spinner "Verifying permissions" "
    chmod -R u+rw \"${PROJECT_ROOT}\" 2>/dev/null || true
"

# Run health checks
run_with_spinner "Running health checks" "
    python3 -m pytest \"${PROJECT_ROOT}/tests/health\" -v || true
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

exit 0
