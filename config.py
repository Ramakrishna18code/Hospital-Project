"""
Configuration file for SecureHealth AI Backend
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'securehealth-ai-2024-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # CORS configuration
    CORS_ORIGINS = ["http://localhost:8000", "http://localhost:3000"]
    
    # Blockchain configuration
    BLOCKCHAIN_DIFFICULTY = 2
    BLOCKCHAIN_AUTO_MINE = True
    
    # Federated Learning configuration
    FL_MAX_PARTICIPANTS = 100
    FL_MIN_PARTICIPANTS = 2
    FL_ROUNDS_LIMIT = 100
    
    # SMPC configuration
    SMPC_ENCRYPTION_ALGORITHM = 'Fernet'
    SMPC_DIFFERENTIAL_PRIVACY_EPSILON = 1.0


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///securehealth_dev.db'
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///securehealth.db'
    SESSION_COOKIE_SECURE = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
