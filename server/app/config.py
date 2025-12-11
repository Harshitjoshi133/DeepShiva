"""
Configuration settings for Deep-Shiva API
Handles environment-specific settings and logging configuration
"""

import os

class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # Application settings
        self.app_name = "Deep-Shiva API"
        self.app_version = "1.0.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # Database settings
        self.database_url = os.getenv("DATABASE_URL")
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")  # json or console
        self.log_file_max_size = int(os.getenv("LOG_FILE_MAX_SIZE", "10485760"))  # 10MB
        self.log_file_backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))
        
        # Security settings
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # requests per minute
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))    # seconds
        
        # Performance settings
        self.slow_query_threshold = float(os.getenv("SLOW_QUERY_THRESHOLD", "1000.0"))  # milliseconds
        self.slow_api_threshold = float(os.getenv("SLOW_API_THRESHOLD", "2000.0"))    # milliseconds
        
        # Monitoring settings
        self.enable_performance_monitoring = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
        self.enable_security_monitoring = os.getenv("ENABLE_SECURITY_MONITORING", "true").lower() == "true"
        self.enable_error_tracking = os.getenv("ENABLE_ERROR_TRACKING", "true").lower() == "true"
        
        # Database logging
        self.sqlalchemy_verbose = os.getenv("SQLALCHEMY_VERBOSE", "false").lower() == "true"
        
        # AI Logging
        self.ai_logging_verbose = os.getenv("AI_LOGGING_VERBOSE", "true").lower() == "true"
        
        # Ollama Configuration
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:1b")
        self.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))
        self.ollama_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        self.ollama_max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "1000"))

# Global settings instance
settings = Settings()

def get_log_config():
    """Get logging configuration based on environment"""
    return {
        "level": settings.log_level,
        "format": settings.log_format,
        "environment": settings.environment,
        "debug": settings.debug
    }

def get_performance_config():
    """Get performance monitoring configuration"""
    return {
        "slow_query_threshold": settings.slow_query_threshold,
        "slow_api_threshold": settings.slow_api_threshold,
        "enable_monitoring": settings.enable_performance_monitoring
    }

def get_security_config():
    """Get security configuration"""
    return {
        "rate_limit_requests": settings.rate_limit_requests,
        "rate_limit_window": settings.rate_limit_window,
        "enable_monitoring": settings.enable_security_monitoring
    }