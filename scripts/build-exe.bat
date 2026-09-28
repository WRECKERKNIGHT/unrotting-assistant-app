@echo off
cd /d "%~dp0\.."

echo =====================================
echo  Building Unrotting EXE
echo =====================================
echo.

:: Check Python
set PYTHON=C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe
if not exist "%PYTHON%" (
    echo [ERROR] Python not found at: %PYTHON%
    pause
    exit /b 1
)

:: Install PyInstaller if needed
"%PYTHON%" -m pip install pyinstaller --quiet

:: Clean previous builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: Build the executable
echo Building executable...
"%PYTHON%" -m PyInstaller --onefile ^
    --name Unrotting ^
    --add-data "ui;ui" ^
    --add-data "assets;assets" ^
    --hidden-import=win32gui ^
    --hidden-import=win32con ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --collect-all pywebview ^
    unrotting.app.__main__

if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo =====================================
echo  Build Complete!
echo  Output: dist\Unrotting.exe
echo =====================================
echo.
echo To run:
echo   dist\Unrotting.exe
echo.
echo To install as service/autorun, copy to:
echo   C:\Program Files\Unrotting\Unrotting.exe
pause
:: Verify build output
if exist dist\UnrottingMinimal.exe (
    echo [SUCCESS] Build complete!
    dir dist\*.exe
) else (
    echo [ERROR] Build failed - executable not found
    exit /b 1
)

:: Create SHA256 checksum
powershell -Command "Get-FileHash dist\UnrottingMinimal.exe -Algorithm SHA256 | Format-Table"
