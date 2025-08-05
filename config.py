"""
Configuration management for the C2 controller
"""
import os
import secrets
from typing import Optional

class Config:
    """Configuration class for the controller"""
    
    # Security settings
    API_KEY: str = os.getenv('API_KEY', secrets.token_urlsafe(32))
    SECRET_KEY: str = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    REQUIRE_AUTH: bool = os.getenv('REQUIRE_AUTH', 'True').lower() == 'true'
    
    # Network settings
    HOST: str = os.getenv('HOST', '127.0.0.1')  # Changed from 0.0.0.0 for security
    PORT: int = int(os.getenv('PORT', '8080'))
    REVERSE_SHELL_PORT: int = int(os.getenv('REVERSE_SHELL_PORT', '9999'))
    
    # Agent settings
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv('AGENT_TIMEOUT_SECONDS', '60'))
    CLEANUP_INTERVAL_SECONDS: int = int(os.getenv('CLEANUP_INTERVAL_SECONDS', '30'))
    MAX_AGENTS: int = int(os.getenv('MAX_AGENTS', '100'))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    MAX_COMMAND_LENGTH: int = int(os.getenv('MAX_COMMAND_LENGTH', '1000'))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'controller.log')
    
    # Production settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return not cls.DEBUG
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        errors = []
        
        if cls.REQUIRE_AUTH and len(cls.API_KEY) < 16:
            errors.append("API_KEY must be at least 16 characters")
        
        if cls.PORT < 1024 and os.getuid() != 0:
            errors.append("Port < 1024 requires root privileges")
        
        if cls.MAX_UPLOAD_SIZE_MB > 100:
            errors.append("MAX_UPLOAD_SIZE_MB should not exceed 100MB")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Print non-sensitive configuration"""
        print("=== Controller Configuration ===")
        print(f"Host: {cls.HOST}")
        print(f"Port: {cls.PORT}")
        print(f"Reverse Shell Port: {cls.REVERSE_SHELL_PORT}")
        print(f"Authentication: {'Enabled' if cls.REQUIRE_AUTH else 'Disabled'}")
        print(f"Debug Mode: {'Enabled' if cls.DEBUG else 'Disabled'}")
        print(f"Max Agents: {cls.MAX_AGENTS}")
        print(f"Agent Timeout: {cls.AGENT_TIMEOUT_SECONDS}s")
        print(f"Rate Limit: {cls.RATE_LIMIT_PER_MINUTE}/min")
        print("===============================")

# Create global config instance
config = Config()