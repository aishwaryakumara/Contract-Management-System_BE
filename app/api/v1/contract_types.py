"""Contract Types API endpoints"""

from flask import Blueprint, jsonify
from app.models.contract_type import ContractType

contract_types_bp = Blueprint('contract_types', __name__)


@contract_types_bp.route('', methods=['GET'])
def get_contract_types():
    """
    Get all contract types
    
    Response:
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "name": "service",
                    "description": "Service Agreement"
                }
            ]
        }
    """
    try:
        types = ContractType.query.all()
        
        types_data = []
        for contract_type in types:
            types_data.append({
                'id': contract_type.id,
                'name': contract_type.name,
                'description': contract_type.description
            })
        
        return jsonify({
            'success': True,
            'data': types_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
