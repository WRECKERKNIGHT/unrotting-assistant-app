"""
Unrotting Auto-Start - Manage Windows startup entry
"""
import sys
import winreg
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

AUTO_RUN_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
]

APP_NAME = "Unrotting"


def get_exe_path():
    return sys.executable


def is_auto_start_enabled():
    try:
        for key_path in AUTO_RUN_KEYS:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
                )
                try:
                    winreg.QueryValueEx(key, APP_NAME)
                    winreg.CloseKey(key)
                    return True
                except FileNotFoundError:
                    winreg.CloseKey(key)
                    continue
            except FileNotFoundError:
                continue
        return False
    except Exception as e:
        print(f"Error checking auto-start: {e}")
        return False


def enable_auto_start():
    try:
        exe_path = get_exe_path()

        # Start the full app, not just tray
        startup_cmd = f'"{exe_path}" -m unrotting.app.main run'

        for key_path in AUTO_RUN_KEYS:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
                )
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_cmd)
                winreg.CloseKey(key)
                print(f"Auto-start enabled in: {key_path}")
                return True
            except Exception as e:
                print(f"Failed to set auto-start in {key_path}: {e}")
                continue

        return False
    except Exception as e:
        print(f"Error enabling auto-start: {e}")
        return False


def disable_auto_start():
    try:
        for key_path in AUTO_RUN_KEYS:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
                )
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    print(f"Auto-start disabled from: {key_path}")
                except FileNotFoundError:
                    pass
                winreg.CloseKey(key)
            except FileNotFoundError:
                continue
        return True
    except Exception as e:
        print(f"Error disabling auto-start: {e}")
        return False


def create_shortcut():
    try:
        import pythoncom
        from win32com.client import Dispatch

        desktop = Path.home() / "Desktop" / "Unrotting.lnk"

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(desktop))
        shortcut.TargetPath = get_exe_path()
        shortcut.Arguments = '-m unrotting.app.main run'
        shortcut.WorkingDirectory = str(Path(__file__).parent.parent)
        shortcut.IconLocation = str(Path(__file__).parent.parent / "assets" / "icon.ico")
        shortcut.Description = "Unrotting - Focus Hard"
        shortcut.Save()

        print(f"Shortcut created: {desktop}")
        return True
    except ImportError:
        print("pywin32 not available for shortcut creation")
        return False
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False


def remove_shortcut():
    desktop = Path.home() / "Desktop" / "Unrotting.lnk"
    if desktop.exists():
        desktop.unlink()
        print(f"Shortcut removed: {desktop}")
        return True
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage Unrotting auto-start")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show auto-start status")
    sub.add_parser("enable", help="Enable auto-start on boot")
    sub.add_parser("disable", help="Disable auto-start on boot")
    sub.add_parser("shortcut", help="Create desktop shortcut")
    sub.add_parser("removeshortcut", help="Remove desktop shortcut")

    args = parser.parse_args()

    if args.command == "status":
        status = "Enabled" if is_auto_start_enabled() else "Disabled"
        print(f"Auto-start: {status}")

    elif args.command == "enable":
        if enable_auto_start():
            print("Auto-start enabled successfully")
        else:
            print("Failed to enable auto-start")

    elif args.command == "disable":
        if disable_auto_start():
            print("Auto-start disabled successfully")
        else:
            print("Failed to disable auto-start")

    elif args.command == "shortcut":
        if create_shortcut():
            print("Shortcut created successfully")
        else:
            print("Failed to create shortcut")

    elif args.command == "removeshortcut":
        if remove_shortcut():
            print("Shortcut removed successfully")
        else:
            print("Shortcut not found or removal failed")
