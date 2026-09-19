@echo off
echo Installing Unrotting...
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Please run as Administrator
    pause
    exit /b 1
)

:: Install to Program Files
set INSTALL_DIR="C:\Program Files\Unrotting"
if not exist %INSTALL_DIR% mkdir %INSTALL_DIR%
copy dist\UnrottingMinimal.exe %INSTALL_DIR%\
copy ui %INSTALL_DIR%\
copy assets %INSTALL_DIR%\

:: Create shortcut
set SHORTCUT="%USERPROFILE%\Desktop\Unrotting.lnk"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut($SHORTCUT); $Shortcut.TargetPath = '%INSTALL_DIR%\UnrottingMinimal.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo Run from Desktop shortcut or:
echo   cd %INSTALL_DIR%
echo   UnrottingMinimal.exe
pause
