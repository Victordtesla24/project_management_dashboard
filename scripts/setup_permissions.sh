#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# Source utility functions
if [ ! -f "${PROJECT_ROOT}/scripts/utils/progress_bar.sh" ]; then
    echo "Error: progress_bar.sh not found" >&2
    exit 1
fi
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Save original progress values
_ORIG_CURRENT_STEP=$CURRENT_STEP
_ORIG_TOTAL_STEPS=$TOTAL_STEPS

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=5
init_progress $TOTAL_STEPS

echo "🚀 Setting up permissions..."

# Set base directory permissions
run_with_spinner "Setting base permissions" "chmod 755 \"${PROJECT_ROOT}\" 2>/dev/null || true"

# Set directory permissions
run_with_spinner "Setting directory permissions" "find \"${PROJECT_ROOT}\" -type d -exec chmod 755 {} + 2>/dev/null || true"

# Set Python file permissions
run_with_spinner "Setting Python file permissions" "find \"${PROJECT_ROOT}\" -type f -name '*.py' -exec chmod 644 {} + 2>/dev/null || true"

# Set shell script permissions
run_with_spinner "Setting script permissions" "find \"${PROJECT_ROOT}/scripts\" -type f -name '*.sh' -exec chmod 755 {} + 2>/dev/null || true"

# Set configuration file permissions
run_with_spinner "Setting config permissions" "find \"${PROJECT_ROOT}\" -type f \( -name '*.yml' -o -name '*.yaml' -o -name '*.json' -o -name '*.md' -o -name '*.rst' -o -name '*.txt' \) -exec chmod 644 {} + 2>/dev/null || true"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

echo "✨ Permissions setup completed successfully!"
