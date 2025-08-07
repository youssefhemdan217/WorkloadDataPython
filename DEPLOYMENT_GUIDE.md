# FABSI - List of Service Application Deployment Guide

## Overview
This guide will help you deploy the FABSI List of Service application on company workstations so users can run it without needing Python installed or seeing the source code.

## Prerequisites
- Windows workstation with administrator privileges
- Python 3.8+ installed on the development machine (where you'll create the executable)
- Internet connection for downloading dependencies

---

## Part 1: Preparing the Application for Deployment

### Step 1: Install Required Packages
Open Command Prompt or PowerShell as administrator and navigate to your project folder:

```bash
cd "d:\Saipem\Workload Excel\pythonApp\WorkloadDataPython"
```

Install PyInstaller and required packages:
```bash
pip install pyinstaller auto-py-to-exe
pip install -r requirements.txt
```

### Step 2: Test Your Application
Before creating the executable, make sure your application runs correctly:
```bash
python Fabsi_List_of_Service.py
```

### Step 3: Create Application Icon (Optional)
If you have a company logo (.ico file), place it in the project folder. If not, we'll create the executable without a custom icon.

---

## Part 2: Creating the Executable

### Method 1: Using PyInstaller (Command Line)

1. **Create the executable:**
```bash
pyinstaller --onefile --windowed --add-data "workload.db;." --add-data "photos;photos" --name "FABSI_List_of_Service" Fabsi_List_of_Service.py
```

**Command explanation:**
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (GUI only)
- `--add-data "workload.db;."`: Includes the database file
- `--add-data "photos;photos"`: Includes the photos folder with logos
- `--name "FABSI_List_of_Service"`: Sets the executable name

2. **If you have an icon file:**
```bash
pyinstaller --onefile --windowed --icon=your_icon.ico --add-data "workload.db;." --add-data "photos;photos" --name "FABSI_List_of_Service" Fabsi_List_of_Service.py
```

### Method 2: Using Auto-Py-to-Exe (GUI Tool)

1. **Launch the GUI tool:**
```bash
auto-py-to-exe
```

2. **Configure the settings:**
   - **Script Location:** Browse and select `Fabsi_List_of_Service.py`
   - **Onefile:** Select "One File"
   - **Console Window:** Select "Window Based (hide the console)"
   - **Icon:** Browse and select your .ico file (optional)
   
3. **Add Additional Files:**
   - Click "Add Files" and add `workload.db`
   - Click "Add Folder" and add the `photos` folder
   
4. **Click "Convert .py to .exe"**

---

## Part 3: Testing the Executable

### Step 1: Locate the Executable
After PyInstaller finishes, you'll find your executable in:
```
d:\Saipem\Workload Excel\pythonApp\WorkloadDataPython\dist\FABSI_List_of_Service.exe
```

### Step 2: Test the Executable
1. Copy the entire `dist` folder to a test location
2. Double-click `FABSI_List_of_Service.exe`
3. Verify all features work:
   - Database connections
   - Image loading (logos)
   - Excel import/export
   - All GUI functions

---

## Part 4: Preparing for Company-Wide Deployment

### Step 1: Create Deployment Package
Create a folder structure like this:
```
FABSI_Application/
├── FABSI_List_of_Service.exe
├── workload.db
├── photos/
│   ├── fabsi_logo.png
│   └── saipem_logo.png
├── User_Manual.pdf (optional)
└── Installation_Instructions.txt
```

### Step 2: Create Installation Instructions
Create `Installation_Instructions.txt`:

```
FABSI - List of Service Application
Installation Instructions

1. Copy the entire FABSI_Application folder to your desired location
   Recommended: C:\Program Files\FABSI\

2. Create a desktop shortcut:
   - Right-click on FABSI_List_of_Service.exe
   - Select "Create shortcut"
   - Move the shortcut to your desktop

3. Double-click the application to run

Note: No Python installation required!
For support, contact: [Your IT Support Email]
```

---

## Part 5: Network Deployment Options

### Option 1: Shared Network Drive
1. Place the application folder on a shared network drive
2. Users can run directly from the network location
3. Centralized updates - update once, affects all users

### Option 2: Local Installation via Script
Create a batch file `install_fabsi.bat`:

```batch
@echo off
echo Installing FABSI Application...

REM Create application directory
mkdir "C:\Program Files\FABSI" 2>nul

REM Copy application files
xcopy /E /Y "\\network-path\FABSI_Application\*" "C:\Program Files\FABSI\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\FABSI.lnk'); $Shortcut.TargetPath = 'C:\Program Files\FABSI\FABSI_List_of_Service.exe'; $Shortcut.Save()"

echo Installation complete!
pause
```

### Option 3: MSI Installer (Advanced)
For professional deployment, consider creating an MSI installer using tools like:
- Inno Setup (free)
- NSIS (free)
- Advanced Installer
- WiX Toolset

---

## Part 6: Database Considerations

### Database Location Options:

#### Option 1: Local Database (Current Setup)
- Each user has their own database
- No data sharing between users
- Simple deployment

#### Option 2: Shared Network Database
1. Place `workload.db` on a shared network drive
2. Modify the database path in your code:
```python
db_path = r"\\shared-server\FABSI\workload.db"
```
3. Rebuild the executable

#### Option 3: Central Database Server
For enterprise deployment, consider:
- SQL Server
- PostgreSQL
- MySQL

---

## Part 7: Troubleshooting Common Issues

### Issue 1: "Failed to execute script" error
**Solution:** Include all dependencies in the PyInstaller command
```bash
pyinstaller --onefile --windowed --hidden-import=sqlalchemy.sql.default_comparator --add-data "workload.db;." --add-data "photos;photos" Fabsi_List_of_Service.py
```

### Issue 2: Database not found
**Solution:** Ensure database path is relative and database is included in build
```python
# In your code, use relative path:
db_path = os.path.join(os.path.dirname(__file__), 'workload.db')
```

### Issue 3: Images not loading
**Solution:** Ensure images are included and paths are correct
```bash
--add-data "photos;photos"
```

### Issue 4: Slow startup
**Solution:** Use `--exclude-module` to remove unused modules
```bash
pyinstaller --onefile --windowed --exclude-module matplotlib --exclude-module numpy Fabsi_List_of_Service.py
```

---

## Part 8: Security Considerations

### For Company Deployment:
1. **Antivirus:** Your IT department may need to whitelist the .exe file
2. **Code Signing:** Consider signing the executable for trust
3. **User Permissions:** Ensure users have write access to database location
4. **Backup:** Implement database backup strategy

---

## Part 9: Updates and Maintenance

### Updating the Application:
1. Make changes to your Python code
2. Rebuild the executable using the same PyInstaller command
3. Replace the old .exe file with the new one
4. Test thoroughly before company-wide deployment

### Version Control:
- Keep track of application versions
- Maintain changelog for user communication
- Consider automatic update mechanisms for future versions

---

## Support and Contact

For technical support or questions:
- IT Department: [Your IT Email]
- Developer: [Your Email]
- Documentation: [Link to additional docs]

---

## Appendix: Complete PyInstaller Command Reference

### Basic Command:
```bash
pyinstaller --onefile --windowed Fabsi_List_of_Service.py
```

### Complete Command with All Options:
```bash
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=fabsi_icon.ico ^
    --add-data "workload.db;." ^
    --add-data "photos;photos" ^
    --name "FABSI_List_of_Service" ^
    --clean ^
    --noconfirm ^
    Fabsi_List_of_Service.py
```

### For Debug Version (shows console):
```bash
pyinstaller --onefile --console --add-data "workload.db;." --add-data "photos;photos" --name "FABSI_List_of_Service_Debug" Fabsi_List_of_Service.py
```

---

*Last updated: [Current Date]*
*Version: 1.0*
