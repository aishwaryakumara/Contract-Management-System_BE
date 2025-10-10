import os
import logging
import uuid
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g
from pythonjsonlogger import jsonlogger
from app.config import config
from app.extensions import db, jwt, migrate
from flask_cors import CORS
import time


def setup_logging(app):
    """Setup production-grade JSON logging"""
    
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    os.makedirs(log_dir, exist_ok=True)
    
    # JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['timestamp'] = record.created
            log_record['level'] = record.levelname
            log_record['service'] = 'contract-management-api'
            # Only add request_id if we're in a request context
            try:
                if hasattr(g, 'request_id'):
                    log_record['request_id'] = g.request_id
            except RuntimeError:
                # Not in request context, skip request_id
                pass
    
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(message)s')
    
    # Console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # File
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Errors
    error_handler = RotatingFileHandler(
        app.config['LOG_FILE'].replace('.log', '_errors.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    app.logger.handlers = []
    app.logger.addHandler(console)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)


def register_request_logging(app):
    """Log all requests with request ID"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        # Generate request ID ourselves
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        app.logger.info('Request started', extra={
            'method': request.method,
            'endpoint': request.path
        })
    
    @app.after_request
    def after_request(response):
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.request_id
        
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000
            app.logger.info('Request completed', extra={
                'duration_ms': round(duration, 2),
                'status_code': response.status_code,
                'method': request.method,
                'endpoint': request.path
            })
        return response


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register request logging
    register_request_logging(app)
    
    # Register blueprints
    from app.api import api_v1
    app.register_blueprint(api_v1, url_prefix='/api')
    
    # Import models
    with app.app_context():
        from app import models
    
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.logger.info('Application started', extra={'environment': config_name})
    return app
