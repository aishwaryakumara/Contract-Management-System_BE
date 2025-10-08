from app.extensions import db
from app.models.base import TimestampMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, TimestampMixin):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # For now, all users have 'user' role
    
    # Relationships
    created_contracts = db.relationship('Contract', foreign_keys='Contract.created_by', backref='creator', lazy='dynamic')
    uploaded_documents = db.relationship('Document', foreign_keys='Document.uploaded_by', backref='uploader', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the user password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password, password)
    
    @property
    def full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.email}>'
