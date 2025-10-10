"""Contract service for business logic"""

from datetime import datetime
from typing import Dict, Optional, List
from werkzeug.datastructures import FileStorage
from app.models.contract import Contract
from app.repositories.contract_repository import ContractRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.contract_type_repository import ContractTypeRepository
from app.repositories.contract_status_repository import ContractStatusRepository
from app.services.storage_service import StorageService
from app.utils.activity_logger import log_activity


class ContractService:
    """Service for contract business logic"""
    
    def __init__(self):
        """Initialize contract service with dependencies"""
        self.contract_repo = ContractRepository()
        self.document_repo = DocumentRepository()
        self.user_repo = UserRepository()
        self.contract_type_repo = ContractTypeRepository()
        self.contract_status_repo = ContractStatusRepository()
        self.storage_service = StorageService()
    
    def get_all_contracts(self) -> List[Dict]:
        """
        Get all contracts with creator info
        
        Returns:
            List of contract dictionaries
        """
        contracts = self.contract_repo.find_all_with_details()
        
        contracts_data = []
        for contract in contracts:
            creator = self.user_repo.find_by_id(contract.created_by)
            
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
                'description': contract.description,
                'version': contract.version,
                'renewed_from': contract.renewed_from,
                'renewed_to': contract.renewed_to,
                'createdAt': contract.created_at.isoformat() if contract.created_at else None,
                'createdBy': creator.email if creator else None,
                'lastModified': contract.updated_at.isoformat() if contract.updated_at else None
            })
        
        return contracts_data
    
    def get_contract_details(self, instance_id: str) -> Optional[Dict]:
        """
        Get contract details with documents
        
        Args:
            instance_id: Contract instance ID
            
        Returns:
            Contract details dict or None if not found
        """
        contract = self.contract_repo.find_by_instance_id(instance_id)
        if not contract:
            return None
        
        creator = self.user_repo.find_by_id(contract.created_by)
        documents = self.document_repo.find_by_contract(instance_id)
        
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
            'description': contract.description,
            'version': contract.version,
            'renewed_from': contract.renewed_from,
            'renewed_to': contract.renewed_to,
            'createdAt': contract.created_at.isoformat() if contract.created_at else None,
            'createdBy': creator.email if creator else None,
            'lastModified': contract.updated_at.isoformat() if contract.updated_at else None
        }
        
        return {
            'contract': contract_data,
            'documents': documents_data
        }
    
    def create_contract(self, data: Dict, file: Optional[FileStorage], user_id: int) -> Dict:
        """
        Create new contract with business logic
        
        Args:
            data: Contract data dict
            file: Optional file upload
            user_id: User creating the contract
            
        Returns:
            Created contract info
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['contractName', 'clientName', 'contractType', 'startDate']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'Missing required field: {field}')
        
        # Get type and status IDs
        contract_type_id = self.contract_type_repo.get_id_by_name(data['contractType'])
        if not contract_type_id:
            raise ValueError(f"Invalid contract type: {data['contractType']}")
        
        # Business Rule: All new contracts start as 'draft'
        status_id = self.contract_status_repo.get_id_by_name('draft')
        if not status_id:
            raise ValueError("Draft status not found in database")
        
        # Handle file upload
        file_info = None
        if file:
            file_info = self.storage_service.save_file(file)
        
        # Generate contract IDs
        contract_id = Contract.generate_contract_id()
        version = 1
        contract_instance_id = Contract.generate_instance_id(contract_id, version)
        
        # Create contract
        contract = self.contract_repo.create_contract({
            'contract_instance_id': contract_instance_id,
            'id': contract_id,
            'contract_name': data['contractName'],
            'client_name': data['clientName'],
            'contract_type_id': contract_type_id,
            'status_id': status_id,
            'created_by': user_id,
            'start_date': datetime.strptime(data['startDate'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(data['endDate'], '%Y-%m-%d').date() if data.get('endDate') else None,
            'value': float(data['value']) if data.get('value') else None,
            'version': version,
            'description': data.get('description', '')
        })
        
        # Create document if file uploaded
        if file_info:
            self.document_repo.create_document({
                'contract_instance_id': contract.contract_instance_id,
                'document_name': file_info['filename'],
                'file_path': file_info['path'],
                'file_size': file_info['size'],
                'version': 1,
                'document_type_id': 1,  # Main contract type
                'uploaded_by': user_id,
                'uploaded_at': datetime.utcnow()
            })
        
        self.contract_repo.commit()
        
        # Log creation activity
        log_activity(
            contract_instance_id=contract.contract_instance_id,
            activity_type='created',
            message=f"Contract '{contract.contract_name}' created"
        )
        
        return {
            'id': contract.contract_instance_id,
            'contractId': contract.id,
            'contractName': contract.contract_name,
            'fileName': file_info['filename'] if file_info else None
        }
    
    def update_contract(self, instance_id: str, data: Dict) -> Optional[Contract]:
        """
        Update contract with business logic and validation
        
        Args:
            instance_id: Contract instance ID
            data: Update data
            
        Returns:
            Updated contract or None
            
        Raises:
            ValueError: If validation fails
        """
        contract = self.contract_repo.find_by_instance_id(instance_id)
        if not contract:
            return None
        
        # 1️⃣ CAPTURE OLD VALUES (before any changes)
        old_values = {
            'contractName': contract.contract_name,
            'clientName': contract.client_name,
            'contractType': contract.contract_type.name if contract.contract_type else None,
            'status': contract.status.name if contract.status else None,
            'startDate': contract.start_date.isoformat() if contract.start_date else None,
            'endDate': contract.end_date.isoformat() if contract.end_date else None,
            'value': str(contract.value) if contract.value else None,
            'description': contract.description
        }
        
        # 2️⃣ UPDATE FIELDS
        # Update basic fields
        if 'contractName' in data:
            contract.contract_name = data['contractName']
        if 'clientName' in data:
            contract.client_name = data['clientName']
        if 'contractType' in data:
            contract_type_id = self.contract_type_repo.get_id_by_name(data['contractType'])
            if contract_type_id:
                contract.contract_type_id = contract_type_id
        
        # Handle status changes with business rules
        if 'status' in data:
            new_status = data['status']
            current_status = contract.status.name
            
            # Business Rule: Renewed contracts cannot change status (archived)
            if current_status == 'renewed':
                raise ValueError('Cannot change status of renewed contract. This is an archived version.')
            
            # Business Rule: Active contracts can only move to expired
            if current_status == 'active' and new_status not in ['active', 'expired']:
                raise ValueError(f'Active contracts can only be marked as expired. Cannot change to {new_status}.')
            
            # Business Rule: Expired contracts are locked (cannot change status)
            if current_status == 'expired':
                raise ValueError('Expired contracts are locked and cannot change status. Consider creating a new contract or renewing.')
            
            status_id = self.contract_status_repo.get_id_by_name(new_status)
            if status_id:
                contract.status_id = status_id
            else:
                raise ValueError(f'Invalid status: {new_status}')
        
        if 'startDate' in data:
            contract.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        if 'endDate' in data:
            contract.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date() if data['endDate'] else None
        if 'value' in data:
            contract.value = float(data['value']) if data['value'] else None
        if 'description' in data:
            contract.description = data.get('description')
        
        contract.updated_at = datetime.utcnow()
        
        # 3️⃣ COMPARE & LOG CHANGES
        changes = []
        
        # Check each field for changes
        if old_values['contractName'] != contract.contract_name:
            changes.append({
                'field': 'contractName',
                'oldValue': old_values['contractName'] or 'empty',
                'newValue': contract.contract_name or 'empty'
            })
        
        if old_values['clientName'] != contract.client_name:
            changes.append({
                'field': 'clientName',
                'oldValue': old_values['clientName'] or 'empty',
                'newValue': contract.client_name or 'empty'
            })
        
        new_contract_type = contract.contract_type.name if contract.contract_type else None
        if old_values['contractType'] != new_contract_type:
            changes.append({
                'field': 'contractType',
                'oldValue': old_values['contractType'] or 'empty',
                'newValue': new_contract_type or 'empty'
            })
        
        new_status = contract.status.name if contract.status else None
        if old_values['status'] != new_status:
            changes.append({
                'field': 'status',
                'oldValue': old_values['status'] or 'empty',
                'newValue': new_status or 'empty'
            })
        
        new_start_date = contract.start_date.isoformat() if contract.start_date else None
        if old_values['startDate'] != new_start_date:
            changes.append({
                'field': 'startDate',
                'oldValue': old_values['startDate'] or 'empty',
                'newValue': new_start_date or 'empty'
            })
        
        new_end_date = contract.end_date.isoformat() if contract.end_date else None
        if old_values['endDate'] != new_end_date:
            changes.append({
                'field': 'endDate',
                'oldValue': old_values['endDate'] or 'empty',
                'newValue': new_end_date or 'empty'
            })
        
        new_value = str(contract.value) if contract.value else None
        if old_values['value'] != new_value:
            changes.append({
                'field': 'value',
                'oldValue': f"${old_values['value']}" if old_values['value'] else 'empty',
                'newValue': f"${new_value}" if new_value else 'empty'
            })
        
        if old_values['description'] != contract.description:
            changes.append({
                'field': 'description',
                'oldValue': old_values['description'] or 'empty',
                'newValue': contract.description or 'empty'
            })
        
        # Commit changes
        self.contract_repo.commit()
        
        # 4️⃣ LOG ACTIVITY (only if something actually changed)
        if changes:
            log_activity(
                contract_instance_id=instance_id,
                activity_type='modified',
                message=f'Contract updated - {len(changes)} field(s) changed',
                changes=changes
            )
        
        return contract
    
    def upload_document(self, instance_id: str, file: FileStorage, user_id: int) -> Dict:
        """
        Upload additional document to contract
        
        Args:
            instance_id: Contract instance ID
            file: File to upload
            user_id: User uploading
            
        Returns:
            Document info
            
        Raises:
            ValueError: If validation fails
        """
        # Verify contract exists
        contract = self.contract_repo.find_by_instance_id(instance_id)
        if not contract:
            raise ValueError('Contract not found')
        
        # Save file
        file_info = self.storage_service.save_file(file)
        
        # Create document record
        document = self.document_repo.create_document({
            'contract_instance_id': instance_id,
            'document_name': file_info['filename'],
            'file_path': file_info['path'],
            'file_size': file_info['size'],
            'version': 1,
            'document_type_id': 2,  # Supporting document
            'uploaded_by': user_id,
            'uploaded_at': datetime.utcnow()
        })
        
        self.document_repo.commit()
        
        # Log document upload activity
        log_activity(
            contract_instance_id=instance_id,
            activity_type='document_uploaded',
            message=f"Document '{file_info['filename']}' uploaded"
        )
        
        return {
            'id': document.id,
            'contractId': document.contract_instance_id,
            'fileName': document.document_name,
            'fileSize': document.file_size,
            'uploadedAt': document.uploaded_at.isoformat()
        }
    
    def renew_contract(self, instance_id: str, data: Dict, file: FileStorage, user_id: int) -> Dict:
        """
        Renew a contract - creates new version
        
        Args:
            instance_id: Old contract instance ID
            data: Renewal data (new_start_date, new_end_date, new_value)
            file: New contract document
            user_id: User renewing the contract
            
        Returns:
            Renewal info with old and new version IDs
            
        Raises:
            ValueError: If validation fails
        """
        # Get old contract
        old_contract = self.contract_repo.find_by_instance_id(instance_id)
        if not old_contract:
            raise ValueError('Contract not found')
        
        # Business Rule: Can only renew from 'active' status
        if old_contract.status.name != 'active':
            raise ValueError(f'Can only renew active contracts. Current status: {old_contract.status.name}')
        
        # Business Rule: Cannot renew if already renewed
        if old_contract.renewed_to:
            raise ValueError(f'Contract already renewed to {old_contract.renewed_to}')
        
        # Validate dates
        new_start_date = data.get('new_start_date')
        new_end_date = data.get('new_end_date')
        
        if not new_start_date or not new_end_date:
            raise ValueError('new_start_date and new_end_date are required')
        
        try:
            start_date_obj = datetime.strptime(new_start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(new_end_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')
        
        # Business Rule: End date must be after start date
        if end_date_obj <= start_date_obj:
            raise ValueError('End date must be after start date')
        
        # Business Rule: Start date cannot be in the past
        if start_date_obj < datetime.now().date():
            raise ValueError('Start date cannot be in the past')
        
        # Save new file
        if not file:
            raise ValueError('Contract document is required for renewal')
        
        file_info = self.storage_service.save_file(file)
        
        # Get max version and create new
        new_version = self.contract_repo.get_max_version(old_contract.id) + 1
        new_contract_instance_id = Contract.generate_instance_id(old_contract.id, new_version)
        
        # Get draft status
        draft_status_id = self.contract_status_repo.get_id_by_name('draft')
        if not draft_status_id:
            raise ValueError('Draft status not found in database')
        
        # Create new contract version
        new_contract = self.contract_repo.create_contract({
            'contract_instance_id': new_contract_instance_id,
            'id': old_contract.id,  # Same contract ID to group versions
            'contract_name': old_contract.contract_name,
            'client_name': old_contract.client_name,
            'contract_type_id': old_contract.contract_type_id,
            'status_id': draft_status_id,
            'created_by': user_id,
            'start_date': start_date_obj,
            'end_date': end_date_obj,
            'value': float(data['new_value']) if data.get('new_value') else old_contract.value,
            'version': new_version,
            'renewed_from': old_contract.contract_instance_id,
            'description': old_contract.description
        })
        
        # Create document for new version
        self.document_repo.create_document({
            'contract_instance_id': new_contract_instance_id,
            'document_name': file_info['filename'],
            'file_path': file_info['path'],
            'file_size': file_info['size'],
            'version': 1,
            'document_type_id': 1,
            'uploaded_by': user_id,
            'uploaded_at': datetime.utcnow()
        })
        
        # Update old contract
        renewed_status_id = self.contract_status_repo.get_id_by_name('renewed')
        if renewed_status_id:
            old_contract.status_id = renewed_status_id
        old_contract.renewed_to = new_contract_instance_id
        
        self.contract_repo.commit()
        
        return {
            'old_version': old_contract.contract_instance_id,
            'new_version': new_contract.contract_instance_id,
            'new_contract_id': new_contract.contract_instance_id
        }
