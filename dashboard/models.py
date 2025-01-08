from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class JSONSerializable:
    """Mixin for JSON serialization."""
    def to_dict(self):
        """Convert model to dictionary."""
        result = {}
        for key in self.__mapper__.attrs.keys():
            value = getattr(self, key)
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

class User(db.Model, JSONSerializable):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check password hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username
        }

class Metric(db.Model, JSONSerializable):
    """Metric model."""
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model, JSONSerializable):
    """Alert model."""
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def model_to_dict(obj):
    """Convert model to dictionary."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [model_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: model_to_dict(value) for key, value in obj.items()}
    return obj

def init_db(app):
    """Initialize database."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
