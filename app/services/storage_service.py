"""Storage service for file handling operations"""

import os
from typing import Dict, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app


class StorageService:
    """Service for handling file storage operations"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    def __init__(self):
        """Initialize storage service"""
        pass
    
    def is_allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed
        
        Args:
            filename: Name of the file
            
        Returns:
            True if allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_file(self, file: FileStorage, subfolder: str = '') -> Dict[str, any]:
        """
        Save uploaded file to storage
        
        Args:
            file: Uploaded file object
            subfolder: Optional subfolder path
            
        Returns:
            Dict with file info (filename, path, size)
            
        Raises:
            ValueError: If file is invalid or extension not allowed
        """
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        if not self.is_allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Create upload directory
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if subfolder:
            upload_folder = os.path.join(upload_folder, subfolder)
        
        # Convert to absolute path
        upload_folder = os.path.abspath(upload_folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Build full file path (absolute)
        file_path = os.path.join(upload_folder, filename)
        
        # Save file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return {
            'filename': filename,
            'path': file_path,
            'size': file_size
        }
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted, False if file not found
        """
        if not file_path or not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            # Log error but don't crash
            print(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if exists, False otherwise
        """
        return os.path.exists(file_path) if file_path else False
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size or None if not found
        """
        if self.file_exists(file_path):
            return os.path.getsize(file_path)
        return None
