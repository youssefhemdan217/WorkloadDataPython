@echo off
title FABSI Application Installer

echo ==========================================
echo FABSI - List of Service Application
echo Installation Script
echo ==========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator... Good!
) else (
    echo WARNING: Not running as Administrator
    echo Some installation steps may fail
    echo Right-click and "Run as Administrator" for best results
)

echo.
echo Choose installation location:
echo 1. Program Files (Recommended - requires admin)
echo 2. User folder (No admin required)
echo 3. Custom location
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    set "install_path=C:\Program Files\FABSI"
) else if "%choice%"=="2" (
    set "install_path=%USERPROFILE%\FABSI"
) else if "%choice%"=="3" (
    set /p install_path="Enter full path: "
) else (
    echo Invalid choice. Using default location.
    set "install_path=%USERPROFILE%\FABSI"
)

echo.
echo Installing to: %install_path%
echo.

REM Create installation directory
echo Creating installation directory...
mkdir "%install_path%" 2>nul

REM Copy application files
echo Copying application files...
copy "FABSI_List_of_Service.exe" "%install_path%\" >nul
if exist "workload.db" copy "workload.db" "%install_path%\" >nul
if exist "photos" xcopy /E /Y "photos" "%install_path%\photos\" >nul

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\FABSI List of Service.lnk'); $Shortcut.TargetPath = '%install_path%\FABSI_List_of_Service.exe'; $Shortcut.WorkingDirectory = '%install_path%'; $Shortcut.Description = 'FABSI List of Service Application'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FABSI" 2>nul
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\FABSI\FABSI List of Service.lnk'); $Shortcut.TargetPath = '%install_path%\FABSI_List_of_Service.exe'; $Shortcut.WorkingDirectory = '%install_path%'; $Shortcut.Description = 'FABSI List of Service Application'; $Shortcut.Save()"

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Application installed to: %install_path%
echo Desktop shortcut created: FABSI List of Service
echo Start menu shortcut created: Programs > FABSI
echo.
echo You can now run the application from:
echo - Desktop shortcut
echo - Start menu
echo - Or directly from: %install_path%\FABSI_List_of_Service.exe
echo.

REM Ask if user wants to run the application now
set /p run_now="Do you want to run the application now? (y/n): "
if /i "%run_now%"=="y" (
    echo Starting FABSI List of Service...
    start "" "%install_path%\FABSI_List_of_Service.exe"
)

echo.
echo Press any key to exit...
pause >nul
