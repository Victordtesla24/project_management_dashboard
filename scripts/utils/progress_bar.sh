#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
RESET='\033[0m'

# Rich spinner characters
SPINNER_CHARS='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
SPINNER_DELAY=0.1

# Rich progress bar characters
BAR_DONE='█'
BAR_HALF='▌'
BAR_TODO='░'
BAR_WIDTH=40

# Progress tracking (use existing values if set)
CURRENT_STEP=${CURRENT_STEP:-0}
TOTAL_STEPS=${TOTAL_STEPS:-1}

# Initialize progress tracking
init_progress() {
    TOTAL_STEPS=$1
    CURRENT_STEP=0
    export TOTAL_STEPS
    export CURRENT_STEP
}

# Draw progress bar
draw_progress_bar() {
    local percentage=$1
    local width=$2

    # Ensure percentage is between 0 and 100
    [ $percentage -lt 0 ] && percentage=0
    [ $percentage -gt 100 ] && percentage=100

    local done=$(($percentage * $width / 100))
    local half=$((($percentage * $width * 2 / 100) % 2))
    local todo=$(($width - $done - $half))

    # Ensure done, half and todo are non-negative
    [ $done -lt 0 ] && done=0
    [ $half -lt 0 ] && half=0
    [ $todo -lt 0 ] && todo=0

    local bar=""
    bar+=$(printf "%${done}s" | tr ' ' "$BAR_DONE")
    [ $half -eq 1 ] && bar+="$BAR_HALF"
    bar+=$(printf "%${todo}s" | tr ' ' "$BAR_TODO")
    printf "│%s│ %3d%%" "$bar" "$percentage"
}

# Update progress
update_progress() {
    local step_number=$1
    CURRENT_STEP=$step_number
    [ $CURRENT_STEP -gt $TOTAL_STEPS ] && CURRENT_STEP=$TOTAL_STEPS
    export CURRENT_STEP
}

# Run command with spinner
run_with_spinner() {
    local script_name=$1
    local cmd=$2
    local log_file="/tmp/setup_progress.$$.log"

    local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    [ $percentage -gt 100 ] && percentage=100

    # Show initial status with rich spinner
    printf "\r\033[K%b%s%b %s %s" "${BLUE}" "${SPINNER_CHARS:0:1}" "${RESET}" "$script_name" "$(draw_progress_bar $percentage $BAR_WIDTH)"

    # Run the command and capture its output
    eval "$cmd" >"$log_file" 2>&1
    local status=$?

    # Show final status with rich symbols
    if [ $status -eq 0 ]; then
        printf "\r\033[K%b✓%b %s %s\n" "${GREEN}" "${RESET}" "$script_name" "$(draw_progress_bar $percentage $BAR_WIDTH)"
    else
        printf "\r\033[K%b✗%b %s %s\n" "${RED}" "${RESET}" "$script_name" "$(draw_progress_bar $percentage $BAR_WIDTH)"
        echo "Command failed with status $status. Output:" >&2
        cat "$log_file" >&2
    fi

    rm -f "$log_file"
    return $status
}
