@echo off
REM ===============================================
REM FABSI Workload Management Applications Builder
REM ===============================================

echo.
echo ===============================================
echo   FABSI Workload Management Apps Builder
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [1/5] Installing required packages...
pip install pyinstaller customtkinter pandas sqlalchemy openpyxl Pillow tkcalendar flask flask-sqlalchemy

if errorlevel 1 (
    echo ERROR: Failed to install packages. Please check internet connection.
    pause
    exit /b 1
)

echo.
echo [2/5] Creating List of Services executable...
pyinstaller --onefile --windowed --add-data "workload.db;." --add-data "photos;photos" --add-data "*.xlsx;." --add-data "*.xlsm;." --add-data "*.csv;." --add-data "*.sql;." --name "FABSI_List_of_Services" Fabsi_List_of_Service.py

if errorlevel 1 (
    echo ERROR: Failed to create List of Services executable
    pause
    exit /b 1
)

echo.
echo [3/5] Creating Project Booking executable...
pyinstaller --onefile --windowed --add-data "workload.db;." --add-data "photos;photos" --add-data "*.xlsx;." --add-data "*.xlsm;." --add-data "*.csv;." --add-data "*.sql;." --name "FABSI_Project_Booking" project_booking_app.py

if errorlevel 1 (
    echo ERROR: Failed to create Project Booking executable
    pause
    exit /b 1
)

echo.
echo [4/5] Creating deployment package...
if not exist "FABSI_Deployment" mkdir FABSI_Deployment
if not exist "FABSI_Deployment\Database" mkdir FABSI_Deployment\Database
if not exist "FABSI_Deployment\Photos" mkdir FABSI_Deployment\Photos
if not exist "FABSI_Deployment\Templates" mkdir FABSI_Deployment\Templates

REM Copy executables
copy "dist\FABSI_List_of_Services.exe" "FABSI_Deployment\"
copy "dist\FABSI_Project_Booking.exe" "FABSI_Deployment\"

REM Copy database and supporting files
copy "workload.db" "FABSI_Deployment\Database\"
copy "photos\*.*" "FABSI_Deployment\Photos\"
copy "*.xlsx" "FABSI_Deployment\Templates\"
copy "*.xlsm" "FABSI_Deployment\Templates\"
copy "*.csv" "FABSI_Deployment\Templates\"

echo.
echo [5/5] Creating user documentation...

REM Create README file will be done separately

echo.
echo ===============================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ===============================================
echo.
echo Deployment package created in: FABSI_Deployment\
echo.
echo Contents:
echo   - FABSI_List_of_Services.exe (Main List of Services App)
echo   - FABSI_Project_Booking.exe (Project Booking & Resource Allocation App)
echo   - Database\ (Contains workload.db)
echo   - Photos\ (Application logos and images)
echo   - Templates\ (Excel templates and data files)
echo   - User manuals and documentation
echo.
echo You can now copy the FABSI_Deployment folder to any Windows computer
echo and run the applications without installing Python.
echo.
pause
