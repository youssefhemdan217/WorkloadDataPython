# FABSI Applications - Troubleshooting Guide

## 🔧 Common Issues and Solutions

### Application Startup Issues

#### Problem: "Application won't start" or "Nothing happens when double-clicking"
**Solutions**:
1. **Run as Administrator**:
   - Right-click on the .exe file
   - Select "Run as administrator"
   - Click "Yes" if prompted by Windows

2. **Check Antivirus**:
   - Your antivirus might be blocking the application
   - Add the FABSI_Deployment folder to your antivirus whitelist
   - Temporarily disable real-time protection and try again

3. **Check File Permissions**:
   - Ensure you have read/write access to the folder
   - Try moving the folder to a different location (e.g., Desktop)

#### Problem: "Application starts but crashes immediately"
**Solutions**:
1. **Check Database File**:
   - Ensure `Database/workload.db` exists
   - File should be around 1-50MB in size
   - If missing, restore from backup

2. **Check Dependencies**:
   - Make sure all folders (Database, Photos) are present
   - Don't separate the .exe files from supporting folders

### Data Loading Issues

#### Problem: "No data appears in the application"
**Solutions**:
1. **Wait for Loading**:
   - First startup can take 1-2 minutes
   - Look for "Updated totals" or loading messages
   - Don't interact with the app until loading completes

2. **Check Database**:
   - Navigate to Database/workload.db
   - Right-click → Properties → should show file size > 0 bytes
   - If empty, restore from backup

3. **Reset Filters**:
   - Try clearing all dropdown selections
   - Use "Clear All Filters" button if available

#### Problem: "Some dropdowns are empty"
**Solutions**:
1. **Database Integrity**:
   - Close the application
   - Restart the application
   - Wait for full data loading

2. **Data Dependency**:
   - Some dropdowns depend on others
   - Try selecting items in order: Project → Technical Unit → Employee

### Performance Issues

#### Problem: "Application is very slow"
**Solutions**:
1. **System Resources**:
   - Close other applications to free up RAM
   - Ensure at least 1GB free disk space
   - Restart your computer if necessary

2. **Database Size**:
   - If database is very large (>100MB), consider archiving old data
   - Use filters to reduce displayed data

3. **Application Reset**:
   - Close the application completely
   - Wait 10 seconds
   - Restart the application

#### Problem: "Application freezes or becomes unresponsive"
**Solutions**:
1. **Wait it Out**:
   - Large operations might take time
   - Wait 2-3 minutes before taking action

2. **Force Close and Restart**:
   - Press Ctrl+Alt+Delete → Task Manager
   - Find the FABSI application
   - Click "End Task"
   - Restart the application

### Database and Data Issues

#### Problem: "Changes are not being saved"
**Solutions**:
1. **File Permissions**:
   - Ensure the Database folder is not read-only
   - Right-click Database folder → Properties → uncheck "Read-only"

2. **Database Lock**:
   - Close all instances of both applications
   - Wait 30 seconds
   - Restart only one application at a time

#### Problem: "Error messages about database corruption"
**Solutions**:
1. **Immediate Action**:
   - Stop using the application immediately
   - Don't make any more changes

2. **Restore from Backup**:
   - Navigate to your backup location
   - Copy the backup workload.db file
   - Replace the current Database/workload.db file
   - Restart the application

3. **If No Backup Available**:
   - Try restarting the application
   - If still corrupted, contact technical support

### Display and Interface Issues

#### Problem: "Text is too small to read"
**Solutions**:
1. **Windows Display Scaling**:
   - Right-click desktop → Display settings
   - Change scaling to 125% or 150%
   - Restart the applications

2. **Application Window**:
   - Maximize the application window
   - Try adjusting column widths by dragging borders

#### Problem: "Interface elements are cut off"
**Solutions**:
1. **Screen Resolution**:
   - Ensure minimum 1366x768 resolution
   - Use 1920x1080 for best experience

2. **Window Management**:
   - Maximize the application window
   - Use Windows key + Up arrow to maximize

### Network and File Access Issues

#### Problem: "Permission denied" errors
**Solutions**:
1. **Administrative Rights**:
   - Run the application as administrator
   - Ensure you have write permissions to the folder

2. **Folder Location**:
   - Don't run from network drives
   - Copy to local drive (C:\ or D:\)
   - Avoid running from USB drives if possible

#### Problem: "File in use" or "Database locked" errors
**Solutions**:
1. **Close All Instances**:
   - Make sure both applications are completely closed
   - Check Task Manager for any remaining processes

2. **Restart Computer**:
   - If lock persists, restart your computer
   - Try running only one application at a time

## 🆘 Emergency Procedures

### Complete Application Reset
If all else fails:
1. Close all FABSI applications
2. Backup your current Database folder
3. Restart your computer
4. Try running just one application
5. If it works, try the second application

### Data Recovery
If you lose data:
1. **Don't panic** - check your backups first
2. **Stop using the application** immediately
3. **Restore from most recent backup**:
   - Copy backup workload.db to Database/workload.db
   - Restart the application
4. **Contact support** if no backups are available

### Clean Installation
If applications are completely broken:
1. Create backup of Database/workload.db
2. Download fresh FABSI_Deployment package
3. Extract to new location
4. Copy your backed-up workload.db to new Database folder
5. Test the applications

## 📋 Diagnostic Information

When contacting support, please provide:

### System Information
- Windows version (Windows 10/11)
- Available RAM and disk space
- Antivirus software name

### Error Details
- Exact error message text
- When the error occurs
- What you were doing when it happened
- Screenshots of error messages

### Application State
- Which application has the issue
- Whether both apps have the same problem
- Database file size (Database/workload.db properties)
- When the issue started

## 🔍 Prevention Tips

### Avoid Common Issues
1. **Regular Backups**: Backup Database folder weekly
2. **Don't Move Files**: Keep all files in the FABSI_Deployment folder together
3. **Close Properly**: Always close applications using the X button
4. **One at a Time**: When troubleshooting, run only one application
5. **Admin Rights**: Run as administrator if you have permission issues

### Best Practices
1. **Dedicated Folder**: Keep FABSI applications in their own folder
2. **Regular Restarts**: Restart applications daily
3. **System Maintenance**: Keep your computer updated and clean
4. **Monitor Size**: Watch database size - archive if it gets very large

---

*If none of these solutions work, document the exact error and contact technical support with the diagnostic information listed above.*
