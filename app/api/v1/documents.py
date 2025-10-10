"""Document management API endpoints"""

import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.document import Document

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/<int:document_id>/download', methods=['GET', 'OPTIONS'])
def download_document(document_id):
    """
    Download a document file
    
    Args:
        document_id: Document ID
        
    Response:
        File download or error
        
    Example:
        GET /api/documents/123/download
        Returns the file with proper headers
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    # For GET, require JWT
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401
    
    try:
        # Get document from database
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Handle both absolute and relative paths
        file_path = document.file_path
        if not os.path.isabs(file_path):
            # Convert relative path to absolute
            file_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'File not found on server: {file_path}'
            }), 404
        
        # Send file with proper headers
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document.document_name,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """
    Delete a supporting document
    
    Response:
        {
            "success": true,
            "message": "Document deleted successfully"
        }
    """
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete database record
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
