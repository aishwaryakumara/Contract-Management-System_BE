"""Contract management API endpoints"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.contract_service import ContractService

contracts_bp = Blueprint('contracts', __name__)

# Initialize service
contract_service = ContractService()


@contracts_bp.route('', methods=['GET'])
@jwt_required()
def get_all_contracts():
    """
    Get all contracts
    
    Response:
        {
            "success": true,
            "data": [
                {
                    "id": "CTR_uuid_V1",
                    "contractId": "uuid",
                    "contractName": "...",
                    "clientName": "...",
                    ...
                }
            ]
        }
    """
    try:
        contracts_data = contract_service.get_all_contracts()
        return jsonify({
            'success': True,
            'data': contracts_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contracts_bp.route('', methods=['POST'])
@jwt_required()
def create_contract():
    """
    Create new contract with file upload
    
    Request (multipart/form-data):
        contractName: string
        clientName: string
        contractType: string
        startDate: string (YYYY-MM-DD)
        endDate: string (YYYY-MM-DD)
        value: number
        status: string
        description: string
        file: file
    
    Response:
        {
            "success": true,
            "message": "Contract created successfully",
            "data": {
                "id": "CTR_uuid_V1",
                "contractId": "uuid",
                "contractName": "...",
                "fileName": "contract.docx"
            }
        }
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # Parse form data
        data = {
            'contractName': request.form.get('contractName', '').strip(),
            'clientName': request.form.get('clientName', '').strip(),
            'contractType': request.form.get('contractType', '').strip(),
            'startDate': request.form.get('startDate', '').strip(),
            'endDate': request.form.get('endDate', '').strip(),
            'value': request.form.get('value', '').strip(),
            'description': request.form.get('description', '')
        }
        
        file = request.files.get('file')
        
        # Call service
        result = contract_service.create_contract(data, file, current_user_id)
        
        return jsonify({
            'success': True,
            'message': 'Contract created successfully',
            'data': result
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contracts_bp.route('/<string:instance_id>', methods=['GET'])
@jwt_required()
def get_contract_details(instance_id):
    """
    Get contract details with all documents
    
    Response:
        {
            "success": true,
            "data": {
                "contract": { ... },
                "documents": [ ... ]
            }
        }
    """
    try:
        result = contract_service.get_contract_details(instance_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contracts_bp.route('/<string:instance_id>', methods=['PUT'])
@jwt_required()
def update_contract(instance_id):
    """
    Update contract metadata (not file)
    
    Request:
        {
            "contractName": "...",
            "clientName": "...",
            "contractType": "...",
            "startDate": "...",
            "endDate": "...",
            "value": "...",
            "status": "...",
            "description": "..."
        }
    
    Response:
        {
            "success": true,
            "message": "Contract updated successfully",
            "data": {
                "id": "...",
                "lastModified": "..."
            }
        }
    """
    try:
        data = request.get_json()
        
        contract = contract_service.update_contract(instance_id, data)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Contract updated successfully',
            'data': {
                'id': contract.contract_instance_id,
                'lastModified': contract.updated_at.isoformat()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contracts_bp.route('/<string:instance_id>/documents', methods=['POST'])
@jwt_required()
def upload_document_to_contract(instance_id):
    """
    Upload additional document to contract
    
    Request (multipart/form-data):
        file: file
        documentType: string (optional)
    
    Response:
        {
            "success": true,
            "message": "Document uploaded successfully",
            "data": {
                "id": 2,
                "contractId": "...",
                "fileName": "...",
                "fileSize": 102400,
                "uploadedAt": "..."
            }
        }
    """
    try:
        current_user_id = int(get_jwt_identity())
        file = request.files.get('file')
        
        if not file:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        result = contract_service.upload_document(instance_id, file, current_user_id)
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'data': result
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contracts_bp.route('/<string:instance_id>/renew', methods=['POST'])
@jwt_required()
def renew_contract(instance_id):
    """
    Renew a contract - creates new version
    
    Request: Form-data
        new_start_date: YYYY-MM-DD (required)
        new_end_date: YYYY-MM-DD (required)
        new_value: float (optional, defaults to old value)
        file: contract document (required)
    
    Response:
        {
            "success": true,
            "message": "Contract renewed successfully",
            "data": {
                "old_version": "CTR_abc123_V1",
                "new_version": "CTR_abc123_V2",
                "new_contract_id": "CTR_abc123_V2"
            }
        }
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # Parse form data
        data = {
            'new_start_date': request.form.get('new_start_date', '').strip(),
            'new_end_date': request.form.get('new_end_date', '').strip(),
            'new_value': request.form.get('new_value', '').strip()
        }
        
        file = request.files.get('file')
        
        # Call service
        result = contract_service.renew_contract(instance_id, data, file, current_user_id)
        
        return jsonify({
            'success': True,
            'message': 'Contract renewed successfully',
            'data': result
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
