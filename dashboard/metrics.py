from typing import List, Dict, Any
from datetime import datetime
import psutil
from prometheus_client import Gauge, CollectorRegistry

# Initialize Prometheus registry
REGISTRY = CollectorRegistry()

# Define Prometheus metrics
CPU_GAUGE = Gauge('cpu_usage_percent', 'CPU usage percentage', registry=REGISTRY)
MEMORY_GAUGE = Gauge('memory_usage_percent', 'Memory usage percentage', registry=REGISTRY)
DISK_GAUGE = Gauge('disk_usage_percent', 'Disk usage percentage', registry=REGISTRY)

def _get_cpu_frequency() -> float:
    """Get CPU frequency with error handling."""
    try:
        freq = psutil.cpu_freq()
        return freq.current if freq else 0
    except (FileNotFoundError, AttributeError):
        return 0

def collect_system_metrics() -> Dict[str, Any]:
    """Collect system metrics and update Prometheus gauges."""
    metrics = {
        'cpu': {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'frequency': _get_cpu_frequency()
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'used': psutil.virtual_memory().used,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'percent': psutil.disk_usage('/').percent
        }
    }
    
    # Update Prometheus metrics
    CPU_GAUGE.set(metrics['cpu']['percent'])
    MEMORY_GAUGE.set(metrics['memory']['percent'])
    DISK_GAUGE.set(metrics['disk']['percent'])
    
    return metrics

def process_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Process and format metrics data."""
    return {
        'metrics': metrics,
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': psutil.boot_time()
    }

if __name__ == '__main__':
    import time
    print("Starting metrics collector...")
    try:
        while True:
            metrics = collect_system_metrics()
            processed = process_metrics(metrics)
            time.sleep(1)  # Collect metrics every second
    except KeyboardInterrupt:
        print("\nMetrics collector stopped.")
