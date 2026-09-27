# Unrotting - Build Guide

This document explains how to build executables for all platforms.

## Prerequisites

- Python 3.10+ installed
- pip package manager
- For Android: Linux environment or WSL2 with Android SDK
- For macOS DMG: macOS or cross-compilation environment

## Quick Start

### Windows EXE (from Windows)
```bash
cd C:\Users\harsh\Projects\unrotting-unified
python -m PyInstaller --onefile --name Unrotting --add-data "ui;ui" --add-data "assets;assets" --hidden-import=win32gui --hidden-import=win32con --hidden-import=pystray --hidden-import=PIL --collect-all pywebview app/__main__.py
```

Output: `dist/Unrotting.exe`

### macOS DMG (from macOS)
```bash
cd /path/to/unrotting-unified
bash scripts/build-mac-dmg.sh
```

Output: `dist/Unrotting.dmg`

### Android APK (from Linux/WSL2)
```bash
cd /path/to/unrotting-unified
bash scripts/build-android-apk.sh
```

Output: `bin/Unrotting-1.0.0-debug.apk`

## Manual Build Commands

### Windows (PyInstaller)
```bash
python -m PyInstaller --onefile ^
    --name Unrotting ^
    --add-data "ui;ui" ^
    --add-data "assets;assets" ^
    --hidden-import=win32gui ^
    --hidden-import=win32con ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --collect-all pywebview ^
    app/__main__.py
```

### macOS (PyInstaller)
```bash
python3 -m PyInstaller --onefile \
    --name Unrotting \
    --add-data "ui:ui" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "org.unrotting.app" \
    app/__main__.py
```

Create DMG:
```bash
hdiutil create -volname "Unrotting" -srcfolder dist/Unrotting.app -ov -format UDZO dist/Unrotting.dmg
```

### Android (Buildozer)
```bash
pip install buildozer cython kivy
buildozer android debug
```

## Notes

- The Windows EXE is ~33MB (includes Python runtime)
- The Android APK requires Android SDK and Java JDK
- The macOS DMG requires macOS build tools
- All builds include the complete application with dependencies

## Testing

After building, test the executable:
```bash
# Windows
./dist/Unrotting.exe

# macOS
open dist/Unrotting.app

# Android
adb install bin/Unrotting-1.0.0-debug.apk
```

## macOS Build (Requires macOS)

```bash
# Prerequisites:
# - macOS 10.15+ (Catalina or later)
# - Xcode Command Line Tools: xcode-select --install
# - Python 3.10+ installed via Homebrew or python.org
# - Apple Developer Account (for code signing/notarization)

# Build
cd unrotting-assistant-app
bash scripts/build-mac-dmg.sh

# Output: dist/Unrotting.dmg
```

### Code Signing (Optional but recommended for distribution)

```bash
# Sign the app bundle
codesign --sign "Developer ID Application: Your Name (TEAMID)" \
    --deep --force --options runtime \
    dist/Unrotting.app

# Verify signature
codesign --verify --deep --strict dist/Unrotting.app
```

### Notarization (Required for macOS 10.15+ distribution)

```bash
# Create DMG first
bash scripts/build-mac-dmg.sh

# Submit for notarization
xcrun notarytool submit dist/Unrotting.dmg \
    --apple-id "your@email.com" \
    --team-id "TEAMID" \
    --password "app-specific-password" \
    --wait

# Staple the notarization ticket
xcrun stapler staple dist/Unrotting.dmg

# Verify
spctl -a -v dist/Unrotting.app
```

### Build on CI (GitHub Actions)

```yaml
# .github/workflows/macos-build.yml
name: macOS Build
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install pyinstaller
      - name: Build
        run: bash scripts/build-mac-dmg.sh
      - name: Upload DMG
        uses: actions/upload-artifact@v4
        with:
          name: Unrotting-dmg
          path: dist/Unrotting.dmg
```
