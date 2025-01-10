#!/bin/bash

# Import common utilities if not already imported
if [ -z "$COMMON_IMPORTED" ]; then
    # shellcheck source=./common.sh
    source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
    COMMON_IMPORTED=1
fi

# Default log settings
LOG_LEVEL=${LOG_LEVEL:-"INFO"}
LOG_FILE=${LOG_FILE:-"logs/dashboard.log"}
LOG_MAX_SIZE=${LOG_MAX_SIZE:-10485760}  # 10MB
LOG_BACKUP_COUNT=${LOG_BACKUP_COUNT:-5}
LOG_FORMAT='%Y-%m-%d %H:%M:%S'

# Log levels
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARNING"]=2
    ["ERROR"]=3
    ["CRITICAL"]=4
)

# Function to initialize logging
init_logging() {
    local log_dir
    log_dir=$(dirname "$LOG_FILE")

    # Create log directory if it doesn't exist
    ensure_directory "$log_dir"

    # Create log file if it doesn't exist
    if [ ! -f "$LOG_FILE" ]; then
        touch "$LOG_FILE"
        print_success "Created log file: $LOG_FILE"
    fi

    # Set up log rotation
    setup_log_rotation
}

# Function to set log level
set_log_level() {
    local level=$1
    if [[ -n "${LOG_LEVELS[$level]}" ]]; then
        LOG_LEVEL=$level
        print_success "Log level set to $LOG_LEVEL"
    else
        print_error "Invalid log level: $level"
        print_info "Valid levels: ${!LOG_LEVELS[*]}"
        return 1
    fi
}

# Function to check if message should be logged
should_log() {
    local level=$1
    [[ ${LOG_LEVELS[$level]} -ge ${LOG_LEVELS[$LOG_LEVEL]} ]]
}

# Function to format log message
format_log_message() {
    local level=$1
    local message=$2
    local timestamp
    timestamp=$(date +"$LOG_FORMAT")
    echo "[$timestamp] [$level] $message"
}

# Function to write to log file
write_log() {
    local formatted_message=$1
    echo "$formatted_message" >> "$LOG_FILE"
}

# Function to rotate logs
rotate_log() {
    local log_size
    log_size=$(stat -f%z "$LOG_FILE")

    if [ "$log_size" -gt "$LOG_MAX_SIZE" ]; then
        # Rotate existing backup logs
        for i in $(seq $((LOG_BACKUP_COUNT - 1)) -1 1); do
            if [ -f "${LOG_FILE}.$i" ]; then
                mv "${LOG_FILE}.$i" "${LOG_FILE}.$((i + 1))"
            fi
        done

        # Backup current log
        mv "$LOG_FILE" "${LOG_FILE}.1"
        touch "$LOG_FILE"

        # Remove old logs
        if [ -f "${LOG_FILE}.$((LOG_BACKUP_COUNT + 1))" ]; then
            rm "${LOG_FILE}.$((LOG_BACKUP_COUNT + 1))"
        fi

        print_success "Rotated log file"
    fi
}

# Function to set up log rotation
setup_log_rotation() {
    # Check log size before each write
    trap rotate_log DEBUG
}

# Logging functions
log_debug() {
    if should_log "DEBUG"; then
        local formatted_message
        formatted_message=$(format_log_message "DEBUG" "$1")
        write_log "$formatted_message"
        print_color "$BLUE" "$formatted_message"
    fi
}

log_info() {
    if should_log "INFO"; then
        local formatted_message
        formatted_message=$(format_log_message "INFO" "$1")
        write_log "$formatted_message"
        print_color "$GREEN" "$formatted_message"
    fi
}

log_warning() {
    if should_log "WARNING"; then
        local formatted_message
        formatted_message=$(format_log_message "WARNING" "$1")
        write_log "$formatted_message"
        print_color "$YELLOW" "$formatted_message"
    fi
}

log_error() {
    if should_log "ERROR"; then
        local formatted_message
        formatted_message=$(format_log_message "ERROR" "$1")
        write_log "$formatted_message"
        print_color "$RED" "$formatted_message"
    fi
}

log_critical() {
    if should_log "CRITICAL"; then
        local formatted_message
        formatted_message=$(format_log_message "CRITICAL" "$1")
        write_log "$formatted_message"
        print_color "$RED" "$formatted_message"
    fi
}

# Function to get recent logs
get_recent_logs() {
    local lines=${1:-10}
    tail -n "$lines" "$LOG_FILE"
}

# Function to search logs
search_logs() {
    local pattern=$1
    local context=${2:-0}
    grep -A "$context" -B "$context" "$pattern" "$LOG_FILE"
}

# Function to clear logs
clear_logs() {
    local backup="${LOG_FILE}.$(date +%Y%m%d_%H%M%S).bak"
    cp "$LOG_FILE" "$backup"
    : > "$LOG_FILE"
    print_success "Logs cleared (backup created: $backup)"
}

# Function to analyze logs
analyze_logs() {
    local hours=${1:-24}
    local since
    since=$(date -v-"${hours}"H +"%Y-%m-%d %H:%M:%S")

    echo "Log Analysis (last $hours hours):"
    echo "--------------------------------"
    echo "Error count: $(grep -c "ERROR" "$LOG_FILE")"
    echo "Warning count: $(grep -c "WARNING" "$LOG_FILE")"
    echo "Critical count: $(grep -c "CRITICAL" "$LOG_FILE")"
    echo
    echo "Most common errors:"
    grep "ERROR" "$LOG_FILE" | sort | uniq -c | sort -nr | head -5
}

# Export functions
export -f init_logging
export -f set_log_level
export -f log_debug
export -f log_info
export -f log_warning
export -f log_error
export -f log_critical
export -f get_recent_logs
export -f search_logs
export -f clear_logs
export -f analyze_logs

# Initialize logging
init_logging
