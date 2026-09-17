#!/bin/bash
# Build Android APK for Unrotting
# This requires Linux environment with Android SDK or WSL2

set -e

echo "====================================="
echo " Building Unrotting Android APK"
echo "====================================="
echo

# Check if running in WSL/Linux
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$WSL_DISTRO_NAME" == "" ]]; then
    echo "[WARNING] This script is designed for Linux/WSL2."
    echo "On Windows, please use WSL2 or an online builder."
    echo ""
    echo "To use WSL2:"
    echo "  1. Install WSL2: wsl --install"
    echo "  2. Open WSL terminal and navigate to this directory"
    echo "  3. Run: bash scripts/build-android-apk.sh"
    exit 1
fi

# Install buildozer and dependencies
echo "Installing build dependencies..."
pip3 install --user buildozer cython kivy pywebview

# Initialize buildozer spec if not exists
if [[ ! -f "buildozer.spec" ]]; then
    echo "Initializing buildozer..."
    buildozer init
fi

# Create/update buildozer.spec
cat > buildozer.spec << 'EOF'
[app]
title = Unrotting
package.name = unrotting
package.domain = org.unrotting
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
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
log_level = 2
wm_size = 1024x768
title = Unrotting
author = Unrotting Team
package.org = org.unrotting
package.class = org.unrotting.MainActivity
android.entrypoint = org.unrotting.MainActivity
android.permissions = INTERNET,ACCESS_NETWORK_STATE

[buildozer]
# Android SDK path (adjust for your system)
sdk_dir = ~/Android/Sdk
# NDK path (adjust for your system)
ndk_dir = ~/Android/Sdk/ndk/25b
# Java path (adjust for your system)
jdk_dir = /usr/lib/jvm/java-17-openjdk-amd64
EOF

# Build the APK
echo "Building Android APK..."
buildozer android debug

if [ $? -ne 0 ]; then
    echo "[ERROR] APK build failed!"
    exit 1
fi

echo ""
echo "====================================="
echo " APK Build Complete!"
echo " Output: bin/Unrotting-1.0.0-debug.apk"
echo "====================================="
echo ""
echo "To install on device:"
echo "  adb install bin/Unrotting-1.0.0-debug.apk"
echo ""
echo "For production build, run:"
echo "  buildozer android release"

# Add APK signing configuration
if [ -f "keystore.properties" ]; then
    source keystore.properties
    buildozer android debug release
    echo "APK signed with custom keystore"
else
    echo "No keystore found, building debug APK"
    buildozer android debug
fi
