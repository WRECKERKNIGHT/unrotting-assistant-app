#!/bin/bash
# Build macOS DMG for Unrotting
# This script should be run on macOS

set -e

echo "====================================="
echo " Building Unrotting macOS DMG"
echo "====================================="
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "[ERROR] This script must be run on macOS."
    echo "Use WSL2 or a Mac build environment."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install Python 3.10+."
    exit 1
fi

echo "Python version: $(python3 --version)"

# Install PyInstaller if needed
echo "Installing PyInstaller..."
pip3 install pyinstaller --quiet

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Create app bundle structure
echo "Creating app bundle..."
APP_NAME="Unrotting"
APP_BUNDLE="dist/${APP_NAME}.app"
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

# Build the executable
echo "Building executable..."
python3 -m PyInstaller --onefile \
    --name "${APP_NAME}" \
    --add-data "ui:ui" \
    --add-data "assets:assets" \
    --hidden-import=macos \
    --collect-all pywebview \
    --osx-bundle-identifier "org.unrotting.app" \
    app/__main__.py

# Move the executable into the bundle
cp dist/${APP_NAME} "${APP_BUNDLE}/Contents/MacOS/"
rm -f dist/${APP_NAME}

# Copy assets and UI
cp -r ui "${APP_BUNDLE}/Contents/Resources/"
cp -r assets "${APP_BUNDLE}/Contents/Resources/"

# Copy Python scripts
cp -r app "${APP_BUNDLE}/Contents/Resources/app"

# Create Info.plist
cat > "${APP_BUNDLE}/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Unrotting</string>
    <key>CFBundleIdentifier</key>
    <string>org.unrotting.app</string>
    <key>CFBundleName</key>
    <string>Unrotting</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSBackgroundOnly</key>
    <false/>
    <key>NSMainNibFile</key>
    <string></string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
</dict>
</plist>
EOF

# Add application icon
if [ -f "assets/icon.png" ]; then
    cp assets/icon.png "${APP_BUNDLE}/Contents/Resources/AppIcon.icns"
    # Convert PNG to ICNS (requires ImageMagick)
    if command -v convert &> /dev/null; then
        mkdir -p "${APP_BUNDLE}/Contents/Resources"
        convert assets/icon.png -resize 1024x1024 "${APP_BUNDLE}/Contents/Resources/icon_1024x1024.png"
        convert assets/icon.png -resize 512x512 "${APP_BUNDLE}/Contents/Resources/icon_512x512.png"
        convert assets/icon.png -resize 256x256 "${APP_BUNDLE}/Contents/Resources/icon_256x256.png"
        convert assets/icon.png -resize 128x128 "${APP_BUNDLE}/Contents/Resources/icon_128x128.png"
        convert assets/icon.png -resize 32x32 "${APP_BUNDLE}/Contents/Resources/icon_32x32.png"
        convert assets/icon.png -resize 16x16 "${APP_BUNDLE}/Contents/Resources/icon_16x16.png"
    fi
fi

# Make executable
chmod +x "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"

# Create DMG
echo "Creating DMG..."
DMG_NAME="Unrotting.dmg"
STAGING_DIR="dist/staging"
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}"
cp -r "${APP_BUNDLE}" "${STAGING_DIR}/"

# Create symlink to Applications
ln -s /Applications "${STAGING_DIR}/Applications"

hdiutil create \
    -volname "${APP_NAME}" \
    -srcfolder "${STAGING_DIR}" \
    -ov \
    -format UDZO \
    "dist/${DMG_NAME}"

# Cleanup
rm -rf "${STAGING_DIR}"

echo ""
echo "====================================="
echo " Build Complete!"
echo " Output: dist/${DMG_NAME}"
echo "====================================="
echo ""
echo "To sign and notarize (optional):"
echo "  codesign --sign 'Developer ID' --deep dist/${APP_NAME}.app"
echo "  xcrun notarytool submit dist/${DMG_NAME} --apple-id YOUR@email --team-id TEAMID"
