"""Authentication service for user authentication and authorization"""

from typing import Dict, Optional
from flask_jwt_extended import create_access_token
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication-related business logic"""
    
    def __init__(self):
        """Initialize auth service with dependencies"""
        self.user_repo = UserRepository()
    
    def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user and generate JWT token
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with token and user info
            
        Raises:
            ValueError: If validation fails or credentials invalid
        """
        # Validate inputs
        if not email or not password:
            raise ValueError('Email and password are required')
        
        # Find user
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise ValueError('Invalid email or password')
        
        # Verify password
        if not user.check_password(password):
            raise ValueError('Invalid email or password')
        
        # Generate JWT token
        access_token = create_access_token(identity=str(user.id))
        
        return {
            'token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }
    
    def get_current_user(self, user_id: int) -> Optional[Dict]:
        """
        Get current user information
        
        Args:
            user_id: User ID from JWT token
            
        Returns:
            User info dict or None if not found
        """
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            return None
        
        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
    
    def register(self, data: Dict) -> Dict:
        """
        Register a new user
        
        Args:
            data: User registration data
            
        Returns:
            Created user info
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'Missing required field: {field}')
        
        # Check if email already exists
        if self.user_repo.email_exists(data['email']):
            raise ValueError('Email already registered')
        
        # Create user (password hashing happens in User model)
        user = self.user_repo.create({
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'role': data.get('role', 'user'),  # Default role
            'password': data['password']  # Will be hashed by User model
        })
        
        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
