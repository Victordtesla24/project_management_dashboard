#!/bin/bash

# Import utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/utils/common.sh"
source "$SCRIPT_DIR/../scripts/utils/logger.sh"

# Default values
PORT=${PORT:-5000}
CONFIG_PATH=${CONFIG_PATH:-"config.json"}
LOG_LEVEL=${LOG_LEVEL:-"INFO"}
METRICS_INTERVAL=${METRICS_INTERVAL:-5}
WS_PORT=${WS_PORT:-8765}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python version
    check_python_version "3.9" || exit 1
    
    # Check virtual environment
    check_venv || exit 1
    
    # Check required commands
    check_requirements "python3" "pip" "curl" "nc" || exit 1
    
    # Check ports
    check_port "$PORT" || exit 1
    check_port "$WS_PORT" || exit 1
    
    # Check disk space
    check_disk_space 1 || log_warning "Low disk space"
    
    # Check memory
    check_memory 90 || log_warning "High memory usage"
}

# Function to setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Load environment variables
    load_env
    
    # Create necessary directories
    ensure_directory "logs"
    ensure_directory "instance"
    
    # Validate configuration
    if [ ! -f "$CONFIG_PATH" ]; then
        log_error "Configuration file not found at $CONFIG_PATH"
        exit 1
    fi
    
    validate_json "$CONFIG_PATH" || exit 1
}

# Function to start services
start_services() {
    log_info "Starting services..."
    
    # Start InfluxDB if not running
    if ! curl -s http://localhost:8086/health > /dev/null; then
        log_info "Starting InfluxDB..."
        influxd &
        sleep 5  # Wait for InfluxDB to start
    fi
    
    # Start WebSocket server
    log_info "Starting WebSocket server..."
    python3 -c "
import asyncio
from dashboard.websocket.server import MetricsWebSocket

async def main():
    ws = MetricsWebSocket('$CONFIG_PATH')
    server = await ws.start_server()
    collection_task = asyncio.create_task(ws.start_metric_collection())
    await asyncio.gather(server.wait_closed(), collection_task)

asyncio.run(main())
" &
    echo $! > .websocket.pid
    log_success "WebSocket server started (PID: $(cat .websocket.pid))"
    
    # Start monitoring service
    log_info "Starting monitoring service..."
    python3 -c "
import time
from dashboard.metrics import collect_system_metrics
while True:
    metrics = collect_system_metrics()
    time.sleep($METRICS_INTERVAL)
" &
    echo $! > .monitor.pid
    log_success "Monitoring service started (PID: $(cat .monitor.pid))"
    
    # Start Flask application
    log_info "Starting Flask application..."
    export FLASK_APP=dashboard.app
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    
    flask run --host=0.0.0.0 --port=$PORT &
    echo $! > .implementation.pid
    log_success "Flask application started (PID: $(cat .implementation.pid))"
}

# Function to show status
show_status() {
    log_info "Dashboard is running!"
    log_info "- Web interface: http://localhost:$PORT"
    log_info "- WebSocket server: ws://localhost:$WS_PORT"
    log_info "- Metrics interval: ${METRICS_INTERVAL}s"
    log_info "- Log level: $LOG_LEVEL"
    echo
    log_info "Process IDs:"
    log_info "- Flask: $(cat .implementation.pid)"
    log_info "- WebSocket: $(cat .websocket.pid)"
    log_info "- Monitor: $(cat .monitor.pid)"
    echo
    log_info "To stop the dashboard, run: ./stop.sh"
}

# Cleanup function
cleanup() {
    log_info "Stopping services..."
    kill $(cat .implementation.pid) 2>/dev/null || true
    kill $(cat .websocket.pid) 2>/dev/null || true
    kill $(cat .monitor.pid) 2>/dev/null || true
    rm -f .implementation.pid .websocket.pid .monitor.pid
    deactivate
    log_success "All services stopped"
    exit 0
}

# Main function
main() {
    # Set up trap for cleanup
    trap cleanup INT TERM
    
    # Run setup steps
    check_prerequisites
    setup_environment
    start_services
    show_status
    
    # Wait for any process to exit
    wait -n
    
    # Cleanup if any process exits
    cleanup
}

# Run main function
main "$@"
