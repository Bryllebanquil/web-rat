"""
Security middleware and utilities for the C2 controller
"""
import time
import hashlib
import hmac
from functools import wraps
from typing import Dict, Optional, Callable, Any
from flask import request, jsonify, g
from collections import defaultdict, deque
import re

from config import config
from logger import log_security_event, log_warning, log_error

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
        # Check for forwarded headers (behind proxy)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or 'unknown'

# Global instances
rate_limiter = RateLimiter()
auth_manager = AuthManager()
validator = InputValidator()

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

def validate_agent_id_param(f: Callable) -> Callable:
    """Decorator to validate agent_id parameter"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        agent_id = kwargs.get('agent_id')
        if agent_id and not validator.validate_agent_id(agent_id):
            log_warning(f"Invalid agent_id format: {agent_id}")
            return jsonify({'error': 'Invalid agent_id format'}), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_json_input(required_fields: list = None):
    """Decorator to validate JSON input"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'Missing required fields: {missing_fields}'
                    }), 400
            
            # Store validated data in Flask's g object
            g.validated_data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def security_headers(f: Callable) -> Callable:
    """Add security headers to response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Convert response to Flask Response object if needed
        if not hasattr(response, 'headers'):
            from flask import make_response
            response = make_response(response)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        if config.is_production():
            response.headers['Server'] = 'Secure-Server'
        
        return response
    return decorated_function

def log_request(f: Callable) -> Callable:
    """Log all requests for auditing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = auth_manager.get_client_ip()
        
        # Log request start
        log_security_event(
            'REQUEST_START',
            f'{request.method} {request.endpoint}',
            extra={
                'ip': client_ip,
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'content_length': request.content_length or 0
            }
        )
        
        try:
            result = f(*args, **kwargs)
            # Log successful completion
            status_code = getattr(result, 'status_code', 200)
            if hasattr(result, '__getitem__') and len(result) > 1:
                status_code = result[1]
            
            log_security_event(
                'REQUEST_SUCCESS',
                f'{request.method} {request.endpoint} - {status_code}',
                extra={'ip': client_ip, 'status_code': status_code}
            )
            return result
            
        except Exception as e:
            # Log errors
            log_security_event(
                'REQUEST_ERROR',
                f'{request.method} {request.endpoint} - Error: {str(e)}',
                severity='HIGH',
                extra={'ip': client_ip, 'error': str(e)}
            )
            raise
    
    return decorated_function