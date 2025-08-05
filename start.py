#!/usr/bin/env python3
"""
Secure startup script for the C2 Controller
"""
import os
import sys
import secrets
from pathlib import Path

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")

# Import our modules
from config import config, Config
from logger import controller_logger, log_info, log_error, log_security_event

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
        load_dotenv()
        return True
    
    return False

def check_security():
    """Perform security checks"""
    issues = []
    
    # Check API key strength
    if config.REQUIRE_AUTH and len(config.API_KEY) < 16:
        issues.append("API_KEY is too short (minimum 16 characters)")
    
    # Check if running as root
    if os.getuid() == 0:
        issues.append("Running as root is not recommended")
    
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
    required_modules = ['flask', 'requests', 'cryptography']
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

def main():
    """Main startup function"""
    print("🚀 Starting C2 Controller...")
    print("=" * 50)
    
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
    
    print(f"\n🌐 Controller will be available at:")
    print(f"   • http://{config.HOST}:{config.PORT}")
    print(f"   • Reverse shell port: {config.REVERSE_SHELL_PORT}")
    
    print("\n" + "=" * 50)
    print("Starting Flask application...")
    
    try:
        # Import and start the controller
        from controller_secure import app, start_reverse_shell_server, start_cleanup_thread
        
        # Start background services
        log_info("Starting reverse shell server...")
        start_reverse_shell_server()
        
        log_info("Starting agent monitoring...")
        start_cleanup_thread()
        
        # Start Flask app
        log_info(f"Starting Flask web server on {config.HOST}:{config.PORT}")
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        log_info("Received shutdown signal")
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        log_error(f"Fatal error during startup: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()