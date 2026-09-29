"""
Unrotting — Permission management for cross-platform support
"""
import sys
import os
import subprocess
from pathlib import Path


class PermissionManager:
    """Manages application permissions across platforms."""

    def __init__(self):
        self.platform = sys.platform
        self.is_admin = False

    def check_admin(self) -> bool:
        """Check if running with admin/sudo privileges."""
        if self.platform == 'win32':
            return self._check_windows_admin()
        elif self.platform == 'darwin':
            return self._check_macos_admin()
        else:
            return self._check_linux_admin()

    def _check_windows_admin(self) -> bool:
        """Check admin on Windows."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def _check_macos_admin(self) -> bool:
        """Check sudo on macOS."""
        try:
            import subprocess
            result = subprocess.run(['id', '-u'], capture_output=True, text=True)
            return result.stdout.strip() == '0'
        except Exception:
            return False

    def _check_linux_admin(self) -> bool:
        """Check sudo on Linux."""
        try:
            import subprocess
            result = subprocess.run(['id', '-u'], capture_output=True, text=True)
            return result.stdout.strip() == '0'
        except Exception:
            return False

    def request_admin(self) -> dict:
        """Request admin elevation."""
        if self.platform == 'win32':
            return self._request_windows_admin()
        elif self.platform == 'darwin':
            return self._request_macos_admin()
        else:
            return {"success": True, "message": "Running without elevated privileges"}

    def _request_windows_admin(self) -> dict:
        """Request admin on Windows via UAC."""
        import subprocess
        import sys
        try:
            # Try to relaunch with elevation
            script = Path(__file__).parent.parent / 'run.bat'
            if script.exists():
                subprocess.Popen([script], creationflags=subprocess.DETACHED_PROCESS)
                return {"success": True, "message": "Please accept the UAC prompt"}
            return {"success": False, "error": "Could not find launcher script"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _request_macos_admin(self) -> dict:
        """Request sudo on macOS."""
        import subprocess
        try:
            # Trigger sudo prompt
            result = subprocess.run(['sudo', '-n', 'echo'], capture_output=True, timeout=5)
            if result.returncode == 0:
                return {"success": True, "message": "Sudo access granted"}
            return {"success": False, "message": "Sudo access denied or timed out"}
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Sudo prompt timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_permission_status(self) -> dict:
        """Get current permission status."""
        return {
            "is_admin": self.check_admin(),
            "platform": self.platform,
            "features": self._get_available_features()
        }

    def _get_available_features(self) -> list:
        """Get list of available features based on permissions."""
        features = ["Task Management", "Statistics", "Password Protection"]

        if self.check_admin():
            features.extend([
                "Hosts File Blocking",
                "Process Enforcement",
                "Window Management",
                "Auto-Restart"
            ])
        else:
            features.extend([
                "Hosts File Blocking (Limited)",
                "Process Enforcement (No Kill)",
                "Window Management (Read-Only)"
            ])

        return features


# Global instance
permission_manager = PermissionManager()


def is_admin() -> bool:
    """Convenience function to check admin status."""
    return permission_manager.check_admin()


def get_permission_status() -> dict:
    """Get detailed permission status."""
    return permission_manager.get_permission_status()


def request_admin_access() -> dict:
    """Request admin/sudo access."""
    return permission_manager.request_admin()