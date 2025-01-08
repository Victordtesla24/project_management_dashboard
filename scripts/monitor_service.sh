#!/bin/bash

# Exit on error
set -e

# Default values
CHECK_INTERVAL=30  # seconds
LOG_FILE="logs/monitor.log"
METRICS_FILE="logs/metrics.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=90
ALERT_THRESHOLD_DISK=85

# Function to check if a process is running
check_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            return 0
        else
            log_message "WARNING: $service_name is not running (PID: $pid)"
            return 1
        fi
    else
        log_message "WARNING: $service_name PID file not found"
        return 1
    fi
}

# Function to check system resources
check_resources() {
    # CPU usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
    if [ "$cpu_usage" -gt "$ALERT_THRESHOLD_CPU" ]; then
        log_message "ALERT: High CPU usage: ${cpu_usage}%"
    fi
    
    # Memory usage
    memory_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ "$memory_usage" -gt "$ALERT_THRESHOLD_MEMORY" ]; then
        log_message "ALERT: High memory usage: ${memory_usage}%"
    fi
    
    # Disk usage
    disk_usage=$(df -h / | awk 'NR==2 {print int($5)}')
    if [ "$disk_usage" -gt "$ALERT_THRESHOLD_DISK" ]; then
        log_message "ALERT: High disk usage: ${disk_usage}%"
    fi
    
    # Log metrics
    echo "$(date '+%Y-%m-%d %H:%M:%S') CPU:${cpu_usage}% MEM:${memory_usage}% DISK:${disk_usage}%" >> "$METRICS_FILE"
}

# Function to check service health
check_service_health() {
    local url=$1
    local service_name=$2
    
    if curl -s "$url" > /dev/null; then
        return 0
    else
        log_message "WARNING: $service_name health check failed"
        return 1
    fi
}

# Function to check WebSocket connection
check_websocket() {
    local ws_url=$1
    
    if nc -z localhost 8765; then
        return 0
    else
        log_message "WARNING: WebSocket server is not responding"
        return 1
    fi
}

# Function to check InfluxDB connection
check_influxdb() {
    if curl -s "http://localhost:8086/health" > /dev/null; then
        return 0
    else
        log_message "WARNING: InfluxDB is not responding"
        return 1
    fi
}

# Function to log messages
log_message() {
    local message=$1
    echo "$(date '+%Y-%m-%d %H:%M:%S') $message" >> "$LOG_FILE"
    echo "$message"
}

# Function to rotate logs
rotate_logs() {
    for log_file in "$LOG_FILE" "$METRICS_FILE"; do
        if [ -f "$log_file" ]; then
            if [ $(stat -f%z "$log_file") -gt 10485760 ]; then  # 10MB
                mv "$log_file" "${log_file}.$(date +%Y%m%d)"
                gzip "${log_file}.$(date +%Y%m%d)"
            fi
        fi
    done
}

# Function to check log sizes
check_logs() {
    # Check and clean old log files (older than 7 days)
    find logs/ -name "*.gz" -mtime +7 -delete
    
    # Rotate current logs if needed
    rotate_logs
}

# Function to show service status
show_status() {
    echo "Service Status:"
    echo "---------------"
    
    # Check Flask application
    if check_process ".implementation.pid" "Flask application"; then
        echo "✓ Flask application is running"
    else
        echo "✗ Flask application is not running"
    fi
    
    # Check WebSocket server
    if check_process ".websocket.pid" "WebSocket server"; then
        echo "✓ WebSocket server is running"
    else
        echo "✗ WebSocket server is not running"
    fi
    
    # Check monitoring service
    if check_process ".monitor.pid" "Monitoring service"; then
        echo "✓ Monitoring service is running"
    else
        echo "✗ Monitoring service is not running"
    fi
    
    # Check system resources
    echo
    echo "System Resources:"
    echo "----------------"
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
    memory_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    disk_usage=$(df -h / | awk 'NR==2 {print $5}')
    
    echo "CPU Usage:    $cpu_usage%"
    echo "Memory Usage: $memory_usage%"
    echo "Disk Usage:   $disk_usage"
}

# Function to show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --status      Show current service status"
    echo "  --interval N  Set check interval in seconds (default: 30)"
    echo "  --help        Show this help message"
}

# Main monitoring loop
monitor_loop() {
    while true; do
        # Check processes
        check_process ".implementation.pid" "Flask application"
        check_process ".websocket.pid" "WebSocket server"
        check_process ".monitor.pid" "Monitoring service"
        
        # Check system resources
        check_resources
        
        # Check service health
        check_service_health "http://localhost:5000/health" "Flask application"
        check_websocket "ws://localhost:8765"
        check_influxdb
        
        # Check logs
        check_logs
        
        # Wait for next check
        sleep "$CHECK_INTERVAL"
    done
}

# Main script
main() {
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --status)
                show_status
                exit 0
                ;;
            --interval)
                CHECK_INTERVAL=$2
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Start monitoring
    log_message "Starting monitoring service..."
    monitor_loop
}

# Run main function with all arguments
main "$@"
