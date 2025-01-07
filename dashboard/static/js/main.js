const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateMetrics(data);
    updateCharts(data);
};

function updateMetrics(data) {
    document.getElementById('system-metrics').innerHTML =
        `<div>CPU: ${data.cpu}%</div>
         <div>Memory: ${data.memory}%</div>
         <div>Disk: ${data.disk}%</div>`;
}

function updateCharts(data) {
    // Chart updates will be implemented here
}
