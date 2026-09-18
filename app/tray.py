"""
Unrotting System Tray - Always-active system tray icon with timer display
"""
import os
import sys
import time
import threading
from pathlib import Path

import pystray
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import load_config, Stats, update_hosts_file, TaskManager


class UnrottingTray:
    """System tray icon for Unrotting with live timer display."""

    def __init__(self, window_manager=None):
        self.window_manager = window_manager
        self.stats = Stats()
        self.task_manager = TaskManager()
        self.config = load_config()
        self.is_running = False
        self.is_break = False
        self.time_left = 45 * 60
        self.total_time = 45 * 60
        self.session_id = None
        self.session_start_time = None

        # Icon setup
        self.icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
        self.menu = self._create_menu()
        self._stop_icon_update = threading.Event()

    def _create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Open Unrotting", self._open_app, default=True),
            pystray.MenuSeparator(),
            pystray.MenuItem("Start Focus Session", self._start_focus,
                           enabled=lambda: not self.is_running),
            pystray.MenuItem("Pause Timer", self._pause_timer,
                           enabled=lambda: self.is_running and not self.is_break),
            pystray.MenuItem("Resume Timer", self._resume_timer,
                           enabled=lambda: self.is_running and not self.is_break),
            pystray.MenuItem("Skip Break", self._skip_break,
                           enabled=lambda: self.is_running and self.is_break),
            pystray.MenuSeparator(),
            pystray.MenuItem("Settings", self._open_settings),
            pystray.MenuItem("Exit", self._exit_app),
        )

    def _open_app(self, icon=None, menu=None):
        try:
            from app.ui import create_window
            config = load_config()
            from app import TaskManager
            task_manager = TaskManager()
            create_window(config, self.stats, task_manager, self.window_manager)
        except Exception as e:
            print(f"Error opening app: {e}")

    def _start_focus(self, icon=None, menu=None):
        self.is_running = True
        self.is_break = False
        self.time_left = 45 * 60
        self.total_time = 45 * 60
        self.session_id = self.stats.start_session()
        self.session_start_time = time.time()
        update_hosts_file(self.config, force_unblock=False)

    def _pause_timer(self, icon=None, menu=None):
        self.is_running = False

    def _resume_timer(self, icon=None, menu=None):
        self.is_running = True

    def _skip_break(self, icon=None, menu=None):
        self.is_break = False
        self.time_left = 45 * 60
        self.total_time = 45 * 60
        self.is_running = True
        update_hosts_file(self.config, force_unblock=False)

    def _open_settings(self, icon=None, menu=None):
        self._open_app(icon, menu)

    def _exit_app(self, icon=None, menu=None):
        if self.session_id and self.session_start_time:
            focus_seconds = int(time.time() - self.session_start_time)
            self.stats.end_session(self.session_id, 0, focus_seconds)
        self._stop_icon_update.set()
        icon.stop()

    def _generate_icon(self, icon=None):
        if self.icon_path.exists():
            img = Image.open(self.icon_path).resize((128, 128), Image.Resampling.LANCZOS)
        else:
            img = Image.new('RGBA', (128, 128), (15, 12, 41, 255))

        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        # Status indicator dot
        if self.is_break:
            draw.ellipse([100, 10, 120, 30], fill=(74, 222, 128))
        elif self.is_running:
            draw.ellipse([100, 10, 120, 30], fill=(255, 107, 53))
        else:
            draw.ellipse([100, 10, 120, 30], fill=(148, 163, 184))

        # Draw time text if running
        if self.is_running and self.time_left > 0:
            mins = self.time_left // 60
            secs = self.time_left % 60
            time_str = f"{mins:02d}:{secs:02d}"
            bbox = draw.textbbox((0, 0), time_str, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (128 - text_width) // 2
            y = 128 - text_height - 15
            draw.text((x, y), time_str, fill='white', font=font)

        return img

    def _update_icon_loop(self):
        """Background thread to update icon periodically."""
        while not self._stop_icon_update.is_set():
            self._stop_icon_update.wait(1)
            # Trigger icon update by calling update
            if self._running_icon:
                self._running_icon.update_icon()

    def run(self):
        self._stop_icon_update.clear()
        self._running_icon = None

        tray_icon = pystray.Icon(
            "unrotting",
            self._generate_icon,
            "Unrotting - Focus Hard",
            self.menu
        )

        self._running_icon = tray_icon

        # Start icon update thread
        self._update_icon_thread = threading.Thread(target=self._update_icon_loop, daemon=True)
        self._update_icon_thread.start()

        tray_icon.run()


def run_tray():
    tray = UnrottingTray()
    tray.run()


if __name__ == "__main__":
    run_tray()

def update_timer_display(self, icon=None):
    """Update the tray icon timer display."""
    if self.is_running and self.time_left > 0:
        self._generate_icon(icon)
        icon.update_icon()
