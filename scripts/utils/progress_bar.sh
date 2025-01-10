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
TOTAL_STEPS=${TOTAL_STEPS:-20}  # Default to 20 steps (5% each)

# Spinner state
SPINNER_INDEX=0

# Check if this is a subscript of a parent progress
if [ -n "${_PARENT_PROGRESS:-}" ]; then
    return 0
fi

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

    # Round to nearest 5%
    percentage=$(( (percentage + 2) / 5 * 5 ))

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
    printf "│%s│" "$bar"
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
    # Skip if this is a subscript
    if [ -n "${_PARENT_PROGRESS:-}" ]; then
        eval "$2"
        return $?
    fi

    local script_name=$1
    local cmd=$2
    local log_file="/tmp/setup_progress.$$.log"
    local spinner_index=0

    # Run command in background
    eval "$cmd" >"$log_file" 2>&1 &
    local cmd_pid=$!

    # Show spinner while command runs
    while kill -0 $cmd_pid 2>/dev/null; do
        local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
        local spinner_char="${SPINNER_CHARS:$spinner_index:1}"
        # Clear line and print progress
        printf "\r\033[K%b%s%b Running %s %s %3d%%" \
            "${BLUE}" "$spinner_char" "${RESET}" \
            "$script_name" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        spinner_index=$(( (spinner_index + 1) % ${#SPINNER_CHARS} ))
        sleep $SPINNER_DELAY
    done

    wait $cmd_pid
    local status=$?

    if [ $status -eq 0 ]; then
        ((CURRENT_STEP++))
        # Print final state with checkmark
        printf "\r\033[K%b✓%b Running %s %s %3d%%" \
            "${GREEN}" "${RESET}" \
            "$script_name" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
    else
        # Print final state with X
        printf "\r\033[K%b✗%b Running %s %s %3d%%" \
            "${RED}" "${RESET}" \
            "$script_name" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
    fi

    return $status
}
