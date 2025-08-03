#!/usr/bin/env python3
"""
Test script for enhanced process termination with admin privileges.
This script demonstrates the new functionality added to python_agent.py.
"""

import sys
import os

# Add the current directory to Python path to import from python_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from python_agent import (
        terminate_process_with_admin,
        kill_task_manager,
        is_admin,
        elevate_privileges,
        WINDOWS_AVAILABLE
    )
except ImportError as e:
    print(f"Error importing from python_agent: {e}")
    print("Make sure python_agent.py is in the same directory")
    sys.exit(1)

def main():
    """Main test function."""
    print("Enhanced Process Termination Test")
    print("=" * 40)
    
    # Check current privileges
    if WINDOWS_AVAILABLE:
        if is_admin():
            print("✓ Running with administrator privileges")
        else:
            print("⚠ Running with user privileges")
            print("Attempting to elevate privileges...")
            if elevate_privileges():
                print("✓ Privilege escalation successful")
            else:
                print("✗ Privilege escalation failed")
                print("Some termination methods may fail")
    else:
        print("✓ Running on Linux/Unix system")
        if os.geteuid() == 0:
            print("✓ Running as root")
        else:
            print("⚠ Running as regular user")
    
    print("\nAvailable commands:")
    print("1. kill-taskmgr - Terminate Task Manager")
    print("2. terminate <process_name> - Terminate process by name")
    print("3. terminate <pid> - Terminate process by PID")
    print("4. quit - Exit")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == "quit" or command == "exit":
                break
            elif command == "kill-taskmgr":
                print("Attempting to terminate Task Manager...")
                result = kill_task_manager()
                print(f"Result: {result}")
            elif command.startswith("terminate "):
                target = command.split(" ", 1)[1]
                
                # Try to convert to PID if it's a number
                try:
                    target = int(target)
                    print(f"Attempting to terminate process with PID {target}...")
                except ValueError:
                    print(f"Attempting to terminate process '{target}'...")
                
                result = terminate_process_with_admin(target, force=True)
                print(f"Result: {result}")
            else:
                print("Unknown command. Use 'kill-taskmgr', 'terminate <name/pid>', or 'quit'")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()