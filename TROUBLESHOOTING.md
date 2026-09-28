# Troubleshooting Guide

## Common Issues

### Permission Denied on Hosts File
**Symptom:** Error when trying to block domains
**Solution:**
1. Run the app as Administrator (Windows) or with sudo (macOS/Linux)
2. Or manually edit `C:\Windows\System32\drivers\etc\hosts`
3. Remove lines containing `# UNROTTING_BLOCK` to restore access

### Forgot Password
**Solution:**
1. Delete `config/config.json`
2. Restart the app
3. Set a new password

### App Won't Start
1. Check Python version: `python --version`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check logs: `unrotting.log`

### Blocking Not Working
1. Verify admin privileges
2. Check hosts file backup exists
3. Run `python -m unrotting.app.main backup-hosts`
4. Run `python -m unrotting.app.main restore-hosts`

### Stats Reset Unexpectedly
- This can happen if the config directory is deleted or permissions change
- Reset stats: `python -m unrotting.app.main reset-stats`

### macOS Specific
1. Allow app in System Preferences → Security & Privacy
2. If blocked by Gatekeeper: `xattr -cr /Applications/Unrotting.app`
3. For notarization issues, see BUILD.md

### Android Specific
1. Enable "Install from Unknown Sources" in settings
2. Grant storage permissions when prompted
3. Some devices may require additional permissions in Settings
