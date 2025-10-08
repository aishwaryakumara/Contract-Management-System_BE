from datetime import datetime
from app.extensions import db

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
