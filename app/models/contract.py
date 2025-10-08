from app.extensions import db
from app.models.base import TimestampMixin
import uuid

class Contract(db.Model, TimestampMixin):
    """Contract model with versioning support"""
    __tablename__ = 'contracts'
    
    # Primary key is contract_instance_id (with version)
    contract_instance_id = db.Column(db.String(100), primary_key=True)  # e.g., CTR_550e8400-e29b-41d4-a716-446655440000_V1
    id = db.Column(db.String(50), nullable=False, index=True)  # UUID - Groups versions together
    contract_name = db.Column(db.String(255), nullable=False)
    client_name = db.Column(db.String(255), nullable=False, index=True)
    
    # Foreign Keys
    contract_type_id = db.Column(db.Integer, db.ForeignKey('contract_types.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('contract_status.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Contract details
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    renewal_date = db.Column(db.Date)
    value = db.Column(db.Numeric(15, 2))  # Contract value
    
    # Version tracking
    version = db.Column(db.Integer, default=1, nullable=False)
    
    # Relationships
    documents = db.relationship('Document', backref='contract', lazy='dynamic', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_contract_id():
        """Generate a unique contract ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_instance_id(contract_id, version):
        """Generate contract instance ID with version"""
        return f"CTR_{contract_id}_V{version}"
    
    def get_next_version(self):
        """Get the next version number for this contract"""
        max_version = db.session.query(db.func.max(Contract.version)).filter(
            Contract.id == self.id
        ).scalar()
        return (max_version or 0) + 1
    
    def __repr__(self):
        return f'<Contract {self.contract_instance_id} - {self.contract_name}>'