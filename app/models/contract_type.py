from app.extensions import db
from app.models.base import TimestampMixin

class ContractType(db.Model, TimestampMixin):
    """Contract type/category model"""
    __tablename__ = 'contract_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    contracts = db.relationship('Contract', backref='contract_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<ContractType {self.name}>'
