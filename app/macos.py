"""
Unrotting — macOS-specific functionality
"""
import sys
import subprocess
from pathlib import Path

# macOS-specific constants
HOSTS_FILE = Path('/etc/hosts')
BACKUP_HOSTS = None  # Set dynamically based on config

def is_admin() -> bool:
    """Check if running as sudo/admin on macOS."""
    try:
        result = subprocess.run(['id', '-u'], capture_output=True, text=True)
        return result.stdout.strip() == '0'
    except Exception:
        return False


def ensure_hosts_backup(config_dir: Path) -> None:
    """Back up the current hosts file."""
    global BACKUP_HOSTS
    BACKUP_HOSTS = config_dir / 'hosts.backup'

    if HOSTS_FILE.exists() and not BACKUP_HOSTS.exists():
        try:
            content = HOSTS_FILE.read_text()
            BACKUP_HOSTS.write_text(content)
            print("Hosts file backed up")
        except PermissionError:
            print("Need sudo to back up hosts file")


def update_hosts_file(cfg: dict, force_unblock: bool = False) -> None:
    """Update the macOS hosts file."""
    try:
        if not HOSTS_FILE.exists():
            print("Hosts file not found")
            return

        try:
            current = HOSTS_FILE.read_text()
        except PermissionError:
            print("Need sudo rights to modify hosts file")
            return

        # Remove our entries
        lines = []
        skip = False
        for line in current.splitlines():
            if "# UNROTTING_BLOCK" in line:
                skip = True
                continue
            if skip and line.strip() and not line.startswith("#"):
                continue
            skip = False
            lines.append(line)

        if not force_unblock and (cfg.get("block_tiktok") or cfg.get("block_instagram") or cfg.get("block_youtube_shorts")):
            entries = [
                "# UNROTTING_BLOCK - Start",
                "127.0.0.1   www.tiktok.com",
                "127.0.0.1   tiktok.com",
                "127.0.0.1   m.tiktok.com",
                "127.0.0.1   www.instagram.com",
                "127.0.0.1   instagram.com",
                "127.0.0.1   www.youtube.com",
                "127.0.0.1   youtube.com",
                "127.0.0.1   m.youtube.com",
                "127.0.0.1   www.facebook.com",
                "127.0.0.1   facebook.com",
                "# UNROTTING_BLOCK - End",
            ]
            if not cfg.get("block_tiktok"):
                entries = [e for e in entries if "tiktok" not in e.lower()]
            if not cfg.get("block_reels") and not cfg.get("block_instagram"):
                entries = [e for e in entries if "instagram" not in e.lower()]
            if not cfg.get("block_youtube_shorts"):
                entries = [e for e in entries if "youtube" not in e.lower()]
            lines.extend(entries)

        new_content = "\n".join(lines) + "\n"
        HOSTS_FILE.write_text(new_content)
        print("Hosts file updated")

    except Exception as e:
        print(f"Error updating hosts: {e}")


def request_sudo() -> bool:
    """Request sudo password for hosts file modification."""
    try:
        result = subprocess.run(
            ['sudo', '-n', 'echo'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def open_system_preferences() -> None:
    """Open macOS System Preferences for permissions."""
    subprocess.Popen(['open', 'x-apple.systempreferences:com.apple.preference.security'])


def get_macos_version() -> str:
    """Get macOS version info."""
    try:
        result = subprocess.run(['sw_vers'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception:
        return "Unknown"
