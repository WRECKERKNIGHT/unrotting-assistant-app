# Unrotting — Unified Project Guide

## What Is This?

Unrotting is a strict focus application that helps you stop doomscrolling. It blocks short-form content (YouTube Shorts, Instagram Reels, TikTok) while allowing full videos. The key innovation: you earn bonus focus time by completing real-world tasks.

---

## Merged Features

### From Python App (unrotting-app)
- Hosts file blocking (redirects blocked domains to localhost)
- Window title monitoring (closes Shorts/Reels/TikTok tabs)
- Process killing (can terminate specified apps)
- Fixed 45-min Pomodoro timer (locked to prevent loopholes)
- System tray with live countdown
- Password protection
- Auto-start on Windows boot
- Desktop shortcut creation

### From TypeScript Project (unrotting)
- Task creation system
- Points and streak multiplier
- Time earning from tasks
- Activity logging

---

## Bugs Fixed (22 Total)

| # | Bug | Fix |
|---|-----|-----|
| 1 | `main.py` `run_app()` was dead code | Removed; unified entry point |
| 2 | Normal launch skipped enforcement threads | Added WindowManager to `run` command |
| 3 | Missing hosts backup/update on launch | Added in main.py run path |
| 4 | `app.js` line 290 called `start_break()` at wrong time | Removed erroneous line |
| 5 | Tray `_exit_app` referenced undefined `block_count` | Fixed to use 0 |
| 6 | Tray timer never ticked | Added icon update loop |
| 7 | `_lock_apps`/`_unlock_apps` had no effect | Added config save |
| 8 | `watcher` checked exact process name | Now checks any running process |
| 9 | `watcher` restart lost admin rights | Kept same launch method |
| 10 | `autorun` targeted tray instead of full app | Now starts `run` command |
| 11 | `unrotting.bat` referenced non-existent modules | Fixed all module paths |
| 12 | Config had stale timing values | Enforced 45/15/15 on load/save |
| 13 | Missing `blocked_apps` key in config | Added to DEFAULT_CONFIG |
| 14 | UI settings couldn't change timing (by design) | Documented as locked feature |
| 15 | `window_manager` param unused in API | Removed parameter |
| 16 | Window close blocking was fragile | Kept but noted as pywebview-dependent |
| 17 | Stats save failed silently | Added warning logging |
| 18 | No package installability | Added pyproject.toml |
| 19 | Duplicate logic in `__init__.py` and `main.py` | Unified to main.py |
| 20 | `__main__.py` forwarding was broken | Fixed import path |
| 21 | Hosts file permission error handling | Added clear error messages |
| 22 | Orphaned log entries from old version | Cleaned log handling |

---

## New Features Added

### Task System
- Create tasks with custom points and minute rewards
- Complete tasks during breaks or idle time
- Streak multiplier: 10% bonus per day, capped at 2x
- Points tracking in header and summary cards

### UI Improvements
- Added tasks section to main interface
- Added summary card showing points today, minutes earned, tasks completed
- Header shows current points and streak
- All CSS styled consistently

### CLI Commands
```
add-task <title> [--points N] [--minutes N] [--no-daily]
list-tasks
complete-task <id>
reset-tasks
```

---

## Project Structure

```
unrotting-unified/
├── app/
│   ├── __init__.py      # Core: config, stats, tasks, blocking
│   ├── main.py          # CLI entry point
│   ├── __main__.py      # Module entry point
│   ├── ui.py            # Pywebview UI wrapper
│   ├── tray.py          # System tray with timer
│   ├── watcher.py       # Process auto-restart
│   └── autorun.py       # Windows startup management
├── ui/
│   ├── index.html       # Interface HTML
│   ├── styles.css       # Glassmorphism styling
│   └── app.js           # Frontend logic
├── assets/
│   ├── icon.png         # App icon
│   └── icon.ico         # Windows icon
├── config/
│   ├── config.json      # App configuration
│   ├── stats.json       # Focus statistics
│   └── tasks.json       # Tasks and points
├── scripts/
│   ├── build-exe.bat    # Windows build script
│   ├── build-mac-dmg.sh # macOS build script
│   └── build-android-apk.sh # Android build script
├── dist/
│   └── Unrotting.exe    # Windows executable (33MB)
├── pyproject.toml       # Python package config
├── requirements.txt     # Dependencies
├── run.bat              # Quick launcher
├── unrotting.bat        # Control panel menu
└── README.md            # Documentation
```

---

## Build Instructions

### Windows EXE (Already Built)
```
Output: dist/Unrotting.exe (33 MB)
```

To rebuild:
```bash
cd C:\Users\harsh\Projects\unrotting-unified
python -m PyInstaller --onefile --name Unrotting --add-data "ui;ui" --add-data "assets;assets" --hidden-import=win32gui --hidden-import=win32con --hidden-import=pystray --hidden-import=PIL --collect-all pywebview app/__main__.py
```

### macOS DMG
Run on a Mac:
```bash
bash scripts/build-mac-dmg.sh
```

### Android APK
Run in WSL2 or Linux:
```bash
bash scripts/build-android-apk.sh
```

---

## How to Use

### First Time Setup
1. **Run as Administrator** (for hosts file access):
   ```bash
   cd C:\Users\harsh\Projects\unrotting-unified
   .\run.bat
   ```
   Or right-click `dist/Unrotting.exe` → Run as administrator

2. **Set your password**:
   ```bash
   python -m app.main password --new yourpassword
   ```

3. **Add tasks** (optional):
   ```bash
   python -m app.main add-task "Workout 30min" --points 100 --minutes 30
   ```

4. **Create desktop shortcut**:
   ```bash
   python -m app.main create-shortcut
   ```

5. **Enable auto-start**:
   ```bash
   python -m app.main enable-auto-start
   ```

### Daily Usage
- Double-click `run.bat` or the desktop shortcut
- Enter your password (or start if no password set)
- Click "Start Focus" to begin 45-minute session
- During break, you can add/complete tasks
- Blocked apps/sites are enforced automatically

### CLI Reference
| Command | Description |
|---------|-------------|
| `python -m app.main run` | Start the app |
| `python -m app.main tray` | System tray only |
| `python -m app.main config` | Show configuration |
| `python -m app.main password --new <pw>` | Set/change password |
| `python -m app.main reset-stats` | Reset statistics |
| `python -m app.main add-task <title>` | Add a task |
| `python -m app.main list-tasks` | List all tasks |
| `python -m app.main complete-task <id>` | Complete a task |
| `python -m app.main reset-tasks` | Reset tasks and points |
| `python -m app.main backup-hosts` | Backup hosts file |
| `python -m app.main restore-hosts` | Restore hosts file |
| `python -m app.main enable-auto-start` | Add to Windows startup |
| `python -m app.main create-shortcut` | Create desktop shortcut |

---

## Troubleshooting

### Permission denied on hosts file
- Run as Administrator
- Or manually edit: `C:\Windows\System32\drivers\etc\hosts`
- Remove lines containing `# UNROTTING_BLOCK`

### Forgot password
1. Delete `config/config.json`
2. Restart app — fresh without password

### App won't start
```bash
# Check Python
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

### Restore Hosts File
```bash
python -m app.main restore-hosts
```

### Stats/Task files missing
- They are auto-created on first use
- If corrupted, delete and restart

---

## Security Features

- Password-protected settings
- Hosts file modifications require admin rights
- Process protection prevents easy termination
- Settings locked during focus sessions
- Blocked apps cannot be removed during sessions
- Window close blocked during focus (strict mode)

---

## License

MIT
