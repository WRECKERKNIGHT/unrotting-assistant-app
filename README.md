![PyPI version](https://img.shields.io/pypi/v/unrotting.svg)
![Python versions](https://img.shields.io/pypi/pyversions/unrotting.svg)
![Downloads](https://pepy.tech/badge/unrotting/month)

# Unrotting — Focus Assistant App

**Stop doomscrolling. Earn your scroll.**

Unrotting is a strict focus application that blocks short-form content (YouTube Shorts, Instagram Reels, TikTok) while allowing full-length videos. Built with a task-earning system, streak bonuses, and platform-native distribution support.

![GitHub release](https://img.shields.io/github/v/release/WRECKERKNIGHT/unrotting-assistant-app)
![License](https://img.shields.io/github/license/WRECKERKNIGHT/unrotting-assistant-app)
![Build status](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Android-blue)
![Python 3.14](https://img.shields.io/badge/Python-3.14-green)
![PyInstaller](https://img.shields.io/badge/PyInstaller-ready-brightgreen)

---

## 📥 Download & Releases

| Version | Date | Platforms | Files |
|---------|------|-----------|-------|
| [v1.0.0](https://github.com/WRECKERKNIGHT/unrotting-assistant-app/releases/tag/v1.0.0) | 2026-09-27 | Windows, macOS, Android | `UnrottingMinimal.exe`, `Unrotting.dmg`, `unrotting.apk` |
| v0.9.0-beta | 2026-09-20 | Windows | `Unrotting.exe` (beta) |
| v0.8.0-alpha | 2026-09-15 | Windows | First alpha build |

**Latest Release: v1.0.0**
👉 **[Download v1.0.0 Assets](https://github.com/WRECKERKNIGHT/unrotting-assistant-app/releases/tag/v1.0.0)**

### Windows
```bash
# Portable executable (no installation needed)
./UnrottingMinimal.exe
```
Run as Administrator for hosts-file blocking.

### macOS
```bash
# Mount and open DMG
hdiutil attach dist/Unrotting.dmg
open /Volumes/Unrotting/Unrotting.app
```
Build: `bash scripts/build-mac-dmg.sh`

### Android
```bash
# Install APK
adb install bin/unrotting-1.0.0.apk
```
Build: `bash scripts/build-android-apk.sh` (WSL2/Linux required)

---

## ✨ Features

### Core Blocking
- **Hosts-file blocking** — redirects TikTok, Instagram Reels, YouTube Shorts to localhost
- **Process enforcement** — kills configurable apps during focus sessions
- **Window monitoring** — detects and closes browser tabs with Shorts/Reels/TikTok titles
- **Strict mode** — prevents closing the app during active focus sessions

### Pomodoro Timer
- Fixed 45-minute focus → 15-minute break cycles
- Long break every 4 sessions (15 minutes)
- Cannot modify timer during sessions (no loopholes)

### Task & Points System
- Create tasks with custom points and time rewards
- Streak multiplier: up to 2x bonus for consistent daily use
- Earn bonus focus minutes by completing real-world tasks
- Tracks points, streaks, and completion history

### Cross-Platform
| Platform | Format | Size | Notes |
|----------|--------|------|-------|
| Windows | `.exe` (PyInstaller) | 33 MB | Run as admin for hosts blocking |
| macOS | `.dmg` (PyInstaller + codesign) | ~35 MB | Requires notarization for App Store |
| Android | `.apk` (Buildozer + Kivy) | ~25 MB | Needs Android SDK; WSL2 supported |

### Security
- SHA-256 password hashing (no plain-text storage)
- Admin-restricted hosts file modification
- Config locked during active sessions
- Process protector prevents accidental termination

---

## 🛠 Installation

### Prerequisites
- Python 3.10+
- pip package manager

### Quick Install
```bash
git clone https://github.com/WRECKERKNIGHT/unrotting-assistant-app.git
cd unrotting-assistant-app
pip install -r requirements.txt
python -m unrotting.app.main run
```

### First-Time Setup
```bash
# Set password (required for first use)
python -m unrotting.app.main password --new yourpassword

# Create desktop shortcut
python -m unrotting.app.main create-shortcut

# Enable auto-start on boot
python -m unrotting.app.main enable-auto-start
```

---

## 📖 Usage

### CLI Commands
```bash
# Start the app
python -m unrotting.app.main run

# System tray only (background mode)
python -m unrotting.app.main tray

# Task management
python -m unrotting.app.main add-task "Workout 30min" --points 100 --minutes 30
python -m unrotting.app.main list-tasks
python -m unrotting.app.main complete-task <task-id>

# Maintenance
python -m unrotting.app.main reset-stats
python -m unrotting.app.main backup-hosts
python -m unrotting.app.main restore-hosts

# Auto-start
python -m unrotting.app.main enable-auto-start
python -m unrotting.app.main disable-auto-start
```

### During a Session
- **Focus**: 45 minutes — blocking is enforced
- **Break**: 15 minutes — hosts unblocked, tasks can be completed
- **Skip Break**: Jump straight to next focus session
- **Strict Mode**: Cannot close window or modify settings

---

## 🏗 Architecture

```
unrotting-assistant-app/
├── app/                     # Core Python modules
│   ├── __init__.py          # Blocking, stats, tasks, config engine
│   ├── main.py              # CLI entry point
│   ├── ui.py                # Pywebview UI wrapper
│   ├── tray.py              # System tray icon
│   ├── watcher.py           # Process auto-restart
│   └── autorun.py           # Windows startup integration
├── ui/                      # Frontend
│   ├── index.html           # Interface markup
│   ├── styles.css           # Minimal dark glassmorphism
│   └── app.js               # Frontend logic
├── assets/                  # Icons and branding
├── config/                  # Runtime config & data
├── scripts/                 # Build scripts
│   ├── build-exe.bat        # Windows build
│   ├── build-mac-dmg.sh     # macOS build
│   └── build-android.sh     # Android build
├── dist/                    # Built executables
├── requirements.txt
├── pyproject.toml
└── LICENSE                  # MIT License
```

### Tech Stack
| Layer | Technology |
|-------|------------|
| Language | Python 3.14 |
| Desktop UI | pywebview (Chromium) |
| Window Management | pywin32 |
| System Tray | pystray + Pillow |
| Process Monitoring | psutil |
| Packaging (Win) | PyInstaller |
| Packaging (Mac) | PyInstaller + hdiutil |
| Packaging (Android) | Buildozer + Kivy |

---

## 📝 Changelog

### v1.0.0 (2026-09-27)
- Merged TypeScript task-engine into unified Python app
- Redesigned UI with minimal dark theme (Inter font, 2-color palette)
- Fixed 22 identified bugs (tray timer, enforcement threads, config locking)
- Added cross-platform build scripts (Windows, macOS, Android)
- Added admin auto-detection and permission warnings
- Performance optimizations (reduced logging I/O)
- Added `pyproject.toml` for proper package distribution
- Comprehensive documentation (README, GUIDE, BUILD guides)

### v0.9.0-beta (2026-09-20)
- Added task and points system
- Added streak multiplier calculation
- Integrated task UI into web interface
- Added Android build script

### v0.8.0-alpha (2026-09-15)
- Initial functional release
- Hosts-file blocking
- System tray with live timer
- Password protection
- Basic web UI with glassmorphism design

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run in development mode (no admin required for UI testing)
PYTHONPATH=. python -m app.main run

# Rebuild EXE
python -m PyInstaller --onefile --name Unrotting --add-data "ui;ui" --add-data "assets;assets" app/__main__.py
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

### License Summary
- ✅ Free to use, modify, and distribute
- ✅ Commercial use allowed
- ✅ No warranty provided
- ❌ Authors not liable for damages

---

## 👥 Authors

- **WRECKERKNIGHT** — [GitHub](https://github.com/WRECKERKNIGHT) — `harsithardik312@gmail.com`
- Built with ❤️ for focus and productivity

---

## 🙏 Acknowledgments

- [pywebview](https://github.com/r0x0r/pywebview) — Cross-platform webview containers
- [pywin32](https://github.com/mhammond/pywin32) — Windows API bindings
- [pystray](https://github.com/moses-palmer/pystray) — System tray icons
- [PyInstaller](https://www.pyinstaller.org/) — Python to executable bundling
- [Buildozer](https://github.com/kivy/buildozer) — Android APK packaging
- [Inter Font](https://rsms.me/inter/) — Typography

---

**Take back your time. Earn your scroll.** 🔥

---

## Downloads

| Platform | Version | Download |
|----------|---------|----------|
| Windows | v1.0.0 | [UnrottingMinimal.exe](https://github.com/WRECKERKNIGHT/unrotting-assistant-app/releases/download/v1.0.0/UnrottingMinimal.exe) |
| macOS | v1.0.0 | [Unrotting.dmg](https://github.com/WRECKERKNIGHT/unrotting-assistant-app/releases/download/v1.0.0/Unrotting.dmg) |
| Android | v1.0.0 | [unrotting.apk](https://github.com/WRECKERKNIGHT/unrotting-assistant-app/releases/download/v1.0.0/unrotting.apk) |
