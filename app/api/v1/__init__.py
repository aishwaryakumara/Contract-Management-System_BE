"""API v1 Blueprint Registration"""

from flask import Blueprint
from app.api.v1.auth import auth_bp
from app.api.v1.contracts import contracts_bp
from app.api.v1.documents import documents_bp
from app.api.v1.contract_types import contract_types_bp
from app.api.v1.contract_status import contract_status_bp

# Create v1 API blueprint
api_v1 = Blueprint('api_v1', __name__)

# Register sub-blueprints
api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(contracts_bp, url_prefix='/contracts')
api_v1.register_blueprint(documents_bp, url_prefix='/documents')
api_v1.register_blueprint(contract_types_bp, url_prefix='/contract-types')
api_v1.register_blueprint(contract_status_bp, url_prefix='/contract-status')
