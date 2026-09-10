# Unrotting Setup & Usage Guide

## Quick Start

### 1. First Time Setup (Run as Administrator)

**Windows:** Right-click `run.bat` → "Run as administrator"

Or run from terminal:
```bash
# Set your password first
"C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe" -m unrotting.password --new yourpassword

# Then run the app (needs admin for hosts file)
"C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe" -m unrotting.app.main run
```

### 2. Commands

| Command | Description |
|---------|-------------|
| `python -m unrotting` | Run the app |
| `python -m unrotting password --new <pw>` | Set password |
| `python -m unrotting password --new <new> --old <old>` | Change password |
| `python -m unrotting config` | View config |
| `python -m unrotting reset-stats` | Reset statistics |
| `python -m unrotting backup-hosts` | Backup hosts file |
| `python -m unrotting restore-hosts` | Restore hosts file |

## How It Works

### Blocking Mechanisms

1. **Hosts File Blocking** - Redirects blocked domains to localhost:
   - YouTube Shorts (`youtube.com/shorts`)
   - Instagram Reels (`instagram.com/reels`)
   - TikTok (`tiktok.com`)
   - Facebook Reels (`facebook.com/reel`)

2. **Custom App Blocking** - Kills specified processes during focus:
   - Add apps in the UI before starting a session
   - Example: `chrome.exe`, `tiktok.exe`, `firefox.exe`
   - **Cannot be removed during active session**

3. **Window Title Monitoring** - Detects and closes browser tabs with:
   - "Shorts" + "YouTube" in title
   - "Reels" or "Reel" + "Instagram" in title
   - "TikTok" in title

### Fixed Timing (No Loopholes)

- **Focus**: 45 minutes (locked, cannot change)
- **Break**: 15 minutes (locked, cannot change)
- **Long Break**: Every 4 sessions, 15 minutes

### Session Lock (No Bypassing)

Once you start a focus session:
- ❌ Cannot modify blocked apps
- ❌ Cannot change settings
- ❌ Cannot close the window (strict mode)
- ❌ Cannot access shortcuts/reels/tiktok

During break time:
- ✅ Can modify blocked apps
- ✅ Can change settings
- ✅ Can close window

## Security Features

| Feature | Description |
|---------|-------------|
| Password Protection | Lock settings and config |
| Hosts File Protection | Requires admin to modify |
| Process Protection | Auto-restarts if killed |
| Session Locking | Prevents changes during focus |
| Window Close Blocking | Prevents closing during session |

## Usage Examples

### Adding Blocked Apps

1. Open Unrotting
2. In the "Blocked Apps" section, type app name (e.g., `chrome.exe`)
3. Click "Add" or press Enter
4. Start your focus session
5. The app will kill Chrome if you try to open it

### Starting a Session

1. Click "Start Focus"
2. Timer begins at 45:00
3. Blocked apps are enforced
4. Hosts file blocks short-form content
5. Cannot change anything until timer ends

### Skipping a Break

If you want to skip break and continue focusing:
1. Click "Skip Break" button
2. Timer jumps to next focus session
3. Apps remain blocked

## Troubleshooting

### Permission Errors
```
Error: Permission denied: 'C:\\Windows\\System32\\drivers\\etc\\hosts'
```
**Solution**: Run as Administrator

### Forgot Password
1. Delete `config/config.json`
2. Restart app
3. Set new password

### App Won't Start
```bash
# Check Python
"C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe" --version

# Install dependencies
"C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe" -m pip install pywebview pywin32 psutil
```

### Restore Hosts File
```bash
python -m unrotting restore-hosts
```

## Project Location

```
C:\Users\harsh\projects\unrotting-app\
```

## Files

| File | Purpose |
|------|---------|
| `run.bat` | Windows launcher |
| `app/__init__.py` | Core blocking logic |
| `app/ui.py` | Pywebview interface |
| `app/main.py` | CLI entry point |
| `ui/index.html` | Web interface |
| `ui/styles.css` | Styling |
| `ui/app.js` | Frontend logic |
| `config/config.json` | Configuration |
| `config/stats.json` | Statistics |
