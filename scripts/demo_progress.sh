#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Initialize progress bar (5 steps)
init_progress 5

echo "🚀 Starting demo..."

# Demo tasks
run_with_spinner "Task 1: Initializing" sleep 2
run_with_spinner "Task 2: Processing" sleep 2
run_with_spinner "Task 3: Analyzing" sleep 2
run_with_spinner "Task 4: Validating" sleep 2
run_with_spinner "Task 5: Completing" sleep 2

echo "✨ Demo completed successfully!"
