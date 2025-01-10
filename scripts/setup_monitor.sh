#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Check for monitor service file
if [ ! -f "${PROJECT_ROOT}/metrics/monitor.service" ]; then
    handle_error "monitor.service not found"
fi

# Check for process metrics config
if [ ! -f "${PROJECT_ROOT}/metrics/process_metrics.json" ]; then
    handle_error "process_metrics.json not found"
fi

# Check for system metrics config
if [ ! -f "${PROJECT_ROOT}/metrics/system_metrics.json" ]; then
    handle_error "system_metrics.json not found"
fi

# Create required monitor directories
echo "Setting up monitor directory structure..."
directories=(
    "metrics/data"
    "metrics/logs"
    "metrics/tracking"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"

    # Add .gitkeep to preserve empty directories
    touch "$full_path/.gitkeep" 2>/dev/null || true
done

# Create monitor module if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/src/monitor/__init__.py" ]; then
    echo "Creating monitor module..."
    mkdir -p "${PROJECT_ROOT}/src/monitor"
    cat > "${PROJECT_ROOT}/src/monitor/__init__.py" << 'EOF' || handle_error "Failed to create monitor module"
"""Monitor module for collecting system and process metrics."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import psutil

class MetricsMonitor:
    """Monitor for collecting system and process metrics."""

    def __init__(self, config_dir: str = None):
        """Initialize monitor with configuration directory."""
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'metrics')

        self.config_dir = config_dir
        self.process_config = self._load_config('process_metrics.json')
        self.system_config = self._load_config('system_metrics.json')

        # Create data directory
        self.data_dir = os.path.join(config_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = os.path.join(self.config_dir, filename)
        with open(config_path) as f:
            return json.load(f)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        metrics = {
            'cpu': {
                'percent': psutil.cpu_percent(),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            },
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'network': psutil.net_io_counters()._asdict(),
            'load': {'load_avg': psutil.getloadavg()}
        }
        return metrics

    def _collect_process_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Collect process metrics."""
        metrics = {}
        for proc_config in self.process_config.get('processes', []):
            pattern = proc_config['pattern']
            proc_metrics = {}

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any(pattern in ' '.join(proc.cmdline()) for pattern in [pattern]):
                        proc_info = proc.as_dict(attrs=['cpu_percent', 'memory_info', 'num_threads'])
                        proc_metrics = {
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory': proc_info['memory_info']._asdict(),
                            'num_threads': proc_info['num_threads']
                        }
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            metrics[proc_config['name']] = proc_metrics

        return metrics

    def _collect_metrics(self):
        """Collect all metrics and save to file."""
        timestamp = datetime.now().isoformat()
        metrics = {
            'timestamp': timestamp,
            'system': self._collect_system_metrics(),
            'processes': self._collect_process_metrics()
        }

        # Save metrics to file
        filename = f'metrics_{timestamp}.json'
        filepath = os.path.join(self.data_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)

    def run(self):
        """Run the metrics collection loop."""
        while True:
            try:
                self._collect_metrics()
                time.sleep(self.system_config.get('collection_interval', 300))
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                time.sleep(60)  # Wait before retrying

if __name__ == '__main__':
    monitor = MetricsMonitor()
    monitor.run()
EOF
fi

# Install required Python packages
echo "Installing required packages..."
source "${PROJECT_ROOT}/.venv/bin/activate"
pip install psutil

echo "✓ Monitor setup completed"
exit 0
