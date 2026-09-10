@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=C:\Users\harsh\AppData\Local\Programs\Python\Python314\python.exe

:menu
cls
echo ================================
echo       Unrotting Control Panel
echo ================================
echo.
echo 1. Start App (Focus Mode)
echo 2. Start Tray Only (Background)
echo 3. Set/Change Password
echo 4. Show Configuration
echo 5. Reset Statistics
echo 6. Add Task
echo 7. List Tasks
echo 8. Complete Task
echo 9. Reset Tasks & Points
echo 10. Backup Hosts File
echo 11. Restore Hosts File
echo 12. Enable Auto-Start
echo 13. Disable Auto-Start
echo 14. Create Desktop Shortcut
echo 15. Remove Shortcut
echo 0. Exit
echo.
set /p choice="Choose an option: "

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto tray
if "%choice%"=="3" goto password
if "%choice%"=="4" goto config
if "%choice%"=="5" goto reset_stats
if "%choice%"=="6" goto add_task
if "%choice%"=="7" goto list_tasks
if "%choice%"=="8" goto complete_task
if "%choice%"=="9" goto reset_tasks
if "%choice%"=="10" goto backup_hosts
if "%choice%"=="11" goto restore_hosts
if "%choice%"=="12" goto enable_autostart
if "%choice%"=="13" goto disable_autostart
if "%choice%"=="14" goto create_shortcut
if "%choice%"=="15" goto remove_shortcut
if "%choice%"=="0" goto end
goto menu

:start_app
"%PYTHON%" -m unrotting.app.main run
goto menu

:tray
"%PYTHON%" -m unrotting.app.main tray
goto menu

:password
echo.
set /p oldpw="Enter current password (leave blank if first time): "
set /p newpw="Enter new password: "
"%PYTHON%" -m unrotting.app.main password --new "%newpw%" --old "%oldpw%"
echo.
pause
goto menu

:config
"%PYTHON%" -m unrotting.app.main config
echo.
pause
goto menu

:reset_stats
"%PYTHON%" -m unrotting.app.main reset-stats
echo.
pause
goto menu

:add_task
echo.
set /p tasktitle="Enter task title: "
"%PYTHON%" -m unrotting.app.main add-task "%tasktitle%"
echo.
pause
goto menu

:list_tasks
"%PYTHON%" -m unrotting.app.main list-tasks
echo.
pause
goto menu

:complete_task
echo.
echo Available tasks:
"%PYTHON%" -m unrotting.app.main list-tasks
echo.
set /p taskid="Enter task ID to complete: "
"%PYTHON%" -m unrotting.app.main complete-task "%taskid%"
echo.
pause
goto menu

:reset_tasks
"%PYTHON%" -m unrotting.app.main reset-tasks
echo.
pause
goto menu

:backup_hosts
"%PYTHON%" -m unrotting.app.main backup-hosts
echo.
pause
goto menu

:restore_hosts
"%PYTHON%" -m unrotting.app.main restore-hosts
echo.
pause
goto menu

:enable_autostart
"%PYTHON%" -m unrotting.app.main enable-auto-start
echo.
pause
goto menu

:disable_autostart
"%PYTHON%" -m unrotting.app.main disable-auto-start
echo.
pause
goto menu

:create_shortcut
"%PYTHON%" -m unrotting.app.main create-shortcut
echo.
pause
goto menu

:remove_shortcut
"%PYTHON%" -m unrotting.app.main remove-shortcut
echo.
pause
goto menu

:end
exit
