#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Progress bar settings
BAR_WIDTH=40
SPINNER_CHARS='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
SPINNER_DELAY=0.1

# Initialize progress tracking
CURRENT_STEP=0
TOTAL_STEPS=1

# Initialize progress tracking
init_progress() {
    TOTAL_STEPS=$1
    CURRENT_STEP=0
}

# Draw progress bar
draw_progress_bar() {
    local percent=$1
    local width=$2
    local completed=$((width * percent / 100))
    local remaining=$((width - completed))
    
    printf "│"
    printf "%${completed}s" | tr ' ' '█'
    printf "%${remaining}s" | tr ' ' '░'
    printf "│"
}

# Run command with spinner
run_with_spinner() {
    local message=$1
    local command=$2
    local spinner_index=0
    
    # Calculate percentage based on current step
    local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    
    # Execute command in background
    eval "$command" &
    local command_pid=$!
    
    # Show spinner while command is running
    while kill -0 $command_pid 2>/dev/null; do
        local spinner_char="${SPINNER_CHARS:$spinner_index:1}"
        printf "\r${BLUE}%s${RESET} %s %s %3d%%" \
            "$spinner_char" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        spinner_index=$(( (spinner_index + 1) % ${#SPINNER_CHARS} ))
        sleep $SPINNER_DELAY
    done
    
    # Wait for command to finish and get its exit status
    wait $command_pid
    local status=$?
    
    # Update progress
    ((CURRENT_STEP++))
    percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    
    # Show final state
    if [ $status -eq 0 ]; then
        printf "\r${GREEN}✓${RESET} %s %s %3d%%\n" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
    else
        printf "\r${RED}✗${RESET} %s %s %3d%%\n" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        return $status
    fi
}

# Complete progress
complete_progress() {
    local message=$1
    printf "\r${GREEN}✓${RESET} %s %s %3d%%\n" \
        "$message" \
        "$(draw_progress_bar 100 $BAR_WIDTH)" \
        100
}
