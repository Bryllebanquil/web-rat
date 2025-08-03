#!/usr/bin/env python3
"""
High-Performance Screen Capture Module
Optimized for 60+ FPS streaming with sub-100ms latency
"""

import time
import threading
import platform
import numpy as np
import cv2
from typing import Optional, Tuple, Callable
import sys
import logging

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import dxcam
        HAS_DXCAM = True
    except ImportError:
        HAS_DXCAM = False
        import mss
else:
    import mss
    HAS_DXCAM = False

try:
    from turbojpeg import TurboJPEG
    HAS_TURBOJPEG = True
except ImportError:
    HAS_TURBOJPEG = False

try:
    import lz4.frame
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import xxhash
    HAS_XXHASH = True
except ImportError:
    HAS_XXHASH = False

class HighPerformanceCapture:
    """High-performance screen capture with hardware acceleration support"""
    
    def __init__(self, target_fps: int = 60, quality: int = 85, 
                 enable_delta_compression: bool = True):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.quality = quality
        self.enable_delta_compression = enable_delta_compression
        
        # Initialize capture backend
        self.capture_backend = None
        self._init_capture_backend()
        
        # Initialize compression
        self.turbo_jpeg = None
        if HAS_TURBOJPEG:
            self.turbo_jpeg = TurboJPEG()
        
        # Frame management
        self.last_frame = None
        self.last_frame_hash = None
        self.frame_buffer = []
        self.buffer_size = 3  # Triple buffering
        
        # Statistics
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.actual_fps = 0
        
        self.running = False
        self.capture_thread = None
        
        logging.info(f"HighPerformanceCapture initialized:")
        logging.info(f"  - Backend: {self._get_backend_name()}")
        logging.info(f"  - Target FPS: {target_fps}")
        logging.info(f"  - TurboJPEG: {'Available' if HAS_TURBOJPEG else 'Not available'}")
        logging.info(f"  - LZ4: {'Available' if HAS_LZ4 else 'Not available'}")
        logging.info(f"  - Delta compression: {enable_delta_compression}")
    
    def _init_capture_backend(self):
        """Initialize the best available capture backend for the platform"""
        if HAS_DXCAM and platform.system() == "Windows":
            try:
                self.capture_backend = dxcam.create(output_color="RGB")
                self.backend_type = "dxcam"
                logging.info("Using DXcam for screen capture (high performance)")
            except Exception as e:
                logging.warning(f"Failed to initialize DXcam: {e}")
                self._fallback_to_mss()
        else:
            self._fallback_to_mss()
    
    def _fallback_to_mss(self):
        """Fallback to MSS capture"""
        self.capture_backend = mss.mss()
        self.backend_type = "mss"
        logging.info("Using MSS for screen capture (fallback)")
    
    def _get_backend_name(self) -> str:
        """Get the name of the current backend"""
        if hasattr(self, 'backend_type'):
            return self.backend_type.upper()
        return "Unknown"
    
    def capture_frame(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Capture a single frame with optimal performance"""
        try:
            if self.backend_type == "dxcam" and self.capture_backend:
                # DXcam capture (Windows only)
                if region:
                    frame = self.capture_backend.grab(region=region)
                else:
                    frame = self.capture_backend.grab()
                
                if frame is None:
                    return None
                    
                # DXcam returns RGB, no conversion needed
                return frame
                
            elif self.backend_type == "mss":
                # MSS capture
                if region:
                    monitor = {"left": region[0], "top": region[1], 
                              "width": region[2] - region[0], 
                              "height": region[3] - region[1]}
                else:
                    monitor = self.capture_backend.monitors[1]
                
                screenshot = self.capture_backend.grab(monitor)
                frame = np.array(screenshot)
                
                # Convert BGRA to RGB
                if frame.shape[2] == 4:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                elif frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                return frame
                
        except Exception as e:
            logging.error(f"Frame capture error: {e}")
            return None
        
        return None
    
    def encode_frame(self, frame: np.ndarray, force_keyframe: bool = False) -> Optional[bytes]:
        """Encode frame with optimal compression"""
        if frame is None:
            return None
        
        try:
            # Delta compression check
            if self.enable_delta_compression and not force_keyframe:
                if HAS_XXHASH:
                    frame_hash = xxhash.xxh64(frame.tobytes()).hexdigest()
                    if frame_hash == self.last_frame_hash:
                        # No change, return empty data or delta marker
                        return b'DELTA_UNCHANGED'
                    self.last_frame_hash = frame_hash
            
            # Resize for performance if needed
            height, width = frame.shape[:2]
            if width > 1920:
                scale = 1920 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height), 
                                 interpolation=cv2.INTER_AREA)
            
            # Use TurboJPEG if available (faster)
            if HAS_TURBOJPEG and self.turbo_jpeg:
                # Convert RGB to BGR for TurboJPEG
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                encoded = self.turbo_jpeg.encode(frame_bgr, quality=self.quality)
            else:
                # Fallback to OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                success, encoded = cv2.imencode('.jpg', frame_bgr, 
                    [cv2.IMWRITE_JPEG_QUALITY, self.quality,
                     cv2.IMWRITE_JPEG_OPTIMIZE, 1])
                if not success:
                    return None
                encoded = encoded.tobytes()
            
            # Optional LZ4 compression for additional bandwidth savings
            if HAS_LZ4 and len(encoded) > 1024:  # Only compress larger frames
                compressed = lz4.frame.compress(encoded, compression_level=1)
                if len(compressed) < len(encoded):
                    return b'LZ4_COMPRESSED' + compressed
            
            self.last_frame = frame.copy()
            return encoded
            
        except Exception as e:
            logging.error(f"Frame encoding error: {e}")
            return None
    
    def start_capture_stream(self, callback: Callable[[bytes], None], 
                           region: Optional[Tuple[int, int, int, int]] = None):
        """Start continuous capture stream"""
        if self.running:
            return
        
        self.running = True
        self.capture_thread = threading.Thread(
            target=self._capture_loop, 
            args=(callback, region),
            daemon=True
        )
        self.capture_thread.start()
        logging.info("High-performance capture stream started")
    
    def _capture_loop(self, callback: Callable[[bytes], None], 
                     region: Optional[Tuple[int, int, int, int]]):
        """Main capture loop optimized for low latency"""
        last_time = time.time()
        frame_count = 0
        
        while self.running:
            loop_start = time.time()
            
            # Capture frame
            frame = self.capture_frame(region)
            if frame is not None:
                # Encode frame
                encoded = self.encode_frame(frame)
                if encoded and encoded != b'DELTA_UNCHANGED':
                    callback(encoded)
                
                frame_count += 1
            
            # FPS calculation
            current_time = time.time()
            if current_time - self.fps_start_time >= 1.0:
                self.actual_fps = frame_count
                frame_count = 0
                self.fps_start_time = current_time
                if self.actual_fps > 0:
                    logging.debug(f"Actual FPS: {self.actual_fps}")
            
            # Precise timing control
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_time - elapsed)
            
            if sleep_time > 0:
                # Use high-precision sleep
                if sleep_time > 0.001:
                    time.sleep(sleep_time - 0.001)
                
                # Busy wait for final precision
                target_time = loop_start + self.frame_time
                while time.time() < target_time:
                    pass
    
    def stop_capture_stream(self):
        """Stop capture stream"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        logging.info("High-performance capture stream stopped")
    
    def get_stats(self) -> dict:
        """Get capture statistics"""
        return {
            "backend": self._get_backend_name(),
            "target_fps": self.target_fps,
            "actual_fps": self.actual_fps,
            "quality": self.quality,
            "delta_compression": self.enable_delta_compression,
            "turbojpeg": HAS_TURBOJPEG,
            "lz4": HAS_LZ4
        }
    
    def set_quality(self, quality: int):
        """Dynamically adjust encoding quality"""
        self.quality = max(10, min(100, quality))
        logging.info(f"Encoding quality set to {self.quality}")
    
    def set_fps(self, fps: int):
        """Dynamically adjust target FPS"""
        self.target_fps = max(10, min(120, fps))
        self.frame_time = 1.0 / self.target_fps
        logging.info(f"Target FPS set to {self.target_fps}")
    
    def __del__(self):
        """Cleanup"""
        self.stop_capture_stream()
        if hasattr(self, 'capture_backend') and self.backend_type == "dxcam":
            try:
                if hasattr(self.capture_backend, 'release'):
                    self.capture_backend.release()
            except:
                pass


class AdaptiveQualityManager:
    """Manages adaptive quality based on network conditions"""
    
    def __init__(self, capture: HighPerformanceCapture):
        self.capture = capture
        self.bandwidth_samples = []
        self.max_samples = 30
        self.last_adjustment = time.time()
        self.adjustment_interval = 2.0  # seconds
    
    def update_bandwidth(self, bytes_sent: int, time_elapsed: float):
        """Update bandwidth measurement"""
        if time_elapsed > 0:
            bandwidth = bytes_sent / time_elapsed
            self.bandwidth_samples.append(bandwidth)
            
            if len(self.bandwidth_samples) > self.max_samples:
                self.bandwidth_samples.pop(0)
            
            # Adaptive quality adjustment
            current_time = time.time()
            if current_time - self.last_adjustment > self.adjustment_interval:
                self._adjust_quality()
                self.last_adjustment = current_time
    
    def _adjust_quality(self):
        """Adjust quality based on bandwidth"""
        if len(self.bandwidth_samples) < 5:
            return
        
        avg_bandwidth = sum(self.bandwidth_samples) / len(self.bandwidth_samples)
        current_quality = self.capture.quality
        
        # Simple adaptive algorithm
        if avg_bandwidth < 500000:  # < 500KB/s
            new_quality = max(current_quality - 10, 30)
        elif avg_bandwidth > 2000000:  # > 2MB/s
            new_quality = min(current_quality + 5, 95)
        else:
            return  # No change needed
        
        if new_quality != current_quality:
            self.capture.set_quality(new_quality)
            logging.info(f"Adaptive quality: {current_quality} -> {new_quality} "
                        f"(bandwidth: {avg_bandwidth/1024:.1f} KB/s)")


if __name__ == "__main__":
    # Test the capture system
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    def test_callback(data: bytes):
        print(f"Captured frame: {len(data)} bytes")
    
    capture = HighPerformanceCapture(target_fps=60, quality=85)
    
    print("Testing high-performance capture...")
    print(f"Stats: {capture.get_stats()}")
    
    # Test single frame
    frame = capture.capture_frame()
    if frame is not None:
        print(f"Single frame captured: {frame.shape}")
        encoded = capture.encode_frame(frame)
        if encoded:
            print(f"Encoded size: {len(encoded)} bytes")
    
    # Test streaming
    print("Starting 5-second capture test...")
    capture.start_capture_stream(test_callback)
    time.sleep(5)
    capture.stop_capture_stream()
    
    print(f"Final stats: {capture.get_stats()}")