"""Main application module."""

import os
import asyncio
import secrets
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Tuple
from flask import Flask, render_template, request, redirect, url_for, session, g
from dashboard.auth.middleware import init_auth, authenticate, login_required
from dashboard.metrics import collect_system_metrics, process_metrics
from dashboard.websocket.server import MetricsWebSocket
from dashboard.config import init_config

app = Flask(__name__)
metrics_ws = None

def initialize_session_state(session_state: Dict[str, Any]) -> None:
    """Initialize session state with default values."""
    if "metrics_history" not in session_state:
        session_state["metrics_history"] = []
    if "last_update" not in session_state:
        session_state["last_update"] = datetime.now()

def setup_sidebar() -> tuple[int, list[str]]:
    """Setup sidebar controls and return update interval and selected metrics."""
    st.sidebar.title("Dashboard Controls")
    
    # Update interval control
    update_interval = st.sidebar.slider(
        "Update Interval (seconds)",
        min_value=1,
        max_value=60,
        value=5
    )
    
    # Metrics selection
    available_metrics = ["CPU Usage", "Memory Usage", "Disk Usage"]
    metrics_to_show = st.sidebar.multiselect(
        "Metrics to Display",
        options=available_metrics,
        default=available_metrics[:2]  # Default to first two metrics
    )
    
    return update_interval, metrics_to_show

def setup_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Project Management Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def update_metrics(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Update metrics in session state."""
    raw_metrics = collect_system_metrics()
    processed_metrics = process_metrics(raw_metrics)
    
    # Add to history, maintaining max size of 50
    if not hasattr(session_state, 'metrics_history'):
        session_state.metrics_history = []
    
    session_state.metrics_history.append(processed_metrics)
    if len(session_state.metrics_history) > 50:
        session_state.metrics_history = session_state.metrics_history[-50:]
    
    session_state.last_update = datetime.now()
    return processed_metrics

def display_metrics(session_state: Dict[str, Any], metrics_to_show: List[str]) -> None:
    """Display metrics visualization.
    
    Args:
        session_state: The session state containing metrics data
        metrics_to_show: List of metric names to display
    """
    if not hasattr(session_state, 'metrics_history') or not session_state.metrics_history:
        st.warning("No metrics data available")
        return
    
    # Get latest metrics
    latest_metrics = session_state.metrics_history[-1]
    
    # Create metrics display
    col1, col2 = st.columns(2)
    
    with col1:
        if "CPU Usage" in metrics_to_show and "metrics" in latest_metrics:
            st.metric(
                "CPU Usage",
                f"{latest_metrics['metrics']['cpu']['percent']:.1f}%",
                delta=None
            )
        
        if "Memory Usage" in metrics_to_show and "metrics" in latest_metrics:
            st.metric(
                "Memory Usage",
                f"{latest_metrics['metrics']['memory']['percent']:.1f}%",
                delta=None
            )
    
    with col2:
        if "Disk Usage" in metrics_to_show and "metrics" in latest_metrics:
            st.metric(
                "Disk Usage",
                f"{latest_metrics['metrics']['disk']['percent']:.1f}%",
                delta=None
            )
    
    # Create time series plot
    if session_state.metrics_history:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces
        timestamps = [m["timestamp"] for m in session_state.metrics_history]
        
        if "CPU Usage" in metrics_to_show:
            cpu_values = [m["metrics"]["cpu"]["percent"] for m in session_state.metrics_history]
            fig.add_trace(
                go.Scatter(x=timestamps, y=cpu_values, name="CPU Usage"),
                secondary_y=False,
            )
        
        if "Memory Usage" in metrics_to_show:
            memory_values = [m["metrics"]["memory"]["percent"] for m in session_state.metrics_history]
            fig.add_trace(
                go.Scatter(x=timestamps, y=memory_values, name="Memory Usage"),
                secondary_y=True,
            )
        
        # Update layout
        fig.update_layout(
            title="System Metrics Over Time",
            xaxis_title="Time",
            yaxis_title="CPU Usage (%)",
            yaxis2_title="Memory Usage (%)"
        )
        
        st.plotly_chart(fig)

def create_app():
    """Create and configure Flask application."""
    # Load configuration
    config_path = os.getenv('CONFIG_PATH', 'config.json')
    init_config(config_path)
    
    # Initialize authentication
    init_auth(app)
    
    return app

@app.route('/')
@login_required
def index():
    """Render dashboard index page."""
    # Generate WebSocket authentication token
    ws_token = secrets.token_urlsafe(32)
    session['ws_token'] = ws_token
    return render_template('index.html', ws_token=ws_token)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login requests."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate(username, password):
            session['user'] = username
            return redirect(url_for('index'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle logout requests."""
    session.clear()
    return redirect(url_for('login'))

async def start_websocket():
    """Start WebSocket server."""
    global metrics_ws
    metrics_ws = MetricsWebSocket()
    await metrics_ws.start_server()

async def shutdown_websocket():
    """Shutdown WebSocket server."""
    global metrics_ws
    if metrics_ws:
        await metrics_ws.stop_server()

def main():
    """Run the application."""
    app = create_app()
    
    # Start WebSocket server
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_websocket())
        
        # Run Flask app
        app.run(
            host=os.getenv('FLASK_HOST', '127.0.0.1'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        )
    finally:
        loop.run_until_complete(shutdown_websocket())
        loop.close()

if __name__ == '__main__':
    main()
