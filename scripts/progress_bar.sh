#!/bin/bash

# Simple ASCII progress bar implementation
# Usage: ./progress_bar.sh [current] [total] [label]

show_progress() {
    local current=$1
    local total=$2
    local label=${3:-"Progress"}
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))

    # Create the progress bar string
    printf "\r%s [" "$label"
    printf "%${filled}s" "" | tr ' ' '='
    printf "%${empty}s" "" | tr ' ' ' '
    printf "] %d%%" "$percentage"

    # Print newline if complete
    if [ "$current" -eq "$total" ]; then
        printf "\n"
    fi
}

# If script is run directly, use arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -lt 2 ]; then
        echo "Usage: $0 current total [label]"
        exit 1
    fi
    show_progress "$1" "$2" "${3:-Progress}"
fi
