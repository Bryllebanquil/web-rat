#!/usr/bin/env python3
"""
Test script for Enhanced Agent Autostart Functionality
Demonstrates the new autostart and error handling capabilities
"""

import time
import subprocess
import sys
import os
import requests
import signal
import threading
from datetime import datetime

def test_server_startup():
    """Test that we can start the controller server"""
    print("🔧 Testing server startup...")
    
    try:
        # Start the controller in background
        controller_process = subprocess.Popen([
            sys.executable, 'controller.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test server status endpoint
        try:
            response = requests.get('http://localhost:8080/status', timeout=5)
            if response.status_code == 200:
                print("✅ Controller server started successfully")
                print(f"   Status: {response.json()}")
                return controller_process
            else:
                print(f"❌ Server returned status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to server: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start controller: {e}")
        return None

def test_agent_autostart():
    """Test the agent autostart functionality"""
    print("\n🚀 Testing agent autostart...")
    
    try:
        # Start the agent
        agent_process = subprocess.Popen([
            sys.executable, 'python_agent.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("   Agent process started, waiting for autostart connection...")
        time.sleep(10)  # Give time for autostart to work
        
        # Check if agent registered with server
        try:
            response = requests.get('http://localhost:8080/status', timeout=5)
            if response.status_code == 200:
                data = response.json()
                active_agents = data.get('active_agents', 0)
                if active_agents > 0:
                    print(f"✅ Agent autostart successful! {active_agents} agent(s) connected")
                    return agent_process
                else:
                    print("⚠️  Agent started but no connections detected")
                    return agent_process
            else:
                print(f"❌ Server status check failed: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to check server status: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start agent: {e}")
        return None

def test_error_recovery():
    """Test error recovery and reconnection"""
    print("\n🛡️ Testing error recovery...")
    
    # We'll simulate this by checking log output
    print("   Checking for error handling in agent logs...")
    
    if os.path.exists('agent.log'):
        with open('agent.log', 'r') as f:
            log_content = f.read()
            
        # Look for error handling indicators
        error_indicators = [
            'retry_on_failure',
            'safe_execute',
            'connection_manager',
            'health_monitor'
        ]
        
        found_indicators = [indicator for indicator in error_indicators if indicator in log_content]
        
        if found_indicators:
            print(f"✅ Error handling mechanisms detected: {', '.join(found_indicators)}")
        else:
            print("⚠️  No error handling indicators found in logs")
    else:
        print("⚠️  No agent.log file found")

def test_persistence():
    """Test persistence mechanisms"""
    print("\n⚡ Testing persistence mechanisms...")
    
    # Check for created autostart script
    if os.name == 'nt':  # Windows
        script_path = 'autostart.bat'
    else:  # Linux/Unix
        script_path = 'autostart.sh'
    
    if os.path.exists(script_path):
        print(f"✅ Autostart script created: {script_path}")
    else:
        print(f"⚠️  Autostart script not found: {script_path}")
    
    # Check log for persistence setup
    if os.path.exists('agent.log'):
        with open('agent.log', 'r') as f:
            log_content = f.read()
        
        persistence_indicators = [
            'persistence established',
            'Registry persistence',
            'Startup folder',
            'Systemd',
            'Crontab'
        ]
        
        found_persistence = [indicator for indicator in persistence_indicators if indicator in log_content]
        
        if found_persistence:
            print(f"✅ Persistence mechanisms found: {', '.join(found_persistence)}")
        else:
            print("⚠️  No persistence mechanisms detected in logs")

def cleanup_processes(controller_process, agent_process):
    """Clean up test processes"""
    print("\n🧹 Cleaning up test processes...")
    
    try:
        if agent_process and agent_process.poll() is None:
            agent_process.terminate()
            agent_process.wait(timeout=5)
            print("   Agent process terminated")
    except Exception as e:
        print(f"   Warning: Failed to terminate agent: {e}")
    
    try:
        if controller_process and controller_process.poll() is None:
            controller_process.terminate()
            controller_process.wait(timeout=5)
            print("   Controller process terminated")
    except Exception as e:
        print(f"   Warning: Failed to terminate controller: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("ENHANCED AGENT AUTOSTART TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    
    controller_process = None
    agent_process = None
    
    try:
        # Test 1: Start controller
        controller_process = test_server_startup()
        if not controller_process:
            print("\n❌ Cannot continue tests without controller")
            return False
        
        # Test 2: Test agent autostart
        agent_process = test_agent_autostart()
        if not agent_process:
            print("\n❌ Agent autostart test failed")
            return False
        
        # Test 3: Test error recovery
        test_error_recovery()
        
        # Test 4: Test persistence
        test_persistence()
        
        print("\n" + "=" * 60)
        print("✅ AUTOSTART TEST SUITE COMPLETED")
        print("=" * 60)
        
        # Let it run for a bit to see the connection in action
        print("\nLetting agent run for 30 seconds to observe behavior...")
        time.sleep(30)
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        return False
    finally:
        cleanup_processes(controller_process, agent_process)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)