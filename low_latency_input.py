#!/usr/bin/env python3
"""
Low-Latency Input Handler
Optimized for sub-2-second mouse and keyboard latency
"""

import time
import threading
import queue
import logging
from typing import Dict, Any, Callable, Optional
import platform

# Input libraries
from pynput import mouse, keyboard
import pyautogui

# Fast serialization
try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    import json
    HAS_MSGPACK = False

# Performance optimizations
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # Remove delay between commands

class LowLatencyInputHandler:
    """Ultra-low latency input handling system"""
    
    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        self.input_queue = queue.Queue(maxsize=max_queue_size)
        self.processing_thread = None
        self.running = False
        
        # Input controllers
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        # Performance tracking
        self.input_count = 0
        self.last_input_time = time.time()
        self.processing_times = []
        
        # Input state caching for smooth movement
        self.last_mouse_pos = self.mouse_controller.position
        self.mouse_acceleration = 1.0
        self.smooth_mouse = True
        
        logging.info("LowLatencyInputHandler initialized")
        logging.info(f"  - Max queue size: {max_queue_size}")
        logging.info(f"  - Platform: {platform.system()}")
    
    def start(self):
        """Start the input processing thread"""
        if self.running:
            return
        
        self.running = True
        self.processing_thread = threading.Thread(
            target=self._process_input_loop,
            daemon=True
        )
        self.processing_thread.start()
        logging.info("Low-latency input processing started")
    
    def stop(self):
        """Stop input processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        logging.info("Low-latency input processing stopped")
    
    def handle_input(self, input_data: Dict[str, Any]) -> bool:
        """Queue input for processing"""
        try:
            if self.input_queue.full():
                # Drop oldest input if queue is full (prefer latest)
                try:
                    self.input_queue.get_nowait()
                except queue.Empty:
                    pass
            
            # Add timestamp for latency measurement
            input_data['timestamp'] = time.time()
            self.input_queue.put_nowait(input_data)
            return True
            
        except queue.Full:
            logging.warning("Input queue overflow - dropping input")
            return False
    
    def _process_input_loop(self):
        """Main input processing loop"""
        while self.running:
            try:
                # Get input with timeout
                input_data = self.input_queue.get(timeout=0.1)
                
                # Measure processing latency
                process_start = time.time()
                received_time = input_data.get('timestamp', process_start)
                
                # Process the input
                self._execute_input(input_data)
                
                # Track performance
                process_time = time.time() - process_start
                total_latency = time.time() - received_time
                
                self._update_performance_stats(process_time, total_latency)
                self.input_count += 1
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Input processing error: {e}")
    
    def _execute_input(self, input_data: Dict[str, Any]):
        """Execute the input command with optimal performance"""
        action = input_data.get('action')
        data = input_data.get('data', {})
        
        try:
            if action == 'mouse_move':
                self._handle_mouse_move(data)
            elif action == 'mouse_click':
                self._handle_mouse_click(data)
            elif action == 'mouse_scroll':
                self._handle_mouse_scroll(data)
            elif action == 'key_press':
                self._handle_key_press(data)
            elif action == 'key_release':
                self._handle_key_release(data)
            elif action == 'key_type':
                self._handle_key_type(data)
            else:
                logging.warning(f"Unknown input action: {action}")
                
        except Exception as e:
            logging.error(f"Input execution error for {action}: {e}")
    
    def _handle_mouse_move(self, data: Dict[str, Any]):
        """Handle mouse movement with smoothing"""
        try:
            # Get coordinates
            if 'absolute' in data:
                x, y = data['absolute']['x'], data['absolute']['y']
                
                # Apply acceleration/sensitivity
                sensitivity = data.get('sensitivity', 1.0)
                if sensitivity != 1.0:
                    current_x, current_y = self.mouse_controller.position
                    x = current_x + (x - current_x) * sensitivity
                    y = current_y + (y - current_y) * sensitivity
                
                # Direct position setting (fastest)
                self.mouse_controller.position = (int(x), int(y))
                
            elif 'relative' in data:
                dx, dy = data['relative']['x'], data['relative']['y']
                sensitivity = data.get('sensitivity', 1.0)
                
                # Apply relative movement
                current_x, current_y = self.mouse_controller.position
                new_x = current_x + int(dx * sensitivity)
                new_y = current_y + int(dy * sensitivity)
                
                self.mouse_controller.position = (new_x, new_y)
            
            # Update cached position
            self.last_mouse_pos = self.mouse_controller.position
            
        except Exception as e:
            logging.error(f"Mouse move error: {e}")
    
    def _handle_mouse_click(self, data: Dict[str, Any]):
        """Handle mouse clicks"""
        try:
            button_map = {
                'left': mouse.Button.left,
                'right': mouse.Button.right,
                'middle': mouse.Button.middle
            }
            
            button = data.get('button', 'left')
            clicks = data.get('clicks', 1)
            pressed = data.get('pressed', True)
            
            mouse_button = button_map.get(button, mouse.Button.left)
            
            if pressed:
                for _ in range(clicks):
                    self.mouse_controller.click(mouse_button)
            else:
                # Handle button release if needed
                pass
                
        except Exception as e:
            logging.error(f"Mouse click error: {e}")
    
    def _handle_mouse_scroll(self, data: Dict[str, Any]):
        """Handle mouse scrolling"""
        try:
            dx = data.get('dx', 0)
            dy = data.get('dy', 0)
            
            if dx != 0 or dy != 0:
                self.mouse_controller.scroll(dx, dy)
                
        except Exception as e:
            logging.error(f"Mouse scroll error: {e}")
    
    def _handle_key_press(self, data: Dict[str, Any]):
        """Handle key press"""
        try:
            key = data.get('key')
            if not key:
                return
            
            # Handle special keys
            if key.startswith('Key.'):
                # Special key like Key.enter, Key.ctrl, etc.
                key_name = key[4:]  # Remove 'Key.' prefix
                special_key = getattr(keyboard.Key, key_name, None)
                if special_key:
                    self.keyboard_controller.press(special_key)
                else:
                    logging.warning(f"Unknown special key: {key}")
            else:
                # Regular character
                self.keyboard_controller.press(key)
                
        except Exception as e:
            logging.error(f"Key press error: {e}")
    
    def _handle_key_release(self, data: Dict[str, Any]):
        """Handle key release"""
        try:
            key = data.get('key')
            if not key:
                return
            
            # Handle special keys
            if key.startswith('Key.'):
                key_name = key[4:]
                special_key = getattr(keyboard.Key, key_name, None)
                if special_key:
                    self.keyboard_controller.release(special_key)
            else:
                self.keyboard_controller.release(key)
                
        except Exception as e:
            logging.error(f"Key release error: {e}")
    
    def _handle_key_type(self, data: Dict[str, Any]):
        """Handle text typing"""
        try:
            text = data.get('text', '')
            if text:
                # Use direct character typing for best performance
                for char in text:
                    self.keyboard_controller.press(char)
                    self.keyboard_controller.release(char)
                
        except Exception as e:
            logging.error(f"Key type error: {e}")
    
    def _update_performance_stats(self, process_time: float, total_latency: float):
        """Update performance statistics"""
        self.processing_times.append({
            'process_time': process_time,
            'total_latency': total_latency,
            'timestamp': time.time()
        })
        
        # Keep only recent samples
        if len(self.processing_times) > 1000:
            self.processing_times.pop(0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.processing_times:
            return {
                'input_count': self.input_count,
                'queue_size': self.input_queue.qsize(),
                'avg_process_time': 0,
                'avg_latency': 0,
                'max_latency': 0,
                'min_latency': 0
            }
        
        recent_times = self.processing_times[-100:]  # Last 100 samples
        process_times = [t['process_time'] for t in recent_times]
        latencies = [t['total_latency'] for t in recent_times]
        
        return {
            'input_count': self.input_count,
            'queue_size': self.input_queue.qsize(),
            'avg_process_time': sum(process_times) / len(process_times) * 1000,  # ms
            'avg_latency': sum(latencies) / len(latencies) * 1000,  # ms
            'max_latency': max(latencies) * 1000,  # ms
            'min_latency': min(latencies) * 1000,  # ms
            'samples': len(recent_times)
        }
    
    def set_mouse_acceleration(self, acceleration: float):
        """Set mouse acceleration factor"""
        self.mouse_acceleration = max(0.1, min(5.0, acceleration))
        logging.info(f"Mouse acceleration set to {self.mouse_acceleration}")
    
    def clear_queue(self):
        """Clear the input queue"""
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break
        logging.info("Input queue cleared")


class InputMessageEncoder:
    """Fast message encoding/decoding for input data"""
    
    def __init__(self):
        self.use_msgpack = HAS_MSGPACK
        logging.info(f"Input encoder using: {'MessagePack' if self.use_msgpack else 'JSON'}")
    
    def encode(self, data: Dict[str, Any]) -> bytes:
        """Encode input data to bytes"""
        try:
            if self.use_msgpack:
                return msgpack.packb(data)
            else:
                import json
                return json.dumps(data).encode('utf-8')
        except Exception as e:
            logging.error(f"Encoding error: {e}")
            return b''
    
    def decode(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Decode bytes to input data"""
        try:
            if self.use_msgpack:
                return msgpack.unpackb(data, raw=False)
            else:
                import json
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            logging.error(f"Decoding error: {e}")
            return None


class InputLatencyTester:
    """Test input latency and performance"""
    
    def __init__(self, input_handler: LowLatencyInputHandler):
        self.input_handler = input_handler
        self.test_results = []
    
    def test_mouse_latency(self, num_tests: int = 100) -> Dict[str, float]:
        """Test mouse movement latency"""
        results = []
        
        for i in range(num_tests):
            start_time = time.time()
            
            # Send mouse move command
            input_data = {
                'action': 'mouse_move',
                'data': {
                    'absolute': {'x': 100 + i, 'y': 100 + i},
                    'sensitivity': 1.0
                }
            }
            
            self.input_handler.handle_input(input_data)
            
            # Wait a bit to let it process
            time.sleep(0.001)
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # ms
            results.append(latency)
        
        return {
            'avg_latency': sum(results) / len(results),
            'max_latency': max(results),
            'min_latency': min(results),
            'test_count': num_tests
        }
    
    def test_keyboard_latency(self, num_tests: int = 100) -> Dict[str, float]:
        """Test keyboard input latency"""
        results = []
        
        for i in range(num_tests):
            start_time = time.time()
            
            # Send key press command
            input_data = {
                'action': 'key_press',
                'data': {'key': 'a'}
            }
            
            self.input_handler.handle_input(input_data)
            
            # Wait a bit
            time.sleep(0.001)
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # ms
            results.append(latency)
        
        return {
            'avg_latency': sum(results) / len(results),
            'max_latency': max(results),
            'min_latency': min(results),
            'test_count': num_tests
        }


if __name__ == "__main__":
    # Test the input system
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create input handler
    input_handler = LowLatencyInputHandler()
    input_handler.start()
    
    # Test basic functionality
    print("Testing low-latency input handler...")
    
    # Test mouse movement
    test_input = {
        'action': 'mouse_move',
        'data': {
            'absolute': {'x': 500, 'y': 500},
            'sensitivity': 1.0
        }
    }
    
    print("Testing mouse movement...")
    success = input_handler.handle_input(test_input)
    print(f"Mouse move queued: {success}")
    
    # Wait for processing
    time.sleep(0.1)
    
    # Get performance stats
    stats = input_handler.get_performance_stats()
    print(f"Performance stats: {stats}")
    
    # Test latency
    print("Running latency tests...")
    tester = InputLatencyTester(input_handler)
    
    mouse_results = tester.test_mouse_latency(50)
    print(f"Mouse latency: {mouse_results}")
    
    keyboard_results = tester.test_keyboard_latency(50)
    print(f"Keyboard latency: {keyboard_results}")
    
    # Cleanup
    input_handler.stop()
    print("Input handler test completed")