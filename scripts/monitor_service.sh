#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Create required directories
echo "Setting up monitoring directory structure..."
directories=(
    "metrics/tracking"
    "metrics/logs"
    "metrics/data"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"
    touch "$full_path/.gitkeep" 2>/dev/null || true
done

# Get current user for service configuration
CURRENT_USER=$(whoami)
INSTALL_DIR=$(realpath "${PROJECT_ROOT}")

# Create dashboard service file
echo "Creating dashboard service configuration..."
if [ ! -f "${PROJECT_ROOT}/metrics/dashboard.service" ]; then
    cat > "${PROJECT_ROOT}/metrics/dashboard.service" << EOF || handle_error "Failed to create dashboard.service"
[Unit]
Description=Project Management Dashboard Service
After=network.target

[Service]
Type=simple
User=dashboard
WorkingDirectory=/opt/dashboard
ExecStart=/usr/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
fi

# Create monitor service file
echo "Creating monitor service configuration..."
if [ ! -f "${PROJECT_ROOT}/metrics/monitor.service" ]; then
    cat > "${PROJECT_ROOT}/metrics/monitor.service" << EOF || handle_error "Failed to create monitor.service"
[Unit]
Description=Project Management Monitor Service
After=network.target

[Service]
Type=simple
User=dashboard
WorkingDirectory=/opt/dashboard
ExecStart=/usr/bin/python3 monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
fi

# Create default metrics configuration if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/metrics/config.json" ]; then
    echo "Creating default metrics configuration..."
    cat > "${PROJECT_ROOT}/metrics/config.json" << 'EOF' || handle_error "Failed to create metrics config"
{
    "collection_interval": 60,
    "retention_days": 30,
    "metrics": {
        "system": ["cpu", "memory", "disk", "network"],
        "application": ["requests", "errors", "response_time"]
    },
    "alerts": {
        "cpu_threshold": 80,
        "memory_threshold": 90,
        "disk_threshold": 85
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
EOF
fi

# Validate configurations
echo "Validating service configurations..."
for service in "dashboard.service" "monitor.service" "config.json"; do
    if [ ! -s "${PROJECT_ROOT}/metrics/${service}" ]; then
        handle_error "${service} is empty"
    fi
done

# Create log files if they don't exist
for service in "dashboard" "monitor"; do
    touch "${PROJECT_ROOT}/metrics/logs/${service}.log" 2>/dev/null || true
    touch "${PROJECT_ROOT}/metrics/logs/${service}.error.log" 2>/dev/null || true
done

echo "✓ Monitoring service setup completed"
exit 0
