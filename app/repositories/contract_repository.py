"""Contract repository for database operations"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.contract import Contract
from app.extensions import db


class ContractRepository(BaseRepository[Contract]):
    """Repository for contract-related database operations"""
    
    def __init__(self):
        super().__init__(Contract)
    
    def find_by_instance_id(self, instance_id: str) -> Optional[Contract]:
        """
        Find contract by instance ID (e.g., CTR_xxx_V1)
        
        Args:
            instance_id: Contract instance ID with version
            
        Returns:
            Contract or None
        """
        return self.model.query.filter_by(contract_instance_id=instance_id).first()
    
    def find_all_with_details(self) -> List[Contract]:
        """
        Get all contracts with related data (type, status, creator)
        
        Returns:
            List of contracts with relationships loaded
        """
        return self.model.query.all()
    
    def find_by_contract_id(self, contract_id: str) -> List[Contract]:
        """
        Find all versions of a contract by base ID
        
        Args:
            contract_id: Base contract ID (groups versions)
            
        Returns:
            List of contract versions
        """
        return self.model.query.filter_by(id=contract_id).order_by(Contract.version).all()
    
    def get_latest_version(self, contract_id: str) -> Optional[Contract]:
        """
        Get the latest version of a contract
        
        Args:
            contract_id: Base contract ID
            
        Returns:
            Latest version or None
        """
        return self.model.query.filter_by(id=contract_id).order_by(Contract.version.desc()).first()
    
    def get_max_version(self, contract_id: str) -> int:
        """
        Get the maximum version number for a contract
        
        Args:
            contract_id: Base contract ID
            
        Returns:
            Max version number (0 if none exist)
        """
        max_version = db.session.query(func.max(Contract.version)).filter(
            Contract.id == contract_id
        ).scalar()
        return max_version or 0
    
    def create_contract(self, contract_data: dict) -> Contract:
        """
        Create new contract
        
        Args:
            contract_data: Contract field values
            
        Returns:
            Created contract
        """
        contract = Contract(**contract_data)
        db.session.add(contract)
        db.session.flush()  # Get ID without committing
        return contract
    
    def update_contract(self, instance_id: str, updates: dict) -> Optional[Contract]:
        """
        Update contract fields
        
        Args:
            instance_id: Contract instance ID
            updates: Fields to update
            
        Returns:
            Updated contract or None
        """
        contract = self.find_by_instance_id(instance_id)
        if not contract:
            return None
        
        for key, value in updates.items():
            if hasattr(contract, key):
                setattr(contract, key, value)
        
        contract.updated_at = datetime.utcnow()
        return contract
    
    def commit(self):
        """Commit current transaction"""
        db.session.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        db.session.rollback()
