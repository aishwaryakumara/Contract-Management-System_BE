"""Authentication API endpoints"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

# Initialize service
auth_service = AuthService()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Request:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "token": "jwt_token",
                "user": { ... }
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Call service
        result = auth_service.login(email, password)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current logged-in user info
    
    Response:
        {
            "success": true,
            "data": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user"
            }
        }
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # Call service
        user_data = auth_service.get_current_user(current_user_id)
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
