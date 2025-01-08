from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
import jwt
from auth.middleware import verify_token, create_token

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
