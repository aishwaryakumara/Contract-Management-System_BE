from app.extensions import db
from datetime import datetime

class AuditLog(db.Model):
    """Audit log for tracking all system changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # e.g., 'create', 'update', 'delete', 'view'
    entity_type = db.Column(db.String(50), nullable=False)  # e.g., 'contract', 'document', 'user'
    entity_id = db.Column(db.String(50), nullable=False, index=True)  # ID of the affected entity
    changes = db.Column(db.JSON)  # JSON object storing what changed
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type} {self.entity_id}>'
