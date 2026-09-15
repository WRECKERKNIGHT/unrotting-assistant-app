#!/bin/bash
# Build macOS DMG for Unrotting
# This script should be run on macOS or in a cross-compilation environment

set -e

echo "====================================="
echo " Building Unrotting macOS DMG"
echo "====================================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install Python 3.10+."
    exit 1
fi

# Install PyInstaller
pip3 install pyinstaller --quiet

# Clean previous builds
rm -rf build dist

# Build the executable
echo "Building macOS application..."
python3 -m PyInstaller --onefile \
    --name "Unrotting" \
    --add-data "ui:ui" \
    --add-data "assets:assets" \
    --hidden-import=win32gui \
    --hidden-import=win32con \
    --hidden-import=pystray \
    --hidden-import=PIL \
    --collect-all pywebview \
    --osx-bundle-identifier "org.unrotting.app" \
    app/__main__.py

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

# Create DMG
echo "Creating DMG package..."
mkdir -p dist/dmg-mount
cp -r dist/Unrotting.app dist/dmg-mount/
hdiutil create -volname "Unrotting" \
    -srcfolder dist/dmg-mount \
    -ov -format UDZO \
    dist/Unrotting.dmg

# Cleanup
rm -rf dist/dmg-mount

echo ""
echo "====================================="
echo " Build Complete!"
echo " Output: dist/Unrotting.dmg"
echo "====================================="
echo ""
echo "To distribute:"
echo "  - Notarize with Apple: xcrun notarytool submit dist/Unrotting.dmg"
echo "  - Create distributable disk image"

# Enhanced DMG creation with app bundle
APP_BUNDLE="dist/Unrotting.app"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"
cp -r ui assets "$APP_BUNDLE/Contents/Resources/"
cp dist/UnrottingMinimal "$APP_BUNDLE/Contents/MacOS/Unrotting"
chmod +x "$APP_BUNDLE/Contents/MacOS/Unrotting"

# Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLISTEOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>Unrotting</string>
    <key>CFBundleIdentifier</key><string>org.unrotting.app</string>
    <key>CFBundleName</key><string>Unrotting</string>
    <key>CFBundleVersion</key><string>1.0.0</string>
    <key>CFBundleShortVersionString</key><string>1.0.0</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLISTEOF

# Create DMG with custom icon
hdiutil create -volname "Unrotting" -srcfolder "$APP_BUNDLE" -ov -format UDZO dist/Unrotting.dmg
