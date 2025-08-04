#!/bin/bash
echo "Starting Python Agent..."
echo
echo "Please replace YOUR_PC_IP with your actual PC IP address"
echo "Example: 192.168.1.100, 10.0.0.100, etc."
echo
read -p "Enter your PC's IP address: " PC_IP
export CONTROLLER_URL=http://$PC_IP:8080
echo
echo "Connecting to controller at: $CONTROLLER_URL"
echo
python3 python_agent.py