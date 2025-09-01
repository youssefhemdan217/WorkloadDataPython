@echo off
echo Starting Project Booking & Resource Allocation Application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "workload.db" (
    echo Warning: workload.db not found
    echo The application will create the extended schema
    echo.
)

if not exist "project_booking_app.py" (
    echo Error: project_booking_app.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM Run the application
echo Launching Project Booking Application...
python project_booking_app.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo Error: Application exited with error code %ERRORLEVEL%
    echo Check project_booking_app.log for details
    pause
)

echo.
echo Application closed.
pause
