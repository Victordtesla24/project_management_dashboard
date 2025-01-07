class MetricsWebSocket {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => console.log('Connected to metrics server');
        this.ws.onmessage = (event) => this.updateDashboard(JSON.parse(event.data));
        this.ws.onclose = () => this.reconnect();
        this.ws.onerror = (error) => console.error('WebSocket error:', error);
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
        }
    }

    updateDashboard(metrics) {
        Object.entries(metrics).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = typeof value === 'number'
                    ? value.toFixed(1) + '%'
                    : value;
            }
        });
    }
}

const ws = new MetricsWebSocket('ws://localhost:8765');
ws.connect();
