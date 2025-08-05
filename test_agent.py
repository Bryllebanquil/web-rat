#!/usr/bin/env python3
"""
Simple test script to verify agent connectivity to cloud controller
"""
import requests
import json
import time
import uuid

# Configuration
SERVER_URL = "https://agent-controller.onrender.com"
TEST_AGENT_ID = f"test-{str(uuid.uuid4())[:8]}"

def test_basic_connectivity():
    """Test basic HTTP connectivity to the controller"""
    print(f"Testing connectivity to {SERVER_URL}...")
    
    try:
        # Test basic connection
        response = requests.get(f"{SERVER_URL}/", timeout=10)
        print(f"✓ Basic connection successful (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Basic connection failed: {e}")
        return False

def test_agent_endpoints():
    """Test agent-specific endpoints"""
    print(f"Testing agent endpoints with ID: {TEST_AGENT_ID}")
    
    try:
        # Test get_task endpoint
        response = requests.get(f"{SERVER_URL}/get_task/{TEST_AGENT_ID}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ get_task endpoint works (Command: {data.get('command', 'None')})")
        else:
            print(f"⚠️ get_task returned status {response.status_code}")
        
        # Test post_output endpoint
        test_output = {"output": "Test output from connectivity checker"}
        response = requests.post(
            f"{SERVER_URL}/post_output/{TEST_AGENT_ID}",
            json=test_output,
            timeout=10
        )
        if response.status_code == 200:
            print("✓ post_output endpoint works")
        else:
            print(f"⚠️ post_output returned status {response.status_code}")
        
        # Test agents list endpoint
        response = requests.get(f"{SERVER_URL}/agents", timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print(f"✓ agents endpoint works ({len(agents)} agents)")
            if TEST_AGENT_ID in agents:
                print(f"✓ Test agent {TEST_AGENT_ID} is visible in agents list")
        else:
            print(f"⚠️ agents endpoint returned status {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent endpoint test failed: {e}")
        return False

def test_command_execution():
    """Test command execution flow"""
    print("Testing command execution flow...")
    
    try:
        # Simulate agent polling for commands
        print("1. Polling for commands...")
        response = requests.get(f"{SERVER_URL}/get_task/{TEST_AGENT_ID}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            command = data.get("command", "")
            print(f"   Received command: {command}")
            
            # Simulate command execution and result posting
            if command and command != "sleep":
                print("2. Simulating command execution...")
                result_output = f"Simulated execution of: {command}\nTest output successful"
            else:
                print("2. No command to execute (sleep/empty)")
                result_output = "No command received - agent idle"
            
            print("3. Posting command result...")
            response = requests.post(
                f"{SERVER_URL}/post_output/{TEST_AGENT_ID}",
                json={"output": result_output},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Command execution flow test successful")
                return True
            else:
                print(f"⚠️ Failed to post result (Status: {response.status_code})")
                return False
        else:
            print(f"❌ Failed to get task (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Command execution test failed: {e}")
        return False

def main():
    """Run all connectivity tests"""
    print("🧪 Agent Connectivity Test")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("\n❌ Basic connectivity failed. Check your internet connection and server URL.")
        return
    
    print()
    
    # Test 2: Agent endpoints
    if not test_agent_endpoints():
        print("\n❌ Agent endpoint tests failed.")
        return
    
    print()
    
    # Test 3: Command execution flow
    if not test_command_execution():
        print("\n❌ Command execution flow test failed.")
        return
    
    print("\n🎉 All tests passed! Agent should be able to connect successfully.")
    print(f"\nTo test with real agent:")
    print(f"1. Update SERVER_URL in python_agent.py to: {SERVER_URL}")
    print(f"2. Run: python python_agent.py")
    print(f"3. Check the controller dashboard for your agent")

if __name__ == "__main__":
    main()