"""
Unrotting — Main entry point
"""
import sys
import argparse
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import load_config, save_config, hash_password, Stats
from app.ui import create_window


def cli(args: list = None) -> None:
    parser = argparse.ArgumentParser(
        description="Unrotting — Block distractions, stay focused"
    )
    sub = parser.add_subparsers(dest="command")

    # Run (default) - starts with tray, watcher, and monitoring
    run_parser = sub.add_parser("run", help="Start the Unrotting app")

    # Tray-only mode
    sub.add_parser("tray", help="Start system tray only (background mode)")

    # Watcher mode
    sub.add_parser("watcher", help="Start process watcher only")

    # Set password
    pw = sub.add_parser("password", help="Set or change your password")
    pw.add_argument("--new", required=True, help="New password")
    pw.add_argument("--old", help="Current password (if already set)")

    # Show config
    sub.add_parser("config", help="Show current configuration")

    # Reset stats
    sub.add_parser("reset-stats", help="Reset all statistics")

    # Backup/restore hosts
    bp = sub.add_parser("backup-hosts", help="Backup current hosts file")
    rp = sub.add_parser("restore-hosts", help="Restore hosts from backup")

    # Auto-start management
    as_parser = sub.add_parser("enable-auto-start", help="Enable auto-start on Windows boot")
    ds_parser = sub.add_parser("disable-auto-start", help="Disable auto-start on Windows boot")
    sub.add_parser("auto-start-status", help="Check auto-start status")

    # Desktop shortcut
    sub.add_parser("create-shortcut", help="Create desktop shortcut")
    sub.add_parser("remove-shortcut", help="Remove desktop shortcut")

    # Task management
    task_add = sub.add_parser("add-task", help="Add a new task")
    task_add.add_argument("title", help="Task title")
    task_add.add_argument("--points", type=int, default=50, help="Points earned")
    task_add.add_argument("--minutes", type=int, default=15, help="Minutes earned")
    task_add.add_argument("--no-daily", action="store_true", help="Not a daily task")

    task_list = sub.add_parser("list-tasks", help="List all tasks")

    task_complete = sub.add_parser("complete-task", help="Complete a task by ID")
    task_complete.add_argument("task_id", help="Task ID")

    task_reset = sub.add_parser("reset-tasks", help="Reset all tasks and points")

    parsed = parser.parse_args(args)

    config = load_config()

    if parsed.command == "password":
        if config.get("password_hash"):
            if not parsed.old:
                print("Error: current password required")
                sys.exit(1)
            from app import verify_password
            if not verify_password(config, parsed.old):
                print("Error: wrong password")
                sys.exit(1)
        config["password_hash"] = hash_password(parsed.new)
        save_config(config)
        print("Password set successfully")

    elif parsed.command == "config":
        import json
        print(json.dumps(config, indent=2))

    elif parsed.command == "reset-stats":
        stats = Stats()
        stats.reset_stats()
        print("Stats reset")

    elif parsed.command == "backup-hosts":
        from app import ensure_hosts_backup
        ensure_hosts_backup()
        print("Hosts file backed up")

    elif parsed.command == "restore-hosts":
        from app import HOSTS_FILE, BACKUP_HOSTS
        if BACKUP_HOSTS.exists():
            HOSTS_FILE.write_text(BACKUP_HOSTS.read_text())
            print("Hosts file restored")
        else:
            print("No backup found")

    elif parsed.command == "enable-auto-start":
        from app.autorun import enable_auto_start
        if enable_auto_start():
            print("Auto-start enabled successfully")
        else:
            print("Failed to enable auto-start")

    elif parsed.command == "disable-auto-start":
        from app.autorun import disable_auto_start
        if disable_auto_start():
            print("Auto-start disabled successfully")
        else:
            print("Failed to disable auto-start")

    elif parsed.command == "auto-start-status":
        from app.autorun import is_auto_start_enabled
        status = "Enabled" if is_auto_start_enabled() else "Disabled"
        print(f"Auto-start: {status}")

    elif parsed.command == "create-shortcut":
        from app.autorun import create_shortcut
        if create_shortcut():
            print("Shortcut created successfully")
        else:
            print("Failed to create shortcut")

    elif parsed.command == "remove-shortcut":
        from app.autorun import remove_shortcut
        if remove_shortcut():
            print("Shortcut removed successfully")
        else:
            print("Shortcut not found or removal failed")

    elif parsed.command == "add-task":
        from app import TaskManager
        tm = TaskManager()
        task = tm.add_task(
            title=parsed.title,
            points=parsed.points,
            reward_minutes=parsed.minutes,
            daily=not parsed.no_daily,
        )
        print(f"Task added: {task['id']} - {task['title']}")

    elif parsed.command == "list-tasks":
        from app import TaskManager
        tm = TaskManager()
        tasks = tm.get_tasks()
        if not tasks:
            print("No tasks found")
        else:
            for t in tasks:
                print(f"[{t['id'][:8]}] {t['title']} (+{t['points']}pts, +{t['reward_minutes']}min)")

    elif parsed.command == "complete-task":
        from app import TaskManager
        tm = TaskManager()
        result = tm.complete_task(parsed.task_id)
        if result:
            print(f"Task completed! Earned {result['points_earned']} points, {result['minutes_earned']} minutes")
        else:
            print("Task not found")

    elif parsed.command == "reset-tasks":
        from app import TaskManager
        tm = TaskManager()
        tm.reset_tasks()
        print("Tasks reset")

    elif parsed.command == "tray":
        from app.tray import run_tray
        run_tray()

    elif parsed.command == "watcher":
        from app.watcher import start_watcher
        watcher = start_watcher()
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()

    else:
        # Default: run full app with tray, watcher, and enforcement
        stats = Stats()
        from app import TaskManager
        task_manager = TaskManager()

        # Start window manager thread for enforcement
        from app import WindowManager
        window_manager = WindowManager(stats)
        stop_event = threading.Event()
        block_thread = threading.Thread(
            target=window_manager.monitor_loop,
            daemon=True,
            args=(load_config, stop_event),
        )
        block_thread.start()

        # Start watcher in background thread
        from app.watcher import start_watcher
        watcher = start_watcher()

        # Start tray in background thread
        from app.tray import UnrottingTray
        tray = UnrottingTray(window_manager=window_manager)
        tray_thread = threading.Thread(target=tray.run, daemon=True)
        tray_thread.start()

        # Run main window (blocks until closed)
        create_window(config, stats, task_manager, stop_event=stop_event)

        # Clean up
        tray._stop_icon_update.set()
        watcher.stop()


if __name__ == "__main__":
    cli()
