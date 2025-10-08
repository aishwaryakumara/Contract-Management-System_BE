from app.extensions import db
from app.models.base import TimestampMixin

class Document(db.Model, TimestampMixin):
    """Document model for contract files and supporting documents"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_instance_id = db.Column(db.String(100), db.ForeignKey('contracts.contract_instance_id'), nullable=False, index=True)
    document_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger)  # File size in bytes
    version = db.Column(db.Integer, default=1, nullable=False)
    
    # Foreign Keys
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Metadata
    uploaded_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Document {self.document_name} - Contract: {self.contract_instance_id}>'
