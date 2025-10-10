from app.models.activity_history import ActivityHistory
from app.extensions import db
from flask_jwt_extended import get_jwt_identity


def log_activity(contract_instance_id, activity_type, message, changes=None):
    """
    Log activity for a contract
    
    Args:
        contract_instance_id: Contract instance ID (e.g., "CTR_abc123_V1")
        activity_type: 'created', 'modified', 'document_uploaded', 'document_deleted', 'status_changed'
        message: Description of what happened
        changes: List of {field, oldValue, newValue} dicts (for modified type)
    
    Example:
        log_activity(
            contract_instance_id="CTR_abc_V1",
            activity_type="modified",
            message="Contract updated",
            changes=[
                {'field': 'clientName', 'oldValue': 'Acme', 'newValue': 'Acme Corp'},
                {'field': 'value', 'oldValue': '50000', 'newValue': '75000'}
            ]
        )
    """
    try:
        # Get current user from JWT token
        try:
            current_user = get_jwt_identity()
            user_email = current_user.get('email', 'Unknown') if isinstance(current_user, dict) else current_user
        except:
            user_email = 'System'
        
        # Build details object
        details = {'message': message}
        if changes:
            details['changes'] = changes
        
        # Create activity record
        activity = ActivityHistory(
            contract_instance_id=contract_instance_id,
            type=activity_type,
            user=user_email,
            details=details
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Error logging activity: {e}")
        # Don't fail the main operation if logging fails
        db.session.rollback()
        return False
