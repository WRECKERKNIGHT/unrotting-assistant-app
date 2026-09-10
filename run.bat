@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as Administrator. Some features may not work.
    echo         Please right-click and select "Run as administrator".
    echo.
)

:: Check Python
set PYTHON=C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe
if not exist "%PYTHON%" (
    echo [ERROR] Python not found at expected path.
    echo Please install Python 3.14 or update this path in run.bat
    pause
    exit /b 1
)

:: Check/install dependencies
"%PYTHON%" -m pip install -r requirements.txt --quiet 2>nul

:: Run the app
echo Starting Unrotting...
"%PYTHON%" -m unrotting.app.main run

echo.
echo App closed. To stop blocking, run:
echo   python -m unrotting.app.main restore-hosts
pause
