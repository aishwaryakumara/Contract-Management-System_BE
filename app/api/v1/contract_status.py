"""Contract Status API endpoints"""

from flask import Blueprint, jsonify
from app.repositories.contract_status_repository import ContractStatusRepository

contract_status_bp = Blueprint('contract_status', __name__)

# Initialize repository
contract_status_repo = ContractStatusRepository()


@contract_status_bp.route('', methods=['GET'])
def get_contract_statuses():
    """
    Get all contract statuses
    
    Response:
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "name": "draft",
                    "description": "Contract in draft state"
                }
            ]
        }
    """
    try:
        statuses = contract_status_repo.get_all_statuses()
        
        statuses_data = []
        for status in statuses:
            statuses_data.append({
                'id': status.id,
                'name': status.name,
                'description': status.description
            })
        
        return jsonify({
            'success': True,
            'data': statuses_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
