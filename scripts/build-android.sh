#!/bin/bash
# Build Android APK for Unrotting using Buildozer/Kivy
# Note: This requires a Linux environment with Android SDK

set -e

echo "====================================="
echo " Building Unrotting Android APK"
echo "====================================="
echo

# Check if running in WSL/Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "[WARNING] This script is designed for Linux/WSL."
    echo "On Windows, you'll need to use WSL2 or an online service."
    echo ""
    echo "Alternative: Use a cloud builder like:"
    echo "  https://github.com/kivy/buildozer"
fi

# Install buildozer if needed
pip install buildozer cython kivy

# Initialize buildozer spec if not exists
if [[ ! -f "buildozer.spec" ]]; then
    buildozer init
fi

# Edit buildozer.spec for Android
cat > buildozer.spec << 'EOF'
[app]
title = Unrotting
package.name = unrotting
package.domain = org.unrotting
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,pywebview,pywin32,pystray,Pillow,psutil
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
p4a.bootstrap = webview
presplash.files = assets/icon.png
icon.files = assets/icon.png
orientation = portrait
fullscreen = 0
EOF

# Build
echo "Building APK..."
buildozer android debug

echo ""
echo "====================================="
echo " APK Built!"
echo " Output: bin/Unrotting-1.0.0-debug.apk"
echo "====================================="
