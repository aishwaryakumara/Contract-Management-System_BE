"""User repository for database operations"""

from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.extensions import db


class UserRepository(BaseRepository[User]):
    """Repository for user-related database operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email address
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        return self.model.query.filter_by(email=email).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find user by username
        
        Args:
            username: Username
            
        Returns:
            User or None
        """
        return self.model.query.filter_by(username=username).first()
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.exists(email=email)
    
    def commit(self):
        """Commit current transaction"""
        db.session.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        db.session.rollback()
