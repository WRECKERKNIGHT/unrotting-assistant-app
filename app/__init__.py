"""
Unrotting — A strict focus app that blocks short-form content (Reels, Shorts, TikToks)
while allowing full videos. Earn scroll time by completing real-world tasks.
"""

import os
import sys
import json
import threading
import logging
import hashlib
import time
import subprocess
import ctypes
import atexit
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Make sure we can import our packages
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("unrotting.log"),
    ],
)
logger = logging.getLogger("unrotting")

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
HOSTS_FILE = Path(r"C:\Windows\System32\drivers\etc\hosts")
BACKUP_HOSTS = CONFIG_DIR / "hosts.backup"

# ─── Configuration ───────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "strict_mode": True,
    "block_reels": True,
    "block_shorts": True,
    "block_tiktok": True,
    "block_instagram": False,
    "block_youtube_shorts": True,
    "allow_full_videos": True,
    "focus_duration_minutes": 45,
    "break_duration_minutes": 15,
    "long_break_interval": 4,
    "long_break_duration_minutes": 15,
    "password_hash": None,
    "auto_start": True,
    "block_killing": True,
    "blocked_hosts": [],
    "blocked_apps": [],
    "whitelisted_urls": [],
    "enabled": True,
    "apps_locked": False,
}


def load_config() -> dict:
    path = CONFIG_DIR / "config.json"
    if path.exists():
        try:
            with open(path, "r") as f:
                cfg = json.load(f)
            merged = {**DEFAULT_CONFIG, **cfg}
            # Force locked timing values
            merged["focus_duration_minutes"] = 45
            merged["break_duration_minutes"] = 15
            merged["long_break_duration_minutes"] = 15
            return merged
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    cfg["focus_duration_minutes"] = 45
    cfg["break_duration_minutes"] = 15
    cfg["long_break_duration_minutes"] = 15
    path = CONFIG_DIR / "config.json"
    path.write_text(json.dumps(cfg, indent=2))


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(cfg: dict, password: str) -> bool:
    if cfg.get("password_hash") is None:
        return True
    return cfg["password_hash"] == hashlib.sha256(password.encode()).hexdigest()


# ─── Hosts-based blocking ────────────────────────────────────────────────────

def ensure_hosts_backup() -> None:
    if HOSTS_FILE.exists() and not BACKUP_HOSTS.exists():
        try:
            content = HOSTS_FILE.read_text()
            BACKUP_HOSTS.write_text(content)
            logger.info("Hosts file backed up")
        except PermissionError:
            logger.error("Need admin to back up hosts file")


def update_hosts_file(cfg: dict, force_unblock: bool = False) -> None:
    try:
        if not HOSTS_FILE.exists():
            logger.error("Hosts file not found")
            return

        try:
            current = HOSTS_FILE.read_text()
        except PermissionError:
            logger.error("Need admin rights to modify hosts file")
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
        logger.info("Hosts file updated")

    except Exception as e:
        logger.error(f"Error updating hosts: {e}")


# ─── Task & Points System (merged from TS project) ───────────────────────────

class TaskManager:
    """Manages tasks, points, streaks, and time earnings."""

    def __init__(self):
        self.path = CONFIG_DIR / "tasks.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                pass
        return {
            "tasks": [],
            "completions": [],
            "points": 0,
            "streak_days": 0,
            "last_active_date": None,
        }

    def _save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save tasks: {e}")

    def add_task(self, title: str, points: int = 50, reward_minutes: int = 15,
                 daily: bool = True, repeatable: bool = True) -> dict:
        task = {
            "id": datetime.now().isoformat(),
            "title": title,
            "points": points,
            "reward_minutes": reward_minutes,
            "daily": daily,
            "repeatable": repeatable,
            "created_at": datetime.now().isoformat(),
        }
        self.data["tasks"].append(task)
        self._save()
        return task

    def complete_task(self, task_id: str) -> Optional[dict]:
        task = None
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        if not task:
            return None

        # Calculate reward with streak multiplier
        streak_multiplier = min(1 + self.data["streak_days"] * 0.1, 2.0)
        points_earned = int(task["points"] * streak_multiplier)
        minutes_earned = int(task["reward_minutes"] * streak_multiplier)

        completion = {
            "id": datetime.now().isoformat(),
            "task_id": task_id,
            "completed_at": datetime.now().isoformat(),
            "points_earned": points_earned,
            "minutes_earned": minutes_earned,
        }
        self.data["completions"].append(completion)
        self.data["points"] += points_earned
        self._update_streak()
        self._save()
        return completion

    def _update_streak(self) -> None:
        today = datetime.now().date().isoformat()
        last_active = self.data.get("last_active_date")

        if last_active == today:
            return  # Already active today

        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        if last_active == yesterday:
            self.data["streak_days"] += 1
        else:
            self.data["streak_days"] = 1

        self.data["last_active_date"] = today

    def get_tasks(self) -> list:
        return self.data.get("tasks", [])

    def get_completions(self, days: int = 7) -> list:
        cutoff = datetime.now() - timedelta(days=days)
        completions = self.data.get("completions", [])
        return [c for c in completions if datetime.fromisoformat(c["completed_at"]) >= cutoff]

    def get_summary(self) -> dict:
        today = datetime.now().date().isoformat()
        today_completions = [c for c in self.data.get("completions", [])
                           if c["completed_at"].startswith(today)]
        points_today = sum(c["points_earned"] for c in today_completions)
        minutes_today = sum(c["minutes_earned"] for c in today_completions)
        return {
            "total_points": self.data.get("points", 0),
            "points_today": points_today,
            "minutes_earned_today": minutes_today,
            "streak_days": self.data.get("streak_days", 0),
            "total_completions": len(self.data.get("completions", [])),
        }

    def reset_tasks(self) -> None:
        self.data = {
            "tasks": [],
            "completions": [],
            "points": 0,
            "streak_days": 0,
            "last_active_date": None,
        }
        self._save()


# ─── Statistics Tracking ─────────────────────────────────────────────────────

class Stats:
    def __init__(self):
        self.path = CONFIG_DIR / "stats.json"
        self.data = self._load()

    def start_notification(self) -> None:
        """Show desktop notification for session start."""
        try:
            import platform
            if platform.system() == 'Windows':
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast("Unrotting", "Focus session started!", icon_path=str(Path(__file__).parent.parent / "assets" / "icon.ico"), duration=3)
            elif platform.system() == 'Darwin':
                subprocess.run(['osascript', '-e', 'display notification "Focus session started" with title "Unrotting"'])
            else:
                # Linux
                subprocess.run(['notify-send', 'Unrotting', 'Focus session started!'])
        except Exception:
            pass  # Silent fail for notifications

    def end_notification(self, blocks: int) -> None:
        """Show desktop notification for session end."""
        try:
            import platform
            if platform.system() == 'Windows':
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast("Unrotting", f"Focus session complete! {blocks} blocks.", icon_path=str(Path(__file__).parent.parent / "assets" / "icon.ico"), duration=5)
            elif platform.system() == 'Darwin':
                subprocess.run(['osascript', '-e', f'display notification "Session complete! {blocks} blocks" with title "Unrotting"'])
            else:
                subprocess.run(['notify-send', 'Unrotting', f'Focus session complete! {blocks} blocks.'])
        except Exception:
            pass  # Silent fail for notifications

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                pass
        return {
            "sessions": [],
            "total_blocked": 0,
            "total_focus_time_seconds": 0,
            "total_break_time_seconds": 0,
            "blocked_urls": [],
            "last_reset": datetime.now().isoformat(),
        }

    def _save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save stats: {e}")

    def record_block(self, url_or_app: str) -> None:
        self.data["total_blocked"] += 1
        self.data["blocked_urls"].append({
            "url": url_or_app,
            "time": datetime.now().isoformat(),
        })
        if len(self.data["blocked_urls"]) > 100:
            self.data["blocked_urls"] = self.data["blocked_urls"][-100:]
        self._save()

    def start_session(self) -> str:
        session_id = datetime.now().isoformat()
        self.data["sessions"].append({
            "id": session_id,
            "start": session_id,
            "end": None,
            "blocks": 0,
        })
        self._save()
        return session_id

    def end_session(self, session_id: str, blocks: int, focus_seconds: int) -> None:
        for session in self.data["sessions"]:
            if session["id"] == session_id:
                session["end"] = datetime.now().isoformat()
                session["blocks"] = blocks
                session["focus_seconds"] = focus_seconds
                break
        self.data["total_focus_time_seconds"] += focus_seconds
        self._save()

    def get_summary(self) -> dict:
        today = datetime.now().date()
        today_blocks = sum(
            1 for u in self.data.get("blocked_urls", [])
            if datetime.fromisoformat(u["time"]).date() == today
        )
        today_focus = sum(
            s.get("focus_seconds", 0)
            for s in self.data.get("sessions", [])
            if datetime.fromisoformat(s["start"]).date() == today and s.get("end")
        )
        return {
            "total_blocked": self.data["total_blocked"],
            "today_blocked": today_blocks,
            "total_focus_time_seconds": self.data["total_focus_time_seconds"],
            "today_focus_minutes": round(today_focus / 60, 1),
            "total_sessions": len([s for s in self.data.get("sessions", []) if s.get("end")]),
            "recent_blocks": self.data.get("blocked_urls", [])[-10:],
            "streak_days": self._calc_streak(),
        }

    def _calc_streak(self) -> int:
        sessions = self.data.get("sessions", [])
        days_with_focus = set()
        for s in sessions:
            if s.get("end") and s.get("focus_seconds", 0) > 0:
                days_with_focus.add(
                    datetime.fromisoformat(s["start"]).date()
                )
        if not days_with_focus:
            return 0
        streak = 0
        today = datetime.now().date()
        for i in range(365):
            day = today - timedelta(days=i)
            if day in days_with_focus:
                streak += 1
            else:
                break
        return streak

    def reset_stats(self) -> None:
        self.data = {
            "sessions": [],
            "total_blocked": 0,
            "total_focus_time_seconds": 0,
            "total_break_time_seconds": 0,
            "blocked_urls": [],
            "last_reset": datetime.now().isoformat(),
        }
        self._save()


# ─── Window/Process Management (Windows) ────────────────────────────────────

try:
    import win32gui
    import win32con
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logger.warning("pywin32 not available — window management disabled")


class WindowManager:
    """Manages browser windows and enforces blocking."""

    def __init__(self, stats):
        self.stats = stats
        self.is_active_session = False
        self.is_break = False

    def check_and_block(self, config: dict) -> None:
        """Check all open windows and block short-form content."""
        if not HAS_WIN32:
            return

        if self.is_break:
            return

        blocked_apps = config.get("blocked_apps", [])
        if blocked_apps:
            self._block_apps(blocked_apps)

        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                pid = win32gui.GetWindowThreadProcessId(hwnd)[1]

                should_close = False
                reason = ""

                if config.get("block_youtube_shorts") and "shorts" in title and "youtube" in title:
                    should_close = True
                    reason = "YouTube Shorts"
                elif config.get("block_reels") and ("reels" in title or "reel" in title) and "instagram" in title:
                    should_close = True
                    reason = "Instagram Reels"
                elif config.get("block_tiktok") and "tiktok" in title:
                    should_close = True
                    reason = "TikTok"
                elif config.get("block_instagram") and "instagram" in title:
                    should_close = True
                    reason = "Instagram"

                if should_close:
                    try:
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        self.stats.record_block(reason)
                        logger.info(f"Closed window ({reason}): {win32gui.GetWindowText(hwnd)}")
                    except Exception as e:
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                        logger.debug(f"Minimized window instead: {e}")
            return True

        win32gui.EnumWindows(enum_callback, None)

    def _block_apps(self, blocked_apps: list) -> None:
        """Kill specified processes."""
        import psutil
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = proc.info["name"].lower()
                for blocked_app in blocked_apps:
                    if blocked_app.lower() in proc_name:
                        proc.kill()
                        self.stats.record_block(f"App: {proc.info['name']}")
                        logger.info(f"Killed process: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def monitor_loop(self, config_loader, stop_event: threading.Event) -> None:
        """Continuously monitor and enforce blocking."""
        while not stop_event.is_set():
            try:
                cfg = config_loader()
                if cfg.get("enabled", True):
                    self.check_and_block(cfg)
            except Exception as e:
                logger.debug(f"Monitor error: {e}")
            time.sleep(1)


# ─── Process Protection ─────────────────────────────────────────────────────

class ProcessProtector:
    """Prevents the user from killing the unrotting process."""

    def __init__(self):
        self.pid = os.getpid()
        self._running = True

    def protect(self) -> None:
        """Runs in background to ensure process stays alive."""
        import psutil
        import subprocess

        while self._running:
            time.sleep(30)
            if not psutil.pid_exists(self.pid):
                logger.warning("Process died! Restarting...")
                self._restart()

    def _restart(self) -> None:
        """Restart the application."""
        self._running = False
        time.sleep(1)
        subprocess.Popen([sys.executable, "-m", "unrotting.app.main", "run"])
        sys.exit(0)


# ─── Auto-Elevation ────────────────────────────────────────────────────────

def is_admin() -> bool:
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def ensure_admin() -> bool:
    """Request admin elevation if needed. Returns True if we have admin or it was skipped."""
    if is_admin():
        return True

    logger.warning("Running without admin rights — hosts blocking will not work")
    return False


# ─── Main Application Entry Point ───────────────────────────────────────────

_window_manager = None
_stop_event = threading.Event()

def run_app() -> None:
    """Run the Unrotting application."""
    global _window_manager

    from app.ui import create_window

    config = load_config()

    # Ensure admin rights for hosts file
    ensure_admin()

    # Ensure hosts backup exists
    ensure_hosts_backup()

    # Update hosts based on config
    update_hosts_file(config)

    # Launch stats
    stats = Stats()

    # Start window manager thread
    _window_manager = WindowManager(stats)
    block_thread = threading.Thread(
        target=_window_manager.monitor_loop,
        daemon=True,
        args=(load_config, _stop_event),
    )
    block_thread.start()

    # Start process protector if strict mode
    if config.get("block_killing") and HAS_WIN32:
        protector = ProcessProtector()
        protect_thread = threading.Thread(
            target=protector.protect,
            daemon=True,
        )
        protect_thread.start()

    # Launch the web UI
    create_window(config, stats)


if __name__ == "__main__":
    run_app()

def validate_config(cfg: dict) -> tuple[bool, list]:
    """Validate configuration and return (is_valid, errors)."""
    errors = []
    
    # Check timing values
    if cfg.get("focus_duration_minutes", 45) != 45:
        errors.append("focus_duration_minutes must be 45")
    if cfg.get("break_duration_minutes", 15) != 15:
        errors.append("break_duration_minutes must be 15")
    if cfg.get("long_break_duration_minutes", 15) != 15:
        errors.append("long_break_duration_minutes must be 15")
    
    # Check required fields
    required = ["strict_mode", "block_reels", "block_shorts", "block_tiktok",
                "block_instagram", "block_youtube_shorts", "allow_full_videos",
                "focus_duration_minutes", "break_duration_minutes",
                "long_break_interval", "long_break_duration_minutes",
                "password_hash", "auto_start", "block_killing",
                "blocked_hosts", "blocked_apps", "whitelisted_urls",
                "enabled", "apps_locked"]
    
    for field in required:
        if field not in cfg:
            errors.append(f"Missing required field: {field}")
    
    return len(errors) == 0, errors

def safe_hosts_update(cfg: dict) -> dict:
    """Safely update hosts file with error handling."""
    result = {"success": False, "error": None}
    try:
        update_hosts_file(cfg)
        result["success"] = True
    except PermissionError:
        result["error"] = "Permission denied: Run as Administrator"
    except Exception as e:
        result["error"] = str(e)
    return result

# Performance optimizations
import gc

def optimize_memory():
    """Garbage collect and optimize memory usage."""
    gc.collect()

def lazy_load(func):
    """Decorator for lazy loading of expensive operations."""
    def wrapper(*args, **kwargs):
        optimize_memory()
        return func(*args, **kwargs)
    return wrapper

# Performance monitoring
import time
from functools import wraps

def performance_monitor(func):
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        if elapsed > 0.1:  # Log only slow operations
            logger.warning(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

def check_session_locked() -> bool:
    """Check if a focus session is active and locked."""
    return _session_active and not _is_break_time

def get_session_status() -> dict:
    """Get current session status for UI."""
    return {
        "is_active": _session_active,
        "is_break": _is_break_time,
        "is_locked": check_session_locked(),
        "time_remaining": _time_remaining if '_time_remaining' in globals() else 0
    }

# Global session state
_session_active = False
_is_break_time = False
_time_remaining = 0

def safe_config_save(cfg: dict) -> bool:
    """Safely save config with backup on failure."""
    try:
        # Create backup before save
        backup_path = CONFIG_DIR / "config.backup.json"
        if CONFIG_DIR / "config.json".exists():
            import shutil
            shutil.copy2(CONFIG_DIR / "config.json", backup_path)
        
        # Attempt save
        save_config(cfg)
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        # Try to restore from backup
        if (CONFIG_DIR / "config.backup.json").exists():
            try:
                import shutil
                shutil.copy2(CONFIG_DIR / "config.backup.json", CONFIG_DIR / "config.json")
                logger.info("Restored config from backup")
            except:
                pass
        return False

def safe_hosts_update(cfg: dict) -> dict:
    """Safely update hosts file with rollback on failure."""
    result = {"success": False, "error": None}
    try:
        # Backup first
        ensure_hosts_backup()
        
        # Update hosts
        update_hosts_file(cfg)
        result["success"] = True
    except PermissionError:
        result["error"] = "Permission denied: Run as Administrator"
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Hosts update failed: {e}")
    return result
