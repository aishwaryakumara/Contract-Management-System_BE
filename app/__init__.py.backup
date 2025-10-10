import os
from flask import Flask
from app.config import config
from app.extensions import db, jwt
from flask_cors import CORS

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Simple CORS - allow all origins for now
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API blueprints
    from app.api import api_v1
    app.register_blueprint(api_v1, url_prefix='/api')
    
    # Import models to register them with SQLAlchemy
    with app.app_context():
        from app import models
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['LOG_FILE']), exist_ok=True)
    
    return app
