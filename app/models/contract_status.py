from app.extensions import db
from app.models.base import TimestampMixin

class ContractStatus(db.Model, TimestampMixin):
    """Contract status lookup table"""
    __tablename__ = 'contract_status'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'draft', 'active', 'expired', 'renewed'
    description = db.Column(db.Text)
    
    # Relationships
    contracts = db.relationship('Contract', backref='contract_status', lazy='dynamic')
    
    def __repr__(self):
        return f'<ContractStatus {self.name}>'
