"""Document repository for database operations"""

from typing import Optional, List
from datetime import datetime
from app.repositories.base_repository import BaseRepository
from app.models.document import Document
from app.extensions import db


class DocumentRepository(BaseRepository[Document]):
    """Repository for document-related database operations"""
    
    def __init__(self):
        super().__init__(Document)
    
    def find_by_contract(self, contract_instance_id: str) -> List[Document]:
        """
        Get all documents for a contract
        
        Args:
            contract_instance_id: Contract instance ID
            
        Returns:
            List of documents
        """
        return self.model.query.filter_by(contract_instance_id=contract_instance_id).all()
    
    def create_document(self, document_data: dict) -> Document:
        """
        Create new document
        
        Args:
            document_data: Document field values
            
        Returns:
            Created document
        """
        document = Document(**document_data)
        db.session.add(document)
        db.session.flush()
        return document
    
    def delete_by_id(self, document_id: int) -> Optional[Document]:
        """
        Delete document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Deleted document or None
        """
        document = self.find_by_id(document_id)
        if document:
            db.session.delete(document)
        return document
    
    def commit(self):
        """Commit current transaction"""
        db.session.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        db.session.rollback()
