from app.extensions import db
from app.models.base import TimestampMixin

class DocumentType(db.Model, TimestampMixin):
    """Document type lookup table"""
    __tablename__ = 'document_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'main_contract', 'invoice', 'letter', 'supporting_doc'
    description = db.Column(db.Text)
    
    # Relationships
    documents = db.relationship('Document', backref='document_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<DocumentType {self.name}>'
