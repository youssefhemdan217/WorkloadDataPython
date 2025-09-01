@echo off
REM ===============================================
REM FABSI Manual Deployment Package Creator
REM (For when PyInstaller is not available)
REM ===============================================

echo.
echo ===============================================
echo   FABSI Manual Deployment Package Creator
echo ===============================================
echo.

echo This script creates a deployment package that can be run
echo on any computer with Python installed.
echo.

echo [1/3] Creating deployment package structure...
if not exist "FABSI_Manual_Deployment" mkdir FABSI_Manual_Deployment
if not exist "FABSI_Manual_Deployment\Database" mkdir FABSI_Manual_Deployment\Database
if not exist "FABSI_Manual_Deployment\Photos" mkdir FABSI_Manual_Deployment\Photos
if not exist "FABSI_Manual_Deployment\Templates" mkdir FABSI_Manual_Deployment\Templates
if not exist "FABSI_Manual_Deployment\Scripts" mkdir FABSI_Manual_Deployment\Scripts

echo [2/3] Copying application files...
REM Copy Python scripts
copy "Fabsi_List_of_Service.py" "FABSI_Manual_Deployment\Scripts\"
copy "project_booking_app.py" "FABSI_Manual_Deployment\Scripts\"
copy "requirements.txt" "FABSI_Manual_Deployment\"

REM Copy database and supporting files
copy "workload.db" "FABSI_Manual_Deployment\Database\"
if exist "photos\*.*" copy "photos\*.*" "FABSI_Manual_Deployment\Photos\"
if exist "*.xlsx" copy "*.xlsx" "FABSI_Manual_Deployment\Templates\"
if exist "*.xlsm" copy "*.xlsm" "FABSI_Manual_Deployment\Templates\"
if exist "*.csv" copy "*.csv" "FABSI_Manual_Deployment\Templates\"

REM Copy documentation
copy "USER_GUIDE.md" "FABSI_Manual_Deployment\"
copy "QUICK_START.md" "FABSI_Manual_Deployment\"
copy "TROUBLESHOOTING.md" "FABSI_Manual_Deployment\"
copy "MANAGER_DEPLOYMENT_GUIDE.md" "FABSI_Manual_Deployment\"

echo [3/3] Creating launcher scripts...

REM Create launcher for List of Services
(
echo @echo off
echo echo Starting FABSI List of Services...
echo cd /d "%%~dp0Scripts"
echo python Fabsi_List_of_Service.py
echo pause
) > "FABSI_Manual_Deployment\Start_List_of_Services.bat"

REM Create launcher for Project Booking
(
echo @echo off
echo echo Starting FABSI Project Booking...
echo cd /d "%%~dp0Scripts"
echo python project_booking_app.py
echo pause
) > "FABSI_Manual_Deployment\Start_Project_Booking.bat"

REM Create setup script
(
echo @echo off
echo echo FABSI Applications Setup
echo echo ========================
echo echo.
echo echo Installing required Python packages...
echo pip install -r requirements.txt
echo echo.
echo echo Setup complete! You can now run the applications using:
echo echo - Start_List_of_Services.bat
echo echo - Start_Project_Booking.bat
echo echo.
echo pause
) > "FABSI_Manual_Deployment\Setup.bat"

REM Create README for manual deployment
(
echo # FABSI Applications - Manual Deployment Package
echo.
echo ## Requirements
echo - Python 3.8+ installed on the target computer
echo - Internet connection for initial setup
echo.
echo ## Installation Steps
echo 1. Copy this entire FABSI_Manual_Deployment folder to the target computer
echo 2. Run Setup.bat to install required packages
echo 3. Use Start_List_of_Services.bat or Start_Project_Booking.bat to run the applications
echo.
echo ## Package Contents
echo - Scripts/ - Python application files
echo - Database/ - SQLite database with all data
echo - Photos/ - Application logos and images
echo - Templates/ - Excel templates and data files
echo - Documentation files - User guides and troubleshooting
echo.
echo ## For Computers WITHOUT Python
echo You will need to:
echo 1. Install Python 3.8+ from python.org
echo 2. Run Setup.bat to install packages
echo 3. Then use the Start_*.bat files to run applications
echo.
echo See USER_GUIDE.md for complete usage instructions.
) > "FABSI_Manual_Deployment\README.md"

echo.
echo ===============================================
echo   MANUAL DEPLOYMENT PACKAGE CREATED!
echo ===============================================
echo.
echo Package location: FABSI_Manual_Deployment\
echo.
echo Contents:
echo   - Start_List_of_Services.bat (Run List of Services)
echo   - Start_Project_Booking.bat (Run Project Booking)
echo   - Setup.bat (Install Python packages)
echo   - Scripts\ (Python application files)
echo   - Database\ (SQLite database)
echo   - Photos\ (Images and logos)
echo   - Templates\ (Excel files)
echo   - Documentation files
echo.
echo INSTRUCTIONS FOR YOUR MANAGER:
echo 1. Copy the FABSI_Manual_Deployment folder to the target computer
echo 2. Ensure Python 3.8+ is installed
echo 3. Run Setup.bat once to install packages
echo 4. Use Start_*.bat files to run the applications
echo.
echo Note: This package requires Python to be installed on the target computer.
echo For standalone executables, PyInstaller would need to be installed first.
echo.
pause
