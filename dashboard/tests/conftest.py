import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from flask import Flask, current_app, session
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from dashboard.app import create_app
from dashboard.config import init_config
from dashboard.models import Alert, Metric, User
from dashboard.models import db as _db

# Test configuration
TEST_CONFIG = {
"TESTING": True,
"DATABASE_URL": "sqlite:///:memory:",
"SECRET_KEY": "test-key",
"WTF_CSRF_ENABLED": False,
    }
class MockRequest:
def __init__(self):
self.method = "GET"
self.args = {}
self.json = {}
self.headers = {}
self.form = {}
self.environ = {}
self.blueprints = []
@pytest.fixture(scope="function")
def event_loop():
"""\1"""
policy = asyncio.get_event_loop_policy()
loop = policy.new_event_loop()
asyncio.set_event_loop(loop)
yield loop
if loop.is_running():
loop.call_soon(loop.stop)
loop.run_forever()
loop.close()
asyncio.set_event_loop(None)
@pytest.fixture(scope="session")
def config_file():
"""\1"""
path = os.path.join(os.path.dirname(__file__), "fixtures", "test_config.json")
if not os.path.exists(path):
raise FileNotFoundError(f"Test config file not found at {path}")
return path
@pytest.fixture(scope="function")
def app_config(config_file):
"""\1"""
with open(config_file) as f:
config = json.load(f)
return {
"TESTING": True,
"SECRET_KEY": "test_key",
"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
"SQLALCHEMY_TRACK_MODIFICATIONS": False,
"SESSION_TYPE": "filesystem",
"CONFIG_PATH": config_file,
"CONFIG": config,
    }
@pytest.fixture
def app(app_config):
"""\1"""
app = create_app(app_config)
app.config.update(app_config)
with app.app_context():
# Initialize configuration
init_config(app.config["CONFIG_PATH"])
# Create all tables
_db.create_all()
# Create test user
if not User.query.filter_by(username="test_user").first():
user = User(username="test_user")
user.set_password("test_password")
_db.session.add(user)
_db.session.commit()
yield app
# Clean up
_db.session.remove()
_db.drop_all()
@pytest.fixture
def app_context(app):
"""\1"""
with app.app_context() as ctx:
yield ctx
@pytest.fixture
def request_context(app):
"""\1"""
with app.test_request_context() as ctx:
ctx.push()
yield ctx
ctx.pop()
@pytest.fixture
def mock_request(request_context):
"""\1"""
request = MockRequest()
request_context.request = request
return request
@pytest.fixture
def mock_session(request_context):
"""\1"""
session.clear()
return session
@pytest.fixture
def test_client(app):
"""\1"""
with app.test_client() as client:
with app.app_context():
# Initialize routes
from dashboard import routes

yield client
@pytest.fixture
def auth_headers():
"""\1"""
return {"Authorization": "Bearer test_token"}
@pytest.fixture
def mock_websocket(event_loop):
"""\1"""
class MockWebSocket:
def __init__(self):
self.sent_messages = []
self.closed = False
self.loop = event_loop
async def send(self, message):
self.sent_messages.append(message)
async def close(self):
self.closed = True
async def receive(self):
return None
async def __aiter__(self):
return self
async def __anext__(self):
raise StopAsyncIteration
return MockWebSocket()
@pytest.fixture
def mock_influxdb():
"""\1"""
class MockInfluxDB:
def __init__(self):
self.points = []
def write_points(self, points):
self.points.extend(points)
def close(self):
return MockInfluxDB()
@pytest.fixture
def sample_metrics():
"""\1"""
return {
"cpu": {"percent": 45.5, "count": 8, "frequency": 2.5},
"memory": {"percent": 60.2, "total": 16000000000, "used": 9632000000},
"disk": {"percent": 75.8, "total": 500000000000, "used": 379000000000},
    }
@pytest.fixture
def sample_config():
"""\1"""
with open(os.path.join(os.path.dirname(__file__), "fixtures", "test_config.json")) as f:
return json.load(f)
@pytest.fixture
def client(app):
"""\1"""
return app.test_client()
@pytest.fixture
def db(app):
"""\1"""
return _db
@pytest.fixture
def test_metric(db):
"""\1"""
metric = Metric(metric_type="cpu_usage", value=45.5, timestamp=datetime.utcnow())
db.session.add(metric)
db.session.commit()
return metric
@pytest.fixture
def test_alert(db):
"""\1"""
alert = Alert(
metric_type="cpu_usage",
value=85.5,
threshold=80.0,
status="active",
timestamp=datetime.utcnow(),
    )
db.session.add(alert)
db.session.commit()
return alert
@pytest.fixture
def test_user(db):
"""\1"""
from dashboard.models import User

user = User(username="test_user")
user.set_password("test_password")
db.session.add(user)
db.session.commit()
return user
