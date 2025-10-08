import os
from flask import Flask
from app.config import config
from app.extensions import db, jwt, cors

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints (will add later)
    # from app.api import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')
    
    # Import models to register them with SQLAlchemy
    with app.app_context():
        from app import models
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['LOG_FILE']), exist_ok=True)
    
    return app
