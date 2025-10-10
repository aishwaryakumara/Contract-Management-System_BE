"""Contract Type repository for database operations"""

from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.contract_type import ContractType
from app.extensions import db


class ContractTypeRepository(BaseRepository[ContractType]):
    """Repository for contract type-related database operations"""
    
    def __init__(self):
        super().__init__(ContractType)
    
    def find_by_name(self, name: str) -> Optional[ContractType]:
        """
        Find contract type by name
        
        Args:
            name: Type name (e.g., 'service', 'nda')
            
        Returns:
            ContractType or None
        """
        return self.model.query.filter_by(name=name).first()
    
    def get_id_by_name(self, name: str) -> Optional[int]:
        """
        Get contract type ID by name
        
        Args:
            name: Type name (e.g., 'service')
            
        Returns:
            Type ID or None
        """
        contract_type = self.find_by_name(name)
        return contract_type.id if contract_type else None
    
    def get_all_types(self):
        """
        Get all contract types
        
        Returns:
            List of all ContractType records
        """
        return self.find_all()
    
    def commit(self):
        """Commit current transaction"""
        db.session.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        db.session.rollback()
