@echo off
echo =========================================
echo FABSI Application Deployment Builder
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first and try again
    pause
    exit /b 1
)

echo Python found! Proceeding with deployment...
echo.

REM Install required packages
echo Installing PyInstaller and dependencies...
pip install pyinstaller auto-py-to-exe
pip install -r requirements.txt

echo.
echo Creating executable...
echo This may take several minutes...

REM Create the executable
pyinstaller --onefile --windowed --add-data "workload.db;." --add-data "photos;photos" --name "FABSI_List_of_Service" --clean --noconfirm Fabsi_List_of_Service.py

if exist "dist\FABSI_List_of_Service.exe" (
    echo.
    echo ========================================
    echo SUCCESS! Executable created successfully
    echo ========================================
    echo.
    echo Location: dist\FABSI_List_of_Service.exe
    echo.
    echo Creating deployment package...
    
    REM Create deployment folder
    mkdir "FABSI_Deployment" 2>nul
    copy "dist\FABSI_List_of_Service.exe" "FABSI_Deployment\"
    copy "workload.db" "FABSI_Deployment\"
    xcopy /E /Y "photos" "FABSI_Deployment\photos\"
    
    echo.
    echo Deployment package created in: FABSI_Deployment\
    echo.
    echo You can now copy the FABSI_Deployment folder to any Windows computer
    echo and run FABSI_List_of_Service.exe without needing Python installed!
    echo.
) else (
    echo.
    echo ERROR: Failed to create executable
    echo Check the console output above for error details
    echo.
)

echo.
echo Press any key to exit...
pause >nul
