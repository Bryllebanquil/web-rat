# 🚀 Deployment Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Render account (for cloud deployment)
- Local machine with Python environment

## 🌐 Render Deployment (Controller)

### 1. Prepare Repository
```bash
# Clone or prepare your repository
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Render Setup
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `agent-controller`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python controller.py`
   - **Port**: `8080`

### 3. Environment Variables (Optional)
Add these in Render dashboard under "Environment":
```
DEBUG=False
LOG_LEVEL=INFO
MAX_AGENTS=100
RATE_LIMIT_PER_MINUTE=60
```

### 4. Deploy
- Click "Create Web Service"
- Wait for build to complete
- Your controller will be available at: `https://your-app-name.onrender.com`

## 💻 Local Agent Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Agent
Set the server URL in `python_agent.py` or use environment variable:
```bash
export SERVER_URL="https://your-controller-url.onrender.com"
```

### 3. Run Agent
```bash
python python_agent.py
```

### 4. Test Connectivity
```bash
python python_agent.py --test
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: Missing dependencies
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. Permission Errors (Linux)
**Problem**: Audio/video capture requires permissions
**Solution**:
```bash
# Install system dependencies
sudo apt-get install python3-dev portaudio19-dev
sudo apt-get install libasound2-dev
```

#### 3. Windows-Specific Issues
**Problem**: Windows-only dependencies
**Solution**: The code automatically handles platform differences

#### 4. Network Connectivity
**Problem**: Agent can't connect to controller
**Solution**:
1. Verify controller URL is correct
2. Check firewall settings
3. Test with: `python python_agent.py --test`

### Debug Mode
Enable debug mode for detailed logging:
```bash
export DEBUG=True
python controller.py
```

## 📊 Monitoring

### Controller Health Check
Visit: `https://your-controller-url.onrender.com/dashboard`

### Agent Status
- Check controller dashboard for agent connections
- Monitor logs for errors
- Use connectivity test: `python python_agent.py --test`

## 🔒 Security Considerations

1. **Change Default URLs**: Update hardcoded URLs in code
2. **Use Environment Variables**: For sensitive configuration
3. **Enable Authentication**: Set `REQUIRE_AUTH=True` and provide `API_KEY`
4. **Rate Limiting**: Configure appropriate limits
5. **HTTPS Only**: Ensure all communications use HTTPS

## 🚨 Emergency Procedures

### Stop All Agents
```bash
# Send stop command to all agents
curl -X POST https://your-controller-url.onrender.com/issue_command \
  -H "Content-Type: application/json" \
  -d '{"command": "exit", "agent_id": "all"}'
```

### Restart Controller
- Go to Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"

## 📞 Support

If you encounter issues:
1. Check the logs in Render dashboard
2. Run connectivity tests
3. Verify all dependencies are installed
4. Check network connectivity