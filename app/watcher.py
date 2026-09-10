"""
Unrotting Watcher - Ensures app is always running
"""
import os
import sys
import time
import subprocess
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
PROJECT_ROOT = Path(__file__).parent.parent


class ProcessWatcher:
    """Watches for the main app process and restarts if needed."""

    def __init__(self, pid=None):
        self.pid = pid or os.getpid()
        self._running = True
        self._restart_count = 0
        self._max_restarts = 10
        self._restart_delay = 5

    def watch(self):
        print(f"Watcher started, monitoring PID: {self.pid}")

        while self._running and self._restart_count < self._max_restarts:
            time.sleep(30)

            if not self._is_process_alive():
                print(f"Process {self.pid} died, restarting...")
                self._restart_count += 1
                time.sleep(self._restart_delay)
                self._restart_app()

        if self._restart_count >= self._max_restarts:
            print("Max restart attempts reached, watcher stopping")

    def _is_process_alive(self):
        try:
            import psutil
            proc = psutil.Process(self.pid)
            # Check if process is still running (don't require exact name)
            return proc.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        except ImportError:
            try:
                result = subprocess.run(
                    ['tasklist', '/FI', f'PID eq {self.pid}', '/FO', 'CSV', '/NH'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            except:
                return False

    def _restart_app(self):
        try:
            python_exe = sys.executable
            # Try to run as admin if possible
            subprocess.Popen(
                [python_exe, "-m", "unrotting.app.main", "run"],
                cwd=str(PROJECT_ROOT),
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
            print(f"App restarted successfully (attempt {self._restart_count})")
        except Exception as e:
            print(f"Failed to restart app: {e}")

    def stop(self):
        self._running = False
        print("Watcher stopped")


def start_watcher():
    watcher = ProcessWatcher()
    thread = threading.Thread(target=watcher.watch, daemon=True)
    thread.start()
    return watcher


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Unrotting Process Watcher")
    parser.add_argument("--pid", type=int, help="PID to watch")
    args = parser.parse_args()

    watcher = ProcessWatcher(pid=args.pid)
    print("Watcher running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
