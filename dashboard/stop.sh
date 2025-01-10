#!/bin/bash

# Import utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/utils/common.sh"
source "$SCRIPT_DIR/../scripts/utils/logger.sh"

# Function to stop a service by PID file
stop_service() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        log_info "Stopping $service_name..."
        pid=$(cat "$pid_file")

        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            # Wait for process to stop
            for i in {1..10}; do
                if ! ps -p $pid > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                log_warning "Force stopping $service_name..."
                kill -9 $pid 2>/dev/null || true
            fi
            log_success "$service_name stopped"
        else
            log_warning "$service_name is not running"
        fi

        rm -f "$pid_file"
    else
        log_warning "$service_name is not running (no PID file)"
    fi
}

# Function to stop InfluxDB
stop_influxdb() {
    log_info "Stopping InfluxDB..."
    if pgrep influxd > /dev/null; then
        pkill influxd || true
        # Wait for process to stop
        for i in {1..10}; do
            if ! pgrep influxd > /dev/null; then
                break
            fi
            sleep 1
        done
        # Force kill if still running
        if pgrep influxd > /dev/null; then
            log_warning "Force stopping InfluxDB..."
            pkill -9 influxd || true
        fi
        log_success "InfluxDB stopped"
    else
        log_warning "InfluxDB is not running"
    fi
}

# Function to clean up temporary files
cleanup_temp_files() {
    log_info "Cleaning up temporary files..."

    # Backup logs before cleaning
    local backup_dir="logs/backup_$(date +%Y%m%d_%H%M%S)"
    ensure_directory "$backup_dir"

    if [ -d "logs" ]; then
        cp -r logs/*.log "$backup_dir/" 2>/dev/null || true
    fi

    # Clean up directories
    rm -rf logs/*.log
    rm -rf instance/*
    rm -rf __pycache__
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -f .coverage

    log_success "Cleanup complete (logs backed up to $backup_dir)"
}

# Main function
main() {
    log_info "Stopping all services..."

    # Stop services
    stop_service ".implementation.pid" "Flask application"
    stop_service ".websocket.pid" "WebSocket server"
    stop_service ".monitor.pid" "Monitoring service"
    stop_influxdb

    # Clean up PID files
    rm -f .implementation.pid .websocket.pid .monitor.pid

    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        log_info "Deactivating virtual environment..."
        deactivate
    fi

    log_success "All services stopped successfully"

    # Optional cleanup
    read -p "Do you want to clean up temporary files? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup_temp_files
    fi
}

# Run main function
main "$@"
