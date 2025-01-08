// Authentication functions
function logout() {
    sessionStorage.removeItem('auth_token');
    window.location.href = '/login';
}

// WebSocket connection with authentication
function connectWebSocket() {
    const token = getAuthToken();
    if (!token) return;

    const ws = new WebSocket();
    
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
            `<div class=metric>
                <div class=metric-title>CPU Usage</div>
                <div class=metric-value>${data.cpu}%</div>
             </div>
             <div class=metric>
                <div class=metric-title>Memory Usage</div>
                <div class=metric-value>${data.memory}%</div>
             </div>
             <div class=metric>
                <div class=metric-title>Disk Usage</div>
                <div class=metric-value>${data.disk}%</div>
             </div>`;
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
