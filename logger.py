"""
Centralized logging system for the C2 controller
"""
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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

# Create global logger instance
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