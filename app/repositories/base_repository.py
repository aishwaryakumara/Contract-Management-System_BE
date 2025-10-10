"""Base repository with common CRUD operations"""

from app.extensions import db
from typing import TypeVar, Generic, List, Optional, Dict, Any

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing common database operations.
    Inherit from this to get standard CRUD functionality.
    """
    
    def __init__(self, model: type[T]):
        """
        Initialize repository with model class
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new record
        
        Args:
            data: Dictionary of field values
            
        Returns:
            Created model instance
        """
        instance = self.model(**data)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def find_by_id(self, id: Any) -> Optional[T]:
        """
        Find record by primary key
        
        Args:
            id: Primary key value
            
        Returns:
            Model instance or None
        """
        return self.model.query.get(id)
    
    def find_one(self, **filters) -> Optional[T]:
        """
        Find single record by filters
        
        Args:
            **filters: Field filters (e.g., name='test')
            
        Returns:
            Model instance or None
        """
        return self.model.query.filter_by(**filters).first()
    
    def find_all(self, **filters) -> List[T]:
        """
        Find all records matching filters
        
        Args:
            **filters: Field filters (e.g., status='active')
            
        Returns:
            List of model instances
        """
        query = self.model.query
        if filters:
            query = query.filter_by(**filters)
        return query.all()
    
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """
        Update record by ID
        
        Args:
            id: Primary key value
            data: Dictionary of fields to update
            
        Returns:
            Updated model instance or None
        """
        instance = self.find_by_id(id)
        if not instance:
            return None
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        db.session.commit()
        return instance
    
    def delete(self, id: Any) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Primary key value
            
        Returns:
            True if deleted, False if not found
        """
        instance = self.find_by_id(id)
        if not instance:
            return False
        
        db.session.delete(instance)
        db.session.commit()
        return True
    
    def count(self, **filters) -> int:
        """
        Count records matching filters
        
        Args:
            **filters: Field filters
            
        Returns:
            Number of matching records
        """
        query = self.model.query
        if filters:
            query = query.filter_by(**filters)
        return query.count()
    
    def exists(self, **filters) -> bool:
        """
        Check if record exists
        
        Args:
            **filters: Field filters
            
        Returns:
            True if exists, False otherwise
        """
        return self.find_one(**filters) is not None
