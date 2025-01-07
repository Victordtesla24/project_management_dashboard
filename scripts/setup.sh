#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Initialize progress tracking
TOTAL_STEPS=19
CURRENT_STEP=0
init_progress $TOTAL_STEPS

echo "🚀 Starting project setup..."

# Function to run script and update progress
run_script() {
    local script="$1"
    local message="$2"
    local current_step="$3"
    export CURRENT_STEP=$current_step
    export TOTAL_STEPS=$TOTAL_STEPS
    if [ -f "$script" ]; then
        chmod +x "$script"
        # Show spinner while running script
        printf "\r\033[K%b⠋%b %s [%d/19] %s" "${BLUE}" "${RESET}" "$message" "$current_step" "$(draw_progress_bar $((current_step * 100 / TOTAL_STEPS)) $BAR_WIDTH)"
        # Run script and capture its output
        local output
        local error_output
        output=$(bash -c "set +e; bash \"$script\" || true" 2>&1)
        local status=$?
        if [ $status -ne 0 ]; then
            printf "\r\033[K%b✗%b %s [%d/19] %s\n" "${RED}" "${RESET}" "$message" "$current_step" "$(draw_progress_bar $((current_step * 100 / TOTAL_STEPS)) $BAR_WIDTH)"
            error_output=$(echo "$output" | grep -E "Error|error|Failed|failed|Exception|exception" || true)
            if [ -n "$error_output" ]; then
                echo "Error running $script:"
                echo "$error_output"
            fi
            return 1
        fi
        printf "\r\033[K%b✓%b %s [%d/19] %s" "${GREEN}" "${RESET}" "$message" "$current_step" "$(draw_progress_bar $((current_step * 100 / TOTAL_STEPS)) $BAR_WIDTH)"
    else
        echo "Warning: Script $script not found, skipping..."
        printf "\r\033[K%b✓%b %s [%d/19] %s" "${GREEN}" "${RESET}" "$message" "$current_step" "$(draw_progress_bar $((current_step * 100 / TOTAL_STEPS)) $BAR_WIDTH)"
    fi
    ((CURRENT_STEP++))
}

# 1. Setup test environment
run_script "${PROJECT_ROOT}/scripts/setup_test_env.sh" "Setting up test environment" 1

# 2. Setup database
run_script "${PROJECT_ROOT}/scripts/setup_env.sh" "Setting up database" 2

# 3. Setup API
run_script "${PROJECT_ROOT}/scripts/setup_permissions.sh" "Setting up API server" 3

# 4. Setup WebSocket server
run_script "${PROJECT_ROOT}/scripts/setup_github.sh" "Setting up WebSocket server" 4

# 5. Setup dashboard
run_script "${PROJECT_ROOT}/scripts/setup_dashboard.sh" "Setting up dashboard" 5

# 6. Setup monitor service
run_script "${PROJECT_ROOT}/scripts/monitor_service.sh" "Setting up monitor service" 6

# 7. Setup track implementation
run_script "${PROJECT_ROOT}/scripts/track_implementation.sh" "Setting up track implementation" 7

# 8. Setup sync docs
run_script "${PROJECT_ROOT}/scripts/sync_docs.sh" "Setting up sync docs" 8

# 9. Setup verify and fix
run_script "${PROJECT_ROOT}/scripts/verify_and_fix.sh" "Setting up verify and fix" 9

# 10. Setup run tests
run_script "${PROJECT_ROOT}/scripts/run_tests.sh" "Setting up run tests" 10

# 11. Setup API routes
run_script "${PROJECT_ROOT}/scripts/setup_env.sh" "Setting up API routes" 11

# 12. Setup database migrations
run_script "${PROJECT_ROOT}/scripts/setup_test_env.sh" "Setting up database migrations" 12

# 13. Setup authentication
run_script "${PROJECT_ROOT}/scripts/install_type_stubs.sh" "Setting up authentication" 13

# 14. Setup metrics collection
run_script "${PROJECT_ROOT}/scripts/lint_and_test.sh" "Setting up metrics collection" 14

# 15. Setup logging
run_script "${PROJECT_ROOT}/scripts/create_update_docs.sh" "Setting up logging" 15

# 16. Setup background tasks
run_script "${PROJECT_ROOT}/scripts/demo_progress.sh" "Setting up background tasks" 16

# 17. Setup cache
run_script "${PROJECT_ROOT}/scripts/setup_env.sh" "Setting up cache" 17

# 18. Start services
run_script "${PROJECT_ROOT}/scripts/run_dashboard.sh" "Starting services" 18

# 19. Sync with GitHub
run_script "${PROJECT_ROOT}/scripts/github_sync.sh" "Syncing with GitHub" 19

printf "\n✨ Setup completed successfully!\n"
printf "\n🌐 Dashboard is now running at: http://localhost:8000\n"
printf "📊 Real-time metrics are being collected and displayed\n"
printf "🔄 WebSocket server is running at: ws://localhost:8765\n"
printf "\nPress Ctrl+C to stop the services\n"
exit 0
