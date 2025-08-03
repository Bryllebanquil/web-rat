import ctypes
import subprocess
import sys
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def disable_uac():
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 0)
        print("[OK] UAC has been disabled.")
    except PermissionError:
        print("[!] Access denied. Run this script as administrator.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == '__main__':
    if not is_admin():
        print("[!] Relaunching as Administrator...")
        # Relaunch with elevated privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{__file__}"', None, 1
        )
        sys.exit()

    disable_uac()
