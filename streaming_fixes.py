#!/usr/bin/env python3
"""
Streaming Fixes and Improvements
Comprehensive fixes for screen and camera streaming issues
"""
import time
import threading
import requests
import cv2
import numpy as np
import mss
import hashlib
from typing import Optional, Callable, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingStats:
    """Track streaming performance statistics"""
    
    def __init__(self):
        self.frames_sent = 0
        self.bytes_sent = 0
        self.frames_dropped = 0
        self.start_time = time.time()
        self.last_fps_time = time.time()
        self.fps = 0
        
    def update_frame(self, bytes_count: int):
        """Update stats when a frame is sent"""
        self.frames_sent += 1
        self.bytes_sent += bytes_count
        
        # Calculate FPS every second
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frames_sent / (current_time - self.start_time)
            self.last_fps_time = current_time
    
    def drop_frame(self):
        """Record dropped frame"""
        self.frames_dropped += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        runtime = time.time() - self.start_time
        return {
            "runtime": runtime,
            "frames_sent": self.frames_sent,
            "frames_dropped": self.frames_dropped,
            "bytes_sent": self.bytes_sent,
            "fps": self.fps,
            "avg_frame_size": self.bytes_sent / max(1, self.frames_sent),
            "drop_rate": self.frames_dropped / max(1, self.frames_sent + self.frames_dropped)
        }

class AdaptiveCompression:
    """Adaptive compression based on network conditions"""
    
    def __init__(self, initial_quality: int = 85):
        self.quality = initial_quality
        self.min_quality = 30
        self.max_quality = 95
        self.response_times = []
        self.max_samples = 10
        
    def update_response_time(self, response_time: float):
        """Update compression based on response time"""
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_samples:
            self.response_times.pop(0)
            
        # Adjust quality based on average response time
        avg_time = sum(self.response_times) / len(self.response_times)
        
        if avg_time > 0.5:  # High latency
            self.quality = max(self.min_quality, self.quality - 5)
        elif avg_time < 0.1:  # Low latency
            self.quality = min(self.max_quality, self.quality + 2)
    
    def get_quality(self) -> int:
        """Get current quality setting"""
        return self.quality

class ImprovedScreenStreamer:
    """Improved screen streaming with better error handling and performance"""
    
    def __init__(self, server_url: str, agent_id: str, target_fps: int = 30):
        self.server_url = server_url
        self.agent_id = agent_id
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.stats = StreamingStats()
        self.compression = AdaptiveCompression()
        
        # Frame processing
        self.last_frame_hash = None
        self.frame_skip_count = 0
        self.max_skip_frames = 3
        
        # Connection settings
        self.url = f"{server_url}/stream/{agent_id}"
        self.headers = {'Content-Type': 'image/jpeg'}
        self.timeout = 0.1
        
    def start(self):
        """Start the streaming thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.thread.start()
            logger.info(f"Started screen streaming for agent {self.agent_id}")
    
    def stop(self):
        """Stop the streaming thread"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            logger.info(f"Stopped screen streaming for agent {self.agent_id}")
            
            # Log final stats
            final_stats = self.stats.get_stats()
            logger.info(f"Final streaming stats: {final_stats}")
    
    def _stream_loop(self):
        """Main streaming loop with enhanced error handling"""
        with mss.mss() as sct:
            consecutive_errors = 0
            max_consecutive_errors = 10
            
            while self.running and consecutive_errors < max_consecutive_errors:
                try:
                    frame_start = time.time()
                    
                    # Capture screen
                    frame_data = self._capture_frame(sct)
                    if frame_data is None:
                        consecutive_errors += 1
                        continue
                    
                    # Check if frame is duplicate
                    if self._is_duplicate_frame(frame_data):
                        self._maintain_fps(frame_start)
                        continue
                    
                    # Encode frame
                    encoded_frame = self._encode_frame(frame_data)
                    if encoded_frame is None:
                        consecutive_errors += 1
                        continue
                    
                    # Send frame
                    success = self._send_frame(encoded_frame, frame_start)
                    if success:
                        consecutive_errors = 0
                        self.stats.update_frame(len(encoded_frame))
                    else:
                        consecutive_errors += 1
                        self.stats.drop_frame()
                    
                    # Maintain target FPS
                    self._maintain_fps(frame_start)
                    
                except Exception as e:
                    logger.error(f"Error in streaming loop: {e}")
                    consecutive_errors += 1
                    time.sleep(0.1)
            
            if consecutive_errors >= max_consecutive_errors:
                logger.error("Too many consecutive errors, stopping stream")
    
    def _capture_frame(self, sct) -> Optional[np.ndarray]:
        """Capture screen frame with error handling"""
        try:
            # Capture primary monitor
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            sct_img = sct.grab(monitor)
            
            # Convert to numpy array
            frame = np.array(sct_img)
            
            # Handle different color formats
            if frame.shape[2] == 4:  # BGRA
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            elif frame.shape[2] == 3:  # BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def _is_duplicate_frame(self, frame: np.ndarray) -> bool:
        """Check if frame is duplicate to previous frame"""
        try:
            # Create hash of frame data
            frame_hash = hashlib.md5(frame.tobytes()).hexdigest()
            
            if frame_hash == self.last_frame_hash:
                self.frame_skip_count += 1
                if self.frame_skip_count < self.max_skip_frames:
                    return True
            else:
                self.frame_skip_count = 0
                self.last_frame_hash = frame_hash
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking frame duplicate: {e}")
            return False
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode frame with adaptive compression"""
        try:
            # Resize large frames for better performance
            height, width = frame.shape[:2]
            if width > 1920:
                scale = 1920 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height), 
                                 interpolation=cv2.INTER_AREA)
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Encode with adaptive quality
            quality = self.compression.get_quality()
            success, buffer = cv2.imencode('.jpg', frame_bgr, [
                cv2.IMWRITE_JPEG_QUALITY, quality,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                cv2.IMWRITE_JPEG_PROGRESSIVE, 1
            ])
            
            if success:
                return buffer.tobytes()
            else:
                logger.error("Failed to encode frame")
                return None
                
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return None
    
    def _send_frame(self, frame_data: bytes, start_time: float) -> bool:
        """Send frame to server with response time tracking"""
        try:
            response = requests.post(
                self.url, 
                data=frame_data, 
                headers=self.headers, 
                timeout=self.timeout
            )
            
            # Update compression based on response time
            response_time = time.time() - start_time
            self.compression.update_response_time(response_time)
            
            return response.status_code == 200
            
        except requests.exceptions.Timeout:
            # Timeout is acceptable for low-latency streaming
            return False
        except Exception as e:
            logger.error(f"Error sending frame: {e}")
            return False
    
    def _maintain_fps(self, frame_start: float):
        """Maintain target FPS timing"""
        elapsed = time.time() - frame_start
        sleep_time = max(0, self.frame_time - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

class ImprovedCameraStreamer:
    """Improved camera streaming with better error handling"""
    
    def __init__(self, server_url: str, agent_id: str, camera_id: int = 0, target_fps: int = 30):
        self.server_url = server_url
        self.agent_id = agent_id
        self.camera_id = camera_id
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.stats = StreamingStats()
        self.compression = AdaptiveCompression()
        
        # Camera settings
        self.cap: Optional[cv2.VideoCapture] = None
        self.url = f"{server_url}/camera/{agent_id}"
        self.headers = {'Content-Type': 'image/jpeg'}
        self.timeout = 0.5
    
    def start(self):
        """Start camera streaming"""
        if not self.running:
            if self._init_camera():
                self.running = True
                self.thread = threading.Thread(target=self._stream_loop, daemon=True)
                self.thread.start()
                logger.info(f"Started camera streaming for agent {self.agent_id}")
            else:
                logger.error("Failed to initialize camera")
    
    def stop(self):
        """Stop camera streaming"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            if self.cap:
                self.cap.release()
            logger.info(f"Stopped camera streaming for agent {self.agent_id}")
            
            # Log final stats
            final_stats = self.stats.get_stats()
            logger.info(f"Final camera stats: {final_stats}")
    
    def _init_camera(self) -> bool:
        """Initialize camera with proper settings"""
        try:
            # Try different backends
            backends = [cv2.CAP_V4L2, cv2.CAP_ANY]
            
            for backend in backends:
                self.cap = cv2.VideoCapture(self.camera_id, backend)
                if self.cap.isOpened():
                    break
            
            if not self.cap or not self.cap.isOpened():
                logger.error(f"Cannot open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.error("Camera test capture failed")
                return False
            
            logger.info(f"Camera initialized: {frame.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    def _stream_loop(self):
        """Main camera streaming loop"""
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running and consecutive_errors < max_consecutive_errors:
            try:
                frame_start = time.time()
                
                # Capture frame
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    consecutive_errors += 1
                    time.sleep(0.1)
                    continue
                
                # Encode frame
                encoded_frame = self._encode_frame(frame)
                if encoded_frame is None:
                    consecutive_errors += 1
                    continue
                
                # Send frame
                success = self._send_frame(encoded_frame, frame_start)
                if success:
                    consecutive_errors = 0
                    self.stats.update_frame(len(encoded_frame))
                else:
                    consecutive_errors += 1
                    self.stats.drop_frame()
                
                # Maintain target FPS
                self._maintain_fps(frame_start)
                
            except Exception as e:
                logger.error(f"Error in camera loop: {e}")
                consecutive_errors += 1
                time.sleep(0.1)
        
        if consecutive_errors >= max_consecutive_errors:
            logger.error("Too many consecutive camera errors, stopping stream")
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode camera frame"""
        try:
            quality = self.compression.get_quality()
            success, buffer = cv2.imencode('.jpg', frame, [
                cv2.IMWRITE_JPEG_QUALITY, quality,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])
            
            if success:
                return buffer.tobytes()
            else:
                logger.error("Failed to encode camera frame")
                return None
                
        except Exception as e:
            logger.error(f"Error encoding camera frame: {e}")
            return None
    
    def _send_frame(self, frame_data: bytes, start_time: float) -> bool:
        """Send camera frame to server"""
        try:
            response = requests.post(
                self.url,
                data=frame_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Update compression based on response time
            response_time = time.time() - start_time
            self.compression.update_response_time(response_time)
            
            return response.status_code == 200
            
        except requests.exceptions.Timeout:
            return False
        except Exception as e:
            logger.error(f"Error sending camera frame: {e}")
            return False
    
    def _maintain_fps(self, frame_start: float):
        """Maintain target FPS"""
        elapsed = time.time() - frame_start
        sleep_time = max(0, self.frame_time - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

class StreamManager:
    """Manages multiple streams and provides status information"""
    
    def __init__(self, server_url: str, agent_id: str):
        self.server_url = server_url
        self.agent_id = agent_id
        self.screen_streamer: Optional[ImprovedScreenStreamer] = None
        self.camera_streamer: Optional[ImprovedCameraStreamer] = None
    
    def start_screen_stream(self, fps: int = 30):
        """Start screen streaming"""
        if self.screen_streamer is None or not self.screen_streamer.running:
            self.screen_streamer = ImprovedScreenStreamer(
                self.server_url, self.agent_id, fps
            )
            self.screen_streamer.start()
            return True
        return False
    
    def stop_screen_stream(self):
        """Stop screen streaming"""
        if self.screen_streamer and self.screen_streamer.running:
            self.screen_streamer.stop()
            return True
        return False
    
    def start_camera_stream(self, fps: int = 30, camera_id: int = 0):
        """Start camera streaming"""
        if self.camera_streamer is None or not self.camera_streamer.running:
            self.camera_streamer = ImprovedCameraStreamer(
                self.server_url, self.agent_id, camera_id, fps
            )
            self.camera_streamer.start()
            return True
        return False
    
    def stop_camera_stream(self):
        """Stop camera streaming"""
        if self.camera_streamer and self.camera_streamer.running:
            self.camera_streamer.stop()
            return True
        return False
    
    def stop_all_streams(self):
        """Stop all active streams"""
        self.stop_screen_stream()
        self.stop_camera_stream()
    
    def get_status(self) -> Dict[str, Any]:
        """Get streaming status and statistics"""
        status = {
            "screen_streaming": False,
            "camera_streaming": False,
            "screen_stats": None,
            "camera_stats": None
        }
        
        if self.screen_streamer and self.screen_streamer.running:
            status["screen_streaming"] = True
            status["screen_stats"] = self.screen_streamer.stats.get_stats()
        
        if self.camera_streamer and self.camera_streamer.running:
            status["camera_streaming"] = True
            status["camera_stats"] = self.camera_streamer.stats.get_stats()
        
        return status

# Test function
def test_streaming():
    """Test the improved streaming functionality"""
    server_url = "http://localhost:8080"
    agent_id = "test_agent"
    
    manager = StreamManager(server_url, agent_id)
    
    print("Testing screen streaming...")
    manager.start_screen_stream(fps=15)  # Lower FPS for testing
    
    print("Testing camera streaming...")
    manager.start_camera_stream(fps=15)
    
    # Run for 10 seconds
    time.sleep(10)
    
    print("Final status:", manager.get_status())
    manager.stop_all_streams()

if __name__ == "__main__":
    test_streaming()