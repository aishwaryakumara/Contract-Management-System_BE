from app.extensions import db
from datetime import datetime


class ActivityHistory(db.Model):
    __tablename__ = 'activity_history'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_instance_id = db.Column(db.String(50), db.ForeignKey('contracts.contract_instance_id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # created, modified, document_uploaded, document_deleted, status_changed
    user = db.Column(db.String(100), nullable=False)  # username or email
    details = db.Column(db.JSON)  # {message: "...", changes: [...]}
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    contract = db.relationship('Contract', backref='activities', foreign_keys=[contract_instance_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'user': self.user,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
