#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print success message
print_success() {
    print_color "$GREEN" "✓ $1"
}

# Function to print error message
print_error() {
    print_color "$RED" "✗ $1"
}

# Function to print warning message
print_warning() {
    print_color "$YELLOW" "⚠ $1"
}

# Function to print info message
print_info() {
    print_color "$BLUE" "ℹ $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if virtual environment is active
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Virtual environment not activated"
        print_info "Please activate your virtual environment first:"
        print_info "source .venv/bin/activate"
        return 1
    fi
    return 0
}

# Function to check Python version
check_python_version() {
    local required_version=$1
    local python_version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python $required_version or higher is required (found $python_version)"
        return 1
    fi
    print_success "Python version $python_version detected"
    return 0
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -i :"$port" >/dev/null 2>&1; then
        print_error "Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to check if process is running
check_process() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if ps -p "$pid" >/dev/null 2>&1; then
            print_success "$service_name is running (PID: $pid)"
            return 0
        else
            print_error "$service_name is not running (PID: $pid)"
            return 1
        fi
    else
        print_error "$service_name PID file not found"
        return 1
    fi
}

# Function to create directory if it doesn't exist
ensure_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "Created directory: $dir"
    fi
}

# Function to backup file
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        local backup="${file}.$(date +%Y%m%d_%H%M%S).bak"
        cp "$file" "$backup"
        print_success "Created backup: $backup"
    fi
}

# Function to load environment variables
load_env() {
    local env_file=${1:-.env}
    if [ -f "$env_file" ]; then
        # shellcheck disable=SC1090
        source "$env_file"
        print_success "Loaded environment variables from $env_file"
    else
        print_warning "Environment file $env_file not found"
    fi
}

# Function to check required commands
check_requirements() {
    local missing=0
    for cmd in "$@"; do
        if ! command_exists "$cmd"; then
            print_error "Required command not found: $cmd"
            missing=1
        fi
    done
    return $missing
}

# Function to get absolute path
get_absolute_path() {
    local path=$1
    echo "$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
}

# Function to check file permissions
check_permissions() {
    local file=$1
    local required_perms=$2

    if [ ! -e "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi

    local actual_perms
    actual_perms=$(stat -f "%Lp" "$file")
    if [ "$actual_perms" != "$required_perms" ]; then
        print_error "Incorrect permissions for $file: expected $required_perms, got $actual_perms"
        return 1
    fi
    return 0
}

# Function to clean up temporary files
cleanup_temp_files() {
    local dir=${1:-/tmp}
    local pattern=${2:-*}
    local days=${3:-7}

    find "$dir" -name "$pattern" -type f -mtime +"$days" -delete
    print_success "Cleaned up temporary files in $dir older than $days days"
}

# Function to validate JSON file
validate_json() {
    local file=$1
    if ! python3 -c "import json; json.load(open('$file'))"; then
        print_error "Invalid JSON file: $file"
        return 1
    fi
    print_success "Valid JSON file: $file"
    return 0
}

# Function to check disk space
check_disk_space() {
    local min_space=${1:-10} # minimum space in GB
    local disk_space
    disk_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')

    if [ "$disk_space" -lt "$min_space" ]; then
        print_warning "Low disk space: ${disk_space}GB available (minimum: ${min_space}GB)"
        return 1
    fi
    return 0
}

# Function to check memory usage
check_memory() {
    local threshold=${1:-90} # percentage
    local memory_usage
    memory_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ "$memory_usage" -gt "$threshold" ]; then
        print_warning "High memory usage: ${memory_usage}% (threshold: ${threshold}%)"
        return 1
    fi
    return 0
}

# Export functions
export -f print_color
export -f print_success
export -f print_error
export -f print_warning
export -f print_info
export -f command_exists
export -f check_venv
export -f check_python_version
export -f check_port
export -f check_process
export -f ensure_directory
export -f backup_file
export -f load_env
export -f check_requirements
export -f get_absolute_path
export -f check_permissions
export -f cleanup_temp_files
export -f validate_json
export -f check_disk_space
export -f check_memory
