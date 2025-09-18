"""
Flask Application Factory for HEMIS
Creates and configures the Flask application
"""

from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app(config_name=None):
    """Application factory function"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from .config import config
    app.config.from_object(config[config_name])
    
    # Set secret key for sessions
    app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configure session settings for better persistence
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # 30 days
    app.config['SESSION_COOKIE_MAX_AGE'] = 30 * 24 * 60 * 60  # 30 days in seconds
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    return app

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # CORS - Development configuration (more permissive)
    if app.config['DEBUG']:
        # In development, allow all origins for easier testing
        CORS(app, 
             origins="*",
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
             expose_headers=['Content-Type', 'Authorization'])
    else:
        # In production, use configured origins
        CORS(app, 
             origins=app.config['CORS_ORIGINS'], 
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
             expose_headers=['Content-Type', 'Authorization'])
    
    # Rate limiting configuration
    if app.config['DEBUG']:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        app.logger.info('Rate limiting: Using in-memory storage')
    else:
        try:
            redis_url = f"redis://{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/{app.config['REDIS_DB']}"
            if app.config['REDIS_PASSWORD']:
                redis_url = f"redis://:{app.config['REDIS_PASSWORD']}@{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/{app.config['REDIS_DB']}"
            
            import redis
            test_client = redis.from_url(redis_url)
            test_client.ping()
            
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=["200 per day", "50 per hour"],
                storage_uri=redis_url
            )
            app.logger.info(f'Rate limiting: Using Redis storage at {app.config["REDIS_HOST"]}:{app.config["REDIS_PORT"]}')
            
        except Exception as e:
            app.logger.warning(f'Redis unavailable ({e}), falling back to in-memory rate limiting')
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=["200 per day", "50 per hour"]
            )
            app.logger.info('Rate limiting: Using in-memory storage')
    
    # Store limiter in app context for use in routes
    app.limiter = limiter
    
    # Initialize SocketIO for WebSocket support
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    app.socketio = socketio
    
    # Initialize WebSocket service
    from .services.websocket_service import initialize_websocket_service
    initialize_websocket_service(socketio)

def setup_logging(app):
    """Setup application logging (always to stdout for Docker)"""
    # Remove default handlers
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # Stream handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO")))

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    console_handler.setFormatter(formatter)

    app.logger.addHandler(console_handler)
    app.logger.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO")))

    mode = "Development" if app.debug else "Production"
    app.logger.info(f"HEMIS startup - {mode} mode with console logging")

def register_blueprints(app):
    """Register Flask blueprints"""
    
    # Import blueprints here to avoid circular imports
    from .routes import auth, patients, telemetry, vital_signs
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(patients.bp, url_prefix='/api/patients')
    app.register_blueprint(telemetry.bp, url_prefix='/api/telemetry')
    app.register_blueprint(vital_signs.bp, url_prefix='/api/vital-signs')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'HEMIS'}
    
    # Debug logging test endpoint
    @app.route('/test-logging')
    def test_logging():
        """Test endpoint to verify logging is working"""
        app.logger.debug('This is a DEBUG message')
        app.logger.info('This is an INFO message')
        app.logger.warning('This is a WARNING message')
        app.logger.error('This is an ERROR message')
        
        return {
            'message': 'Logging test completed',
            'check_console': 'Look for the log messages above in your terminal'
        }

def setup_error_handlers(app):
    """Setup error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        response = {'error': 'Not found'}
        return response, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        response = {'error': 'Internal server error'}
        return response, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        response = {'error': 'Forbidden'}
        return response, 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        response = {'error': 'Unauthorized'}
        return response, 401

# Create app instance for use in other modules
app = create_app()
