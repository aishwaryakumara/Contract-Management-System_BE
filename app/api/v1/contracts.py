"""Contract management API endpoints"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.contract import Contract
from app.models.contract_type import ContractType
from app.models.contract_status import ContractStatus
from app.models.document import Document
from app.models.user import User

contracts_bp = Blueprint('contracts', __name__)


def get_contract_type_id(type_name):
    """Get contract type ID from name"""
    contract_type = ContractType.query.filter_by(name=type_name).first()
    return contract_type.id if contract_type else None


def get_status_id(status_name):
    """Get status ID from name"""
    status = ContractStatus.query.filter_by(name=status_name).first()
    return status.id if status else None


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        contracts = Contract.query.all()
        
        contracts_data = []
        for contract in contracts:
            # Get creator info
            creator = User.query.get(contract.created_by)
            
            contracts_data.append({
                'id': contract.contract_instance_id,
                'contractId': contract.id,
                'contractName': contract.contract_name,
                'clientName': contract.client_name,
                'contractType': contract.contract_type.name if contract.contract_type else None,
                'startDate': contract.start_date.isoformat() if contract.start_date else None,
                'endDate': contract.end_date.isoformat() if contract.end_date else None,
                'value': str(contract.value) if contract.value else None,
                'status': contract.status.name if contract.status else None,
                'description': None,  # Add description field to model if needed
                'createdAt': contract.created_at.isoformat() if contract.created_at else None,
                'createdBy': creator.email if creator else None,
                'lastModified': contract.updated_at.isoformat() if contract.updated_at else None
            })
        
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
        
        # Get form data (strip whitespace)
        contract_name = request.form.get('contractName', '').strip()
        client_name = request.form.get('clientName', '').strip()
        contract_type = request.form.get('contractType', '').strip()
        start_date = request.form.get('startDate', '').strip()
        end_date = request.form.get('endDate', '').strip()
        value = request.form.get('value', '').strip()
        status = request.form.get('status', 'draft').strip()
        description = request.form.get('description', '')
        
        # Validate required fields
        if not all([contract_name, client_name, contract_type, start_date]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Handle file upload
        file = request.files.get('file')
        file_path = None
        file_name = None
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_name = filename
            
            # Create contract-specific folder
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
        
        # Generate contract ID
        contract_id = Contract.generate_contract_id()
        version = 1
        contract_instance_id = Contract.generate_instance_id(contract_id, version)
        
        # Get contract_type_id and status_id from lookup tables
        contract_type_id = get_contract_type_id(contract_type)
        status_id = get_status_id(status)
        
        if not contract_type_id:
            return jsonify({
                'success': False,
                'error': f'Invalid contract type: {contract_type}'
            }), 400
        
        if not status_id:
            return jsonify({
                'success': False,
                'error': f'Invalid status: {status}'
            }), 400
        
        # Create contract
        new_contract = Contract(
            contract_instance_id=contract_instance_id,
            id=contract_id,
            contract_name=contract_name,
            client_name=client_name,
            contract_type_id=contract_type_id,
            status_id=status_id,
            created_by=current_user_id,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            value=float(value) if value else None,
            version=version
        )
        
        db.session.add(new_contract)
        db.session.flush()  # Get the contract_instance_id
        
        # If file was uploaded, create document entry
        if file_path and file_name:
            document = Document(
                contract_instance_id=new_contract.contract_instance_id,
                document_name=file_name,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                version=1,
                document_type_id=1,  # Main contract type
                uploaded_by=current_user_id,
                uploaded_at=datetime.utcnow()
            )
            db.session.add(document)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contract created successfully',
            'data': {
                'id': new_contract.contract_instance_id,
                'contractId': new_contract.id,
                'contractName': new_contract.contract_name,
                'fileName': file_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
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
        contract = Contract.query.filter_by(contract_instance_id=instance_id).first()
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Get creator info
        creator = User.query.get(contract.created_by)
        
        # Get all documents for this contract
        documents = Document.query.filter_by(contract_instance_id=instance_id).all()
        
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'contractId': doc.contract_instance_id,
                'fileName': doc.document_name,
                'fileSize': doc.file_size,
                'uploadedAt': doc.uploaded_at.isoformat() if doc.uploaded_at else None
            })
        
        contract_data = {
            'id': contract.contract_instance_id,
            'contractId': contract.id,
            'contractName': contract.contract_name,
            'clientName': contract.client_name,
            'contractType': contract.contract_type.name if contract.contract_type else None,
            'startDate': contract.start_date.isoformat() if contract.start_date else None,
            'endDate': contract.end_date.isoformat() if contract.end_date else None,
            'value': str(contract.value) if contract.value else None,
            'status': contract.status.name if contract.status else None,
            'description': None,  # Add description field if needed
            'createdAt': contract.created_at.isoformat() if contract.created_at else None,
            'createdBy': creator.email if creator else None,
            'lastModified': contract.updated_at.isoformat() if contract.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'data': {
                'contract': contract_data,
                'documents': documents_data
            }
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
        
        contract = Contract.query.filter_by(contract_instance_id=instance_id).first()
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Update fields if provided
        if 'contractName' in data:
            contract.contract_name = data['contractName']
        if 'clientName' in data:
            contract.client_name = data['clientName']
        if 'contractType' in data:
            contract_type_id = get_contract_type_id(data['contractType'])
            if contract_type_id:
                contract.contract_type_id = contract_type_id
        if 'status' in data:
            status_id = get_status_id(data['status'])
            if status_id:
                contract.status_id = status_id
        if 'startDate' in data:
            contract.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        if 'endDate' in data:
            contract.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date() if data['endDate'] else None
        if 'value' in data:
            contract.value = float(data['value']) if data['value'] else None
        
        contract.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contract updated successfully',
            'data': {
                'id': contract.contract_instance_id,
                'lastModified': contract.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
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
        
        # Check if contract exists
        contract = Contract.query.filter_by(contract_instance_id=instance_id).first()
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Handle file upload
        file = request.files.get('file')
        if not file or not file.filename:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
        
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Create document entry
        document = Document(
            contract_instance_id=instance_id,
            document_name=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            version=1,
            document_type_id=2,  # Supporting document type
            uploaded_by=current_user_id,
            uploaded_at=datetime.utcnow()
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'data': {
                'id': document.id,
                'contractId': document.contract_instance_id,
                'fileName': document.document_name,
                'fileSize': document.file_size,
                'uploadedAt': document.uploaded_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
