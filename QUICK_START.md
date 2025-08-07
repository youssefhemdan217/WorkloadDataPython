# FABSI Application - Quick Start Guide

## For Developers (Building the Executable)

### Option 1: Automated Build (Easiest)
1. Open Command Prompt in your project folder
2. Run: `build_deployment.bat`
3. Wait for the process to complete
4. Find your deployment package in the `FABSI_Deployment` folder

### Option 2: Manual Build
1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller --onefile --windowed --add-data "workload.db;." --add-data "photos;photos" --name "FABSI_List_of_Service" Fabsi_List_of_Service.py`
3. Find executable in `dist` folder

## For End Users (Installing the Application)

### Method 1: Simple Copy
1. Copy the entire application folder to your computer
2. Double-click `FABSI_List_of_Service.exe` to run

### Method 2: Proper Installation
1. Copy the application files to your computer
2. Run `install_fabsi.bat` as Administrator
3. Follow the installation prompts
4. Use desktop shortcut to run the application

## Files You Need to Distribute

### Essential Files:
- `FABSI_List_of_Service.exe` (Main application)
- `workload.db` (Database file)
- `photos/` folder (Contains logos)

### Optional Files:
- `install_fabsi.bat` (Installation script)
- `README.md` or user manual

## Common Issues & Solutions

### Issue: "Database not found"
**Solution:** Ensure `workload.db` is in the same folder as the .exe file

### Issue: "Images not loading"
**Solution:** Ensure the `photos` folder is in the same directory as the .exe

### Issue: Antivirus blocks the application
**Solution:** Add the application folder to antivirus exclusions

### Issue: Application won't start
**Solution:** Try running as Administrator

## Network Deployment

### For IT Administrators:
1. Place application on shared network drive
2. Create group policy to deploy shortcuts
3. Or use the provided installation script via login script

### Example Network Structure:
```
\\server\shared\FABSI\
├── FABSI_List_of_Service.exe
├── workload.db
├── photos\
└── install_fabsi.bat
```

## Database Options

### Current Setup (Recommended for small teams):
- Each user has their own database copy
- Simple deployment, no network issues

### Shared Database Option:
- Place database on shared network drive
- Multiple users access same data
- Requires network connectivity

## Support

If you encounter issues:
1. Check this guide first
2. Verify all files are present
3. Try running as Administrator
4. Contact IT support with specific error messages

---

**Last Updated:** [Today's Date]
**Version:** 1.0
