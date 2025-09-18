"""
Configuration module for HEMIS Flask application
Loads settings from environment variables
"""

import os
from typing import List

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Session Configuration
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Server Configuration
    BACKEND_PORT = int(os.getenv('BACKEND_PORT', 5000))
    FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', 5173))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174').split(',')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'hemis_db')
    
    # Database Users (for different roles)
    DB_USER = os.getenv('DB_USER', 'hemis_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    SUPER_ADMIN_DB_USER = os.getenv('SUPER_ADMIN_DB_USER', 'super_admin')
    SUPER_ADMIN_DB_PASSWORD = os.getenv('SUPER_ADMIN_DB_PASSWORD', 'SuperAdmin123')
    
    HR_ADMIN_DB_USER = os.getenv('HR_ADMIN_DB_USER', 'admin_hr')
    HR_ADMIN_DB_PASSWORD = os.getenv('HR_ADMIN_DB_PASSWORD', 'AdminHr123')
    
    MEDICAL_ADMIN_DB_USER = os.getenv('MEDICAL_ADMIN_DB_USER', 'admin_medical')
    MEDICAL_ADMIN_DB_PASSWORD = os.getenv('MEDICAL_ADMIN_DB_PASSWORD', 'AdminMedical123')
    
    FINANCE_ADMIN_DB_USER = os.getenv('FINANCE_ADMIN_DB_USER', 'admin_finance')
    FINANCE_ADMIN_DB_PASSWORD = os.getenv('FINANCE_ADMIN_DB_PASSWORD', 'AdminFinance123')
    
    SYSTEM_ADMIN_DB_USER = os.getenv('SYSTEM_ADMIN_DB_USER', 'admin_system')
    SYSTEM_ADMIN_DB_PASSWORD = os.getenv('SYSTEM_ADMIN_DB_PASSWORD', 'AdminSystem123')
    
    DOCTOR_DB_USER = os.getenv('DOCTOR_DB_USER', 'doctor')
    DOCTOR_DB_PASSWORD = os.getenv('DOCTOR_DB_PASSWORD', 'Doctor123')
    
    NURSE_DB_USER = os.getenv('NURSE_DB_USER', 'nurse')
    NURSE_DB_PASSWORD = os.getenv('NURSE_DB_PASSWORD', 'Nurse123')
    
    RECEPTION_DB_USER = os.getenv('RECEPTION_DB_USER', 'reception')
    RECEPTION_DB_PASSWORD = os.getenv('RECEPTION_DB_PASSWORD', 'Reception123')
    
    COORDINATOR_DB_USER = os.getenv('COORDINATOR_DB_USER', 'coordinator')
    COORDINATOR_DB_PASSWORD = os.getenv('COORDINATOR_DB_PASSWORD', 'Coordinator123')
    
    # IoT Device Configuration
    IOT_API_KEY = os.getenv('IOT_API_KEY', 'your_iot_device_api_key')
    TELEMETRY_UPDATE_INTERVAL = int(os.getenv('TELEMETRY_UPDATE_INTERVAL', 1000))
    
    # Test Credentials (for development)
    DEFAULT_SUPER_ADMIN_EMAIL = os.getenv('DEFAULT_SUPER_ADMIN_EMAIL', 'superadmin@clinic.test')
    DEFAULT_SUPER_ADMIN_PASSWORD = os.getenv('DEFAULT_SUPER_ADMIN_PASSWORD', 'admin123')
    
    DEFAULT_MEDICAL_ADMIN_EMAIL = os.getenv('DEFAULT_MEDICAL_ADMIN_EMAIL', 'medical.admin@clinic.test')
    DEFAULT_MEDICAL_ADMIN_PASSWORD = os.getenv('DEFAULT_MEDICAL_ADMIN_PASSWORD', 'admin123')
    
    DEFAULT_DOCTOR_EMAIL = os.getenv('DEFAULT_DOCTOR_EMAIL', 'greg.house@clinic.test')
    DEFAULT_DOCTOR_PASSWORD = os.getenv('DEFAULT_DOCTOR_PASSWORD', 'admin123')
    
    DEFAULT_NURSE_EMAIL = os.getenv('DEFAULT_NURSE_EMAIL', 'nurse1@clinic.test')
    DEFAULT_NURSE_PASSWORD = os.getenv('DEFAULT_NURSE_PASSWORD', 'admin123')
    
    DEFAULT_RECEPTION_EMAIL = os.getenv('DEFAULT_RECEPTION_EMAIL', 'reception1@clinic.test')
    DEFAULT_RECEPTION_PASSWORD = os.getenv('DEFAULT_RECEPTION_PASSWORD', 'admin123')
    
    # Redis Configuration (optional)
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Database Connection Pool Settings
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))
    
    # Role Database Mapping
    ROLE_DB_MAPPING = os.getenv('ROLE_DB_MAPPING', 'super_admin:hemis_db,admin_hr:hemis_db,admin_medical:hemis_db,admin_finance:hemis_db,admin_system:hemis_db,doctor:hemis_db,nurse:hemis_db,reception:hemis_db,coordinator:hemis_db')
    
    @classmethod
    def get_database_url(cls, role: str = None) -> str:
        """Get database connection URL for a specific role or default"""
        if role:
            user_key = f'{role.upper().replace(" ", "_")}_DB_USER'
            password_key = f'{role.upper().replace(" ", "_")}_DB_PASSWORD'
            
            user = getattr(cls, user_key, cls.DB_USER)
            password = getattr(cls, password_key, cls.DB_PASSWORD)
        else:
            user = cls.DB_USER
            password = cls.DB_PASSWORD
        
        return f"mysql+pymysql://{user}:{password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_role_credentials(cls, role: str) -> dict:
        """Get database credentials for a specific role"""
        role_upper = role.upper().replace(' ', '_')
        user_key = f'{role_upper}_DB_USER'
        password_key = f'{role_upper}_DB_PASSWORD'
        
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': getattr(cls, user_key, cls.DB_USER),
            'password': getattr(cls, password_key, cls.DB_PASSWORD)
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
