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
</head>
<body>
    <div id=\"app\">
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
const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateMetrics(data);
    updateCharts(data);
};

function updateMetrics(data) {
    document.getElementById('system-metrics').innerHTML =
        \`<div>CPU: \${data.cpu}%</div>
         <div>Memory: \${data.memory}%</div>
         <div>Disk: \${data.disk}%</div>\`;
}

function updateCharts(data) {
    // Chart updates will be implemented here
}
EOF
"

# Install UI dependencies
run_with_spinner "Installing UI dependencies" "
    python3 -m pip install -q flask-assets webassets || true
"

# Setup UI routes
run_with_spinner "Setting up UI routes" "
    cat > \"${PROJECT_ROOT}/dashboard/routes.py\" << 'EOF'
from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/metrics')
def metrics():
    return render_template('metrics.html')
EOF
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

exit 0
