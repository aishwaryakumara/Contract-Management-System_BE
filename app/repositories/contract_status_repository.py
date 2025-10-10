"""Contract Status repository for database operations"""

from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.contract_status import ContractStatus
from app.extensions import db


class ContractStatusRepository(BaseRepository[ContractStatus]):
    """Repository for contract status-related database operations"""
    
    def __init__(self):
        super().__init__(ContractStatus)
    
    def find_by_name(self, name: str) -> Optional[ContractStatus]:
        """
        Find contract status by name
        
        Args:
            name: Status name (e.g., 'draft', 'active')
            
        Returns:
            ContractStatus or None
        """
        return self.model.query.filter_by(name=name).first()
    
    def get_id_by_name(self, name: str) -> Optional[int]:
        """
        Get contract status ID by name
        
        Args:
            name: Status name (e.g., 'draft')
            
        Returns:
            Status ID or None
        """
        status = self.find_by_name(name)
        return status.id if status else None
    
    def get_all_statuses(self):
        """
        Get all contract statuses
        
        Returns:
            List of all ContractStatus records
        """
        return self.find_all()
    
    def commit(self):
        """Commit current transaction"""
        db.session.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        db.session.rollback()
