# Enhanced Dashboard Controller 🚀

A powerful remote access and control system with advanced features including reverse shell, high-FPS streaming, and voice control capabilities.

## 🆕 New Features

### 1. Reverse Shell Functionality
- **Persistent shell connection** between agent and controller
- **Direct command execution** with real-time responses
- **Cross-platform support** (Windows PowerShell, Linux Bash)
- **Dedicated terminal interface** in the dashboard
- **Connection status monitoring**

### 2. High-FPS Streaming (30 FPS)
- **3x faster streaming** - upgraded from 10 FPS to 30 FPS
- **Optimized compression** for better performance
- **Reduced latency** with shorter timeouts
- **Smart resolution scaling** for large screens
- **Enhanced camera properties** for better quality

### 3. Voice Control System
- **Speech recognition** using Google Speech Recognition
- **Natural language commands** - speak to control the agent
- **Pre-defined command set** for common operations
- **Real-time voice processing** with ambient noise adjustment
- **Voice command feedback** and status indicators

### 4. Enhanced Dashboard UI
- **Modern neural-themed interface** with glassmorphism effects
- **Reverse shell terminal** with dedicated output panel
- **Voice control panel** with command reference
- **Keyboard shortcuts** for quick access
- **Real-time status indicators** for all features

## 🎯 Voice Commands

Speak these commands when voice control is active:

| Voice Command | Action |
|---------------|--------|
| "screenshot" | Take a screenshot |
| "start camera" | Start camera stream |
| "stop camera" | Stop camera stream |
| "start streaming" | Start screen stream |
| "stop streaming" | Stop screen stream |
| "system info" | Get system information |
| "list processes" | Show running processes |
| "current directory" | Show current directory |
| "run [command]" | Execute any command |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install system dependencies (Linux/Ubuntu)
sudo apt update
sudo apt install -y python3-dev portaudio19-dev

# Install Python packages
pip install -r requirements.txt
```

### 2. Start the Controller

```bash
source venv/bin/activate
python controller.py
```

The controller will start:
- **Web server** on port 8080
- **Reverse shell server** on port 9999

### 3. Start the Agent

```bash
source venv/bin/activate
python python_agent.py
```

### 4. Access the Dashboard

Open your browser and go to: **http://localhost:8080/dashboard**

## 🎮 Using the Features

### Reverse Shell
1. Click **"Start Reverse Shell"** in the dashboard
2. Wait for connection confirmation
3. Enter shell commands in the **"Shell Command"** input
4. Click **"Execute Shell Command"** or press Enter
5. View results in the **"Reverse Shell Terminal"** panel

### High-FPS Streaming
1. Click **"Screen Stream"** for 30 FPS screen capture
2. Click **"Camera Stream"** for 30 FPS webcam feed
3. Streams open in new windows with smooth playback
4. Use **"Stop All Streams"** to terminate all streams

### Voice Control
1. Click **"Start Voice Control"** 
2. Speak commands clearly near your microphone
3. Watch for voice command feedback in the dashboard
4. Commands are executed automatically when recognized

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` (in command input) | Execute command |
| `Enter` (in shell input) | Execute shell command |
| `Ctrl+Shift+S` | Start reverse shell |
| `Ctrl+Shift+V` | Start voice control |

## 🔧 Technical Specifications

### Streaming Performance
- **Frame Rate**: 30 FPS (upgraded from 10 FPS)
- **Compression**: JPEG with 85% quality + optimization
- **Resolution**: Auto-scaling for screens > 1920px width
- **Latency**: ~33ms per frame (reduced from 100ms)

### Reverse Shell
- **Protocol**: TCP socket connection on port 9999
- **Security**: Local network only (bind to 0.0.0.0)
- **Timeout**: 30 seconds per command
- **Features**: Directory navigation, command history

### Voice Recognition
- **Engine**: Google Speech Recognition API
- **Microphone**: Default system microphone
- **Language**: English (US)
- **Processing**: Real-time with 5-second phrase limit

## 📁 Project Structure

```
workspace/
├── controller.py          # Enhanced web server with reverse shell
├── python_agent.py        # Agent with voice control & high-FPS streaming
├── requirements.txt       # Updated dependencies
├── test_features.py       # Feature demonstration script
└── README.md             # This documentation
```

## 🔒 Security Notes

- **Local Network Only**: Designed for local network use
- **No Authentication**: Add authentication for production use
- **Firewall Considerations**: Opens ports 8080 and 9999
- **Voice Privacy**: Voice commands processed via Google API

## 🐛 Troubleshooting

### Voice Control Issues
```bash
# Install additional audio dependencies
sudo apt install -y pulseaudio pulseaudio-utils

# Test microphone
arecord -l
```

### Camera Stream Issues
```bash
# Check camera permissions
ls /dev/video*

# Test camera access
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### Reverse Shell Connection Issues
```bash
# Check if ports are available
sudo netstat -tlnp | grep -E "(8080|9999)"

# Check firewall status
sudo ufw status
```

## 🎯 Testing the Features

Run the included test script:

```bash
source venv/bin/activate
python test_features.py
```

This will demonstrate:
- ✅ High-FPS streaming activation
- ✅ Reverse shell connection and command execution
- ✅ Voice control system activation
- ✅ Feature status and endpoints

## 🌟 Advanced Usage

### Custom Voice Commands
Modify the `voice_control_handler` function in `python_agent.py` to add custom voice commands:

```python
elif "custom command" in command:
    execute_voice_command("your-custom-action", agent_id)
```

### Streaming Optimization
Adjust FPS and quality in `python_agent.py`:

```python
target_fps = 60  # Increase for higher FPS
cv2.IMWRITE_JPEG_QUALITY, 95  # Increase for better quality
```

### Shell Command Extensions
Add custom shell commands in the reverse shell handler:

```python
elif command.startswith("custom:"):
    # Handle custom commands
    response = handle_custom_command(command[7:])
```

## 📊 Performance Metrics

| Feature | Before | After | Improvement |
|---------|--------|-------|-------------|
| Screen FPS | 10 FPS | 30 FPS | **3x faster** |
| Camera FPS | 10 FPS | 30 FPS | **3x faster** |
| Stream Latency | 100ms | 33ms | **67% reduction** |
| Command Execution | HTTP only | HTTP + Socket | **2 methods** |
| Control Methods | Manual only | Manual + Voice | **Voice added** |

## 🚀 Future Enhancements

- [ ] Multi-agent reverse shell management
- [ ] Voice command training and customization
- [ ] Video recording and playback
- [ ] Mobile dashboard interface
- [ ] Encrypted communications
- [ ] Authentication and authorization
- [ ] Performance monitoring dashboard

---

**🎉 Enjoy your enhanced dashboard controller with reverse shell, high-FPS streaming, and voice control capabilities!**