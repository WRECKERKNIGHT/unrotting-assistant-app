"""
Unrotting — Native Windows Dialogs
"""
import sys
import os
from pathlib import Path


def show_admin_dialog() -> bool:
    """Show native Windows dialog asking for admin elevation."""
    if sys.platform != 'win32':
        return False

    try:
        import ctypes
        from ctypes import wintypes

        # Use Windows API for native dialog
        # MB_YESNO = 4, MB_ICONQUESTION = 32, MB_DEFBUTTON2 = 256
        result = ctypes.windll.user32MessageBoxW(
            0,
            "Unrotting needs administrator privileges to:\n\n"
            "• Block short-form content at system level (hosts file)\n"
            "• Close distracting browser tabs automatically\n"
            "• Kill specified apps during focus sessions\n\n"
            "Would you like to restart Unrotting with administrator privileges?",
            "Unrotting — Administrator Required",
            0x4 | 0x30 | 0x100  # MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2
        )
        return result == 6  # IDYES = 6
    except Exception:
        return False


def show_hosts_permission_dialog() -> bool:
    """Show dialog explaining hosts file access."""
    if sys.platform != 'win32':
        return False

    try:
        import ctypes
        result = ctypes.windll.user32MessageBoxW(
            0,
            "Unrotting needs to modify your hosts file to block:\n\n"
            "• YouTube Shorts\n"
            "• Instagram Reels\n"
            "• TikTok\n\n"
            "This redirects blocked domains to localhost.\n"
            "Your original hosts file is backed up automatically.\n\n"
            "Do you want to enable hosts file blocking?",
            "Unrotting — Hosts File Access",
            0x4 | 0x33  # MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON1
        )
        return result == 6
    except Exception:
        return False


def show_feature_limitation_dialog() -> bool:
    """Show dialog explaining limited features without admin."""
    if sys.platform != 'win32':
        return False

    try:
        import ctypes
        result = ctypes.windll.user32MessageBoxW(
            0,
            "Without administrator privileges, some features are limited:\n\n"
            "✓ Task Management — Available\n"
            "✓ Statistics — Available\n"
            "✓ Password Protection — Available\n"
            "✗ Hosts File Blocking — Limited (manual setup required)\n"
            "✗ Process Enforcement — Not available\n"
            "✗ Window Management — Read-only\n\n"
            "Would you like to restart with administrator privileges for full access?",
            "Unrotting — Limited Features",
            0x4 | 0x30 | 0x100  # MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2
        )
        return result == 6
    except Exception:
        return False


def show_notification_permission_dialog() -> bool:
    """Ask for notification permissions."""
    if sys.platform != 'win32':
        return False

    try:
        import ctypes
        result = ctypes.windll.user32MessageBoxW(
            0,
            "Unrotting would like to send you notifications for:\n\n"
            "• Focus session start/end\n"
            "• Break reminders\n"
            "• Task completion alerts\n\n"
            "Enable desktop notifications?",
            "Unrotting — Notifications",
            0x4 | 0x33  # MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON1
        )
        return result == 6
    except Exception:
        return False


def show_info_dialog(title: str, message: str) -> None:
    """Show information dialog."""
    if sys.platform != 'win32':
        print(f"{title}: {message}")
        return

    try:
        import ctypes
        ctypes.windll.user32MessageBoxW(0, message, title, 0x40)  # MB_OK | MB_ICONINFORMATION
    except Exception:
        print(f"{title}: {message}")


def show_error_dialog(title: str, message: str) -> None:
    """Show error dialog."""
    if sys.platform != 'win32':
        print(f"ERROR - {title}: {message}")
        return

    try:
        import ctypes
        ctypes.windll.user32MessageBoxW(0, message, title, 0x10)  # MB_OK | MB_ICONERROR
    except Exception:
        print(f"ERROR - {title}: {message}")


def show_confirm_dialog(title: str, message: str) -> bool:
    """Show confirmation dialog."""
    if sys.platform != 'win32':
        return False

    try:
        import ctypes
        result = ctypes.windll.user32MessageBoxW(0, message, title, 0x4 | 0x33)
        return result == 6
    except Exception:
        return False