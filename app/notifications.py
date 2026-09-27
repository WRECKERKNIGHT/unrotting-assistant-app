"""
Unrotting — Cross-platform notification system
"""
import sys
import subprocess
from pathlib import Path


class NotificationManager:
    """Cross-platform desktop notifications."""

    def __init__(self):
        self.platform = sys.platform
        self.icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"

    def notify(self, title: str, message: str, duration: int = 5) -> bool:
        """Send a desktop notification."""
        try:
            if self.platform == 'win32':
                return self._notify_windows(title, message, duration)
            elif self.platform == 'darwin':
                return self._notify_macos(title, message, duration)
            else:
                return self._notify_linux(title, message, duration)
        except Exception as e:
            print(f"Notification failed: {e}")
            return False

    def _notify_windows(self, title: str, message: str, duration: int) -> bool:
        """Windows toast notification."""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title=title,
                msg=message,
                icon_path=str(self.icon_path) if self.icon_path.exists() else None,
                duration=duration,
                threaded=True
            )
            return True
        except ImportError:
            # Fallback to Windows 10+ native
            try:
                subprocess.run([
                    'powershell', '-Command',
                    f'Add-Type -AssemblyName System.Windows.Forms; '
                    f'$notify = New-Object System.Windows.Forms.NotifyIcon; '
                    f'$notify.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon("python.exe"); '
                    f'$notify.Visible = $true; '
                    f'$notify.ShowBalloonTip({duration * 1000}, "{title}", "{message}", "Info")'
                ], capture_output=True)
                return True
            except Exception:
                return False

    def _notify_macos(self, title: str, message: str, duration: int) -> bool:
        """macOS notification via osascript."""
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ], capture_output=True, timeout=5)
            return True
        except Exception:
            return False

    def _notify_linux(self, title: str, message: str, duration: int) -> bool:
        """Linux notification via notify-send."""
        try:
            subprocess.run([
                'notify-send', '-t', str(duration * 1000),
                title, message
            ], capture_output=True, timeout=5)
            return True
        except Exception:
            return False


# Global instance
notification_manager = NotificationManager()


def notify(title: str, message: str, duration: int = 5) -> bool:
    """Convenience function for notifications."""
    return notification_manager.notify(title, message, duration)
