#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Save original progress values
_ORIG_CURRENT_STEP=$CURRENT_STEP
_ORIG_TOTAL_STEPS=$TOTAL_STEPS

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=5
init_progress $TOTAL_STEPS

echo "🚀 Setting up dashboard..."

# Create dashboard directories
run_with_spinner "Creating dashboard directories" "
    mkdir -p \"${PROJECT_ROOT}/dashboard/static/css\" &&
    mkdir -p \"${PROJECT_ROOT}/dashboard/static/js\" &&
    mkdir -p \"${PROJECT_ROOT}/dashboard/templates\" &&
    mkdir -p \"${PROJECT_ROOT}/dashboard/components\" &&
    mkdir -p \"${PROJECT_ROOT}/dashboard/pages\"
"

# Create base templates
run_with_spinner "Creating base templates" "
    cat > \"${PROJECT_ROOT}/dashboard/templates/base.html\" << 'EOF'
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Project Management Dashboard</title>
    <link rel=\"stylesheet\" href=\"/static/css/style.css\">
    <script>
        // Get auth token from session storage or redirect to login
        function getAuthToken() {
            const token = sessionStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/login';
                return null;
            }
            return token;
        }
    </script>
</head>
<body>
    <div id=\"app\">
        <nav class=\"navbar\">
            <div class=\"nav-brand\">Dashboard</div>
            <div class=\"nav-menu\">
                <a href=\"/\" class=\"nav-item\">Home</a>
                <a href=\"/metrics\" class=\"nav-item\">Metrics</a>
                <button onclick=\"logout()\" class=\"nav-item\">Logout</button>
            </div>
        </nav>
        {% block content %}{% endblock %}
    </div>
    <script src=\"/static/js/main.js\"></script>
</body>
</html>
EOF

    cat > \"${PROJECT_ROOT}/dashboard/templates/index.html\" << 'EOF'
{% extends \"base.html\" %}
{% block content %}
<div class=\"dashboard\">
    <div class=\"metrics\">
        <div id=\"system-metrics\"></div>
        <div id=\"project-metrics\"></div>
    </div>
    <div class=\"charts\">
        <div id=\"cpu-chart\"></div>
        <div id=\"memory-chart\"></div>
    </div>
</div>
{% endblock %}
EOF
"

# Create static files
run_with_spinner "Creating static files" "
    cat > \"${PROJECT_ROOT}/dashboard/static/css/style.css\" << 'EOF'
.dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.metrics, .charts {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

[data-theme=\"dark\"] {
    background: #1a1a1a;
    color: #ffffff;
}
EOF

    cat > \"${PROJECT_ROOT}/dashboard/static/js/main.js\" << 'EOF'
// Authentication functions
function logout() {
    sessionStorage.removeItem('auth_token');
    window.location.href = '/login';
}

// WebSocket connection with authentication
function connectWebSocket() {
    const token = getAuthToken();
    if (!token) return;

    const ws = new WebSocket(`ws://localhost:8765?token=${token}`);
    
    ws.onopen = () => {
        console.log('Connected to WebSocket');
        // Subscribe to metrics
        ws.send(JSON.stringify({
            type: 'subscribe',
            metrics: ['cpu', 'memory', 'disk']
        }));
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.error) {
                console.error('WebSocket error:', data.error);
                return;
            }
            updateMetrics(data);
            updateCharts(data);
        } catch (error) {
            console.error('Error processing message:', error);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
    };

    // Ping to keep connection alive
    setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
        }
    }, 30000);

    return ws;
}

function updateMetrics(data) {
    try {
        document.getElementById('system-metrics').innerHTML =
            \`<div class="metric">
                <div class="metric-title">CPU Usage</div>
                <div class="metric-value">\${data.cpu}%</div>
             </div>
             <div class="metric">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value">\${data.memory}%</div>
             </div>
             <div class="metric">
                <div class="metric-title">Disk Usage</div>
                <div class="metric-value">\${data.disk}%</div>
             </div>\`;
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

function updateCharts(data) {
    try {
        // Update CPU chart
        updateLineChart('cpu-chart', data.cpu_history, {
            title: 'CPU Usage Over Time',
            yAxisLabel: 'Usage %'
        });

        // Update Memory chart
        updateLineChart('memory-chart', data.memory_history, {
            title: 'Memory Usage Over Time',
            yAxisLabel: 'Usage %'
        });
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

function updateLineChart(elementId, data, options) {
    // Chart implementation using a library like Chart.js
    // This is a placeholder for the actual implementation
}

// Initialize WebSocket connection when page loads
document.addEventListener('DOMContentLoaded', connectWebSocket);
EOF
"

# Install UI dependencies
run_with_spinner "Installing UI dependencies" "
    python3 -m pip install -q flask-assets webassets || true
"

# Setup UI routes
run_with_spinner "Setting up UI routes" "
    cat > \"${PROJECT_ROOT}/dashboard/routes.py\" << 'EOF'
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
import jwt
from ..auth.middleware import verify_token, create_token

bp = Blueprint('dashboard', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            return redirect(url_for('auth.login'))
        try:
            verify_token(token)
        except jwt.InvalidTokenError:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
def index():
    return render_template('index.html')

@bp.route('/metrics')
@login_required
def metrics():
    return render_template('metrics.html')

@bp.route('/api/metrics')
@login_required
def get_metrics():
    try:
        from ..core_scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        system_metrics = collector.collect_system_metrics()
        project_metrics = collector.collect_project_metrics()
        return jsonify({**system_metrics, **project_metrics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
EOF
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

exit 0
