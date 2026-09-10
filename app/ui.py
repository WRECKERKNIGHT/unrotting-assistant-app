"""
Unrotting UI - Web-based interface using pywebview
"""
import webview
from pathlib import Path
import time

BASE_DIR = Path(__file__).parent.parent
HTML_FILE = BASE_DIR / "ui" / "index.html"


class UnrottingAPI:
    def __init__(self, config, stats, task_manager, window_manager=None):
        self.config = config
        self.stats = stats
        self.task_manager = task_manager
        self.window_manager = window_manager
        self.session_id = None
        self.session_start_time = None
        self.block_count = 0
        self.is_break = False

    def get_config(self) -> dict:
        cfg = self.config.copy()
        if cfg.get("password_hash"):
            cfg["has_password"] = True
        del cfg["password_hash"]
        return cfg

    def set_config(self, updates: dict) -> dict:
        updates["focus_duration_minutes"] = 45
        updates["break_duration_minutes"] = 15
        updates["long_break_duration_minutes"] = 15

        for key, value in updates.items():
            if key in self.config:
                self.config[key] = value

        from app import update_hosts_file, save_config
        update_hosts_file(self.config)
        save_config(self.config)
        return self.get_config()

    def start_session(self) -> dict:
        self.session_id = self.stats.start_session()
        self.session_start_time = time.time()
        self.block_count = 0
        self.is_break = False

        from app import update_hosts_file
        update_hosts_file(self.config, force_unblock=False)
        return {"session_id": self.session_id, "started": True}

    def end_session(self) -> dict:
        if self.session_id and self.session_start_time:
            focus_seconds = int(time.time() - self.session_start_time)
            self.stats.end_session(self.session_id, self.block_count, focus_seconds)
        self.session_id = None
        self.session_start_time = None
        self.block_count = 0
        return {"ended": True}

    def get_stats(self) -> dict:
        stats_summary = self.stats.get_summary()
        task_summary = self.task_manager.get_summary()
        return {**stats_summary, **task_summary}

    def reset_stats(self) -> dict:
        self.stats.reset_stats()
        return {"reset": True}

    def record_block(self, url_or_app: str) -> None:
        self.block_count += 1
        self.stats.record_block(url_or_app)

    def set_password(self, password: str) -> dict:
        from app import hash_password, save_config
        self.config["password_hash"] = hash_password(password)
        save_config(self.config)
        return {"success": True}

    def verify_password(self, password: str) -> bool:
        from app import verify_password
        return verify_password(self.config, password)

    def backup_hosts(self) -> bool:
        from app import ensure_hosts_backup
        ensure_hosts_backup()
        return True

    def restore_hosts(self) -> bool:
        from app import HOSTS_FILE, BACKUP_HOSTS
        try:
            if BACKUP_HOSTS.exists():
                HOSTS_FILE.write_text(BACKUP_HOSTS.read_text())
                return True
        except Exception as e:
            print(f"Failed to restore hosts: {e}")
        return False

    def start_break(self) -> dict:
        self.is_break = True
        from app import update_hosts_file
        update_hosts_file(self.config, force_unblock=True)
        return {"break_started": True}

    def end_break(self) -> dict:
        self.is_break = False
        from app import update_hosts_file
        update_hosts_file(self.config, force_unblock=False)
        return {"break_ended": True}

    # ─── Task API ──────────────────────────────────────────────────────────

    def get_tasks(self) -> list:
        return self.task_manager.get_tasks()

    def complete_task(self, task_id: str) -> dict:
        result = self.task_manager.complete_task(task_id)
        return result if result else {"error": "Task not found"}

    def add_task(self, title: str, points: int = 50, reward_minutes: int = 15, daily: bool = True) -> dict:
        task = self.task_manager.add_task(title, points, reward_minutes, daily)
        return task

    def reset_tasks(self) -> dict:
        self.task_manager.reset_tasks()
        return {"reset": True}


def _run_webview(api: UnrottingAPI) -> None:
    window = webview.create_window(
        title="Unrotting — Focus Hard",
        url=f"file:///{HTML_FILE.as_posix().replace(chr(92), '/')}",
        width=950,
        height=800,
        resizable=False,
        fullscreen=False,
        min_size=(850, 700),
        text_select=True,
    )

    # Expose API to JavaScript
    api_obj = api
    window.expose(api_obj.get_config)
    window.expose(api_obj.set_config)
    window.expose(api_obj.start_session)
    window.expose(api_obj.end_session)
    window.expose(api_obj.get_stats)
    window.expose(api_obj.reset_stats)
    window.expose(api_obj.record_block)
    window.expose(api_obj.set_password)
    window.expose(api_obj.verify_password)
    window.expose(api_obj.backup_hosts)
    window.expose(api_obj.restore_hosts)
    window.expose(api_obj.start_break)
    window.expose(api_obj.end_break)
    window.expose(api_obj.get_tasks)
    window.expose(api_obj.complete_task)
    window.expose(api_obj.add_task)
    window.expose(api_obj.reset_tasks)

    # Prevent window close during active session
    def on_closing():
        if api_obj.session_id is not None and not api_obj.is_break:
            return False
        return True

    window.events.closing += on_closing

    webview.start(debug=False)


def create_window(config, stats, task_manager=None, window_manager=None, stop_event=None) -> None:
    """Entry point for the UI."""
    if task_manager is None:
        from app import TaskManager
        task_manager = TaskManager()
    api = UnrottingAPI(config, stats, task_manager, window_manager)
    _run_webview(api)
