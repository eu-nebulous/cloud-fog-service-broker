class Config:
    """Base configuration."""
    # General config
    SECRET_KEY = '12345'
    # Other configurations

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Development-specific configurations

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    # Testing-specific configurations

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Production-specific configurations
