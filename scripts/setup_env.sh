ng#!/bin/bash

# Enable strict error handling
set -euo pipefail
IFS=$'\n\t'

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# Source utility functions
if [ ! -f "${PROJECT_ROOT}/scripts/utils/progress_bar.sh" ]; then
    echo "Error: progress_bar.sh not found" >&2
    exit 1
fi
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    echo "❌ Error on line ${line_number}: Command exited with status ${exit_code}"
    exit ${exit_code}
}
trap 'handle_error ${LINENO}' ERR

# Save original progress values
_ORIG_CURRENT_STEP=${CURRENT_STEP:-0}
_ORIG_TOTAL_STEPS=${TOTAL_STEPS:-0}

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=8
init_progress $TOTAL_STEPS

# Environment detection
detect_environment() {
    if [ -n "${CI:-}" ]; then
        echo "ci"
    elif [ -n "${KUBERNETES_SERVICE_HOST:-}" ]; then
        echo "prod"
    elif [ -n "${STAGING:-}" ]; then
        echo "staging"
    else
        echo "dev"
    fi
}

# Load environment-specific configuration
load_environment_config() {
    local env=$1
    local config_file="${PROJECT_ROOT}/config/env/${env}.json"
    
    if [ ! -f "$config_file" ]; then
        echo "⚠️  Environment config not found: ${config_file}, using defaults"
        return 1
    fi
    
    # Validate config using Python script
    if ! python3 -c "
from dashboard.config.schema import ConfigManager
cm = ConfigManager('${config_file}')
result = cm.validate_config()
if not result.is_valid:
    for error in result.errors:
        print(f'Error: {error}')
    exit(1)
"; then
        echo "❌ Configuration validation failed"
        exit 1
    fi
    
    # Export environment variables from config
    while IFS="=" read -r key value; do
        if [ -n "$key" ]; then
            export "$key"="$value"
        fi
    done < <(python3 -c "
import json
with open('${config_file}') as f:
    config = json.load(f)
for k, v in config.items():
    if isinstance(v, (str, int, float, bool)):
        print(f'{k}={v}')
")
}

echo "🚀 Setting up environment..."

# Create virtual environment if it doesn't exist
run_with_spinner "Creating virtual environment" "
    if [ ! -d .venv ]; then
        python3 -m venv .venv
    fi
"

# Activate virtual environment
run_with_spinner "Activating virtual environment" "source .venv/bin/activate"

# Install/upgrade pip
run_with_spinner "Upgrading pip" "pip install --upgrade pip"

# Install dependencies
run_with_spinner "Installing dependencies" "pip install -r requirements.txt"

# Detect and load environment configuration
ENV=$(detect_environment)
run_with_spinner "Loading ${ENV} configuration" "load_environment_config ${ENV}"

# Create environment directories
run_with_spinner "Creating environment directories" "
    mkdir -p ${PROJECT_ROOT}/config/env
    mkdir -p ${PROJECT_ROOT}/logs/${ENV}
    mkdir -p ${PROJECT_ROOT}/metrics/${ENV}
"

# Set up environment-specific configuration
run_with_spinner "Setting up environment configuration" "
    # Create default environment config if it doesn't exist
    if [ ! -f \"${PROJECT_ROOT}/config/env/${ENV}.json\" ]; then
        cat > \"${PROJECT_ROOT}/config/env/${ENV}.json\" << EOF
{
    \"environment\": \"${ENV}\",
    \"database\": {
        \"host\": \"localhost\",
        \"port\": 5432,
        \"name\": \"dashboard_${ENV}\"
    },
    \"influxdb\": {
        \"url\": \"http://localhost:8086\",
        \"token\": \"your-token-here\",
        \"org\": \"your-org\",
        \"bucket\": \"dashboard_${ENV}\"
    },
    \"websocket\": {
        \"host\": \"localhost\",
        \"port\": 8765,
        \"ssl\": false
    },
    \"metrics\": {
        \"collection_interval\": 60,
        \"retention_days\": 30,
        \"enabled_metrics\": [\"cpu\", \"memory\", \"disk\"]
    },
    \"logging\": {
        \"level\": \"INFO\",
        \"file\": \"logs/${ENV}/dashboard.log\",
        \"max_size\": 10485760,
        \"backup_count\": 5
    },
    \"auth\": {
        \"secret_key\": \"$(openssl rand -hex 32)\",
        \"token_expiry\": 3600,
        \"algorithm\": \"HS256\",
        \"allowed_origins\": [\"http://localhost:3000\"]
    },
    \"event_loop\": {
        \"max_workers\": 4,
        \"timeout\": 30,
        \"debug\": false
    }
}
EOF
    fi

    # Set up environment variables
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
    
    # Add environment-specific overrides
    echo \"ENV=${ENV}\" >> .env
    echo \"CONFIG_PATH=config/env/${ENV}.json\" >> .env
"

echo "✨ Environment setup completed successfully!"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS
