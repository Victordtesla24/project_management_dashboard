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

echo "🚀 Setting up environment..."

# Create virtual environment if it doesn't exist
run_with_spinner "Creating virtual environment" "
    if [ ! -d .venv ]; then
        python3 -m venv .venv
    fi
"

# Activate virtual environment
run_with_spinner "Activating virtual environment" "source .venv/bin/activate"

# Install/upgrade pip
run_with_spinner "Upgrading pip" "pip install --upgrade pip"

# Install dependencies
run_with_spinner "Installing dependencies" "pip install -r requirements.txt"

# Set environment variables
run_with_spinner "Setting environment variables" "
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
"

echo "✨ Environment setup completed successfully!"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS
