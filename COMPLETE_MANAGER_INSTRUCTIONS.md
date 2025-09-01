# FABSI Applications - Complete Deployment Instructions for Manager

## 📋 What You're Receiving

You are receiving the **FABSI Workload Management Applications** package containing:
1. **FABSI List of Services** - Service record management with filtering capabilities
2. **FABSI Project Booking** - Resource allocation and project booking management

## 📦 Package Options

### Option A: Manual Deployment Package (Recommended if you have Python)
**Folder**: `FABSI_Manual_Deployment`
- Requires Python 3.8+ on target computer
- Smaller file size, easier to transfer
- Run applications using .bat files

### Option B: Executable Package (If available)
**Folder**: `FABSI_Deployment` 
- Standalone .exe files, no Python required
- Larger file size but completely self-contained
- Double-click to run applications

## 🚀 Step-by-Step Installation

### For Manual Deployment Package (Most Common)

#### Step 1: Prerequisites
1. **Check if Python is installed**:
   - Open Command Prompt (Windows key + R, type `cmd`)
   - Type: `python --version`
   - Should show Python 3.8 or higher
   - **If not installed**: Download from [python.org](https://python.org) and install

#### Step 2: Package Transfer
1. **Copy the entire `FABSI_Manual_Deployment` folder** to your computer
2. **Recommended location**: `C:\FABSI_Apps\` or Desktop
3. **Keep all files together** - don't separate any components

#### Step 3: Initial Setup (One-time only)
1. **Navigate** to the FABSI_Manual_Deployment folder
2. **Right-click** on `Setup.bat` → "Run as administrator"
3. **Wait** for package installation to complete (2-5 minutes)
4. **Press any key** when prompted to close the window

#### Step 4: First Run Test
1. **Double-click** `Start_List_of_Services.bat`
2. **Wait** for application to load (1-2 minutes first time)
3. **Verify** you see data and dropdowns are populated
4. **Close** the application
5. **Repeat** with `Start_Project_Booking.bat`

## 📱 Daily Usage Instructions

### Starting the Applications
- **List of Services**: Double-click `Start_List_of_Services.bat`
- **Project Booking**: Double-click `Start_Project_Booking.bat`

### Basic Operations

#### FABSI List of Services
1. **Filter data** using the dropdown menus:
   - Select Project
   - Choose Technical Unit  
   - Pick Employee
   - Select Activities, Progress, etc.
2. **View filtered results** in the main grid
3. **Export to Excel** using the export button
4. **Edit data** by double-clicking any cell

#### FABSI Project Booking  
1. **Select from dropdowns**:
   - Choose Technical Unit
   - Choose Project
   - Choose Employee
2. **Automatic booking creation**: When all three are selected, matching services are automatically added
3. **Review bookings** in the grid (shows booking hours, costs, etc.)
4. **Edit any field** by double-clicking cells

## ⚠️ Important Notes

### Data and Backup
- **Critical**: All data is stored in `Database/workload.db`
- **Backup this file regularly** (daily recommended)
- **Both applications share the same data** - changes in one appear in the other

### Performance Tips
- **First startup** takes 1-2 minutes
- **Subsequent startups** are faster
- **Close applications properly** using the X button
- **Restart weekly** for best performance

### Troubleshooting
- **If apps won't start**: Run .bat files as administrator
- **If no data appears**: Wait 2-3 minutes for loading
- **If errors occur**: Close all applications and restart
- **For detailed help**: See `TROUBLESHOOTING.md` in the package

## 🔒 Security Considerations

### Antivirus
- Your antivirus may flag the applications initially
- **Add the FABSI folder to your antivirus whitelist**
- This is normal for new applications

### Windows Security
- Windows may show "Windows protected your PC" warning
- **Click "More info" → "Run anyway"**
- This happens because applications aren't digitally signed

### Data Security
- All data stays on your local computer
- No internet connection required
- No data sent to external servers

## 📞 Support Structure

### Level 1: Self-Help (Check These First)
- **QUICK_START.md** - 5-minute setup guide  
- **USER_GUIDE.md** - Complete usage instructions
- **TROUBLESHOOTING.md** - Common problem solutions

### Level 2: IT Support
- Windows application troubleshooting
- File permissions and antivirus issues
- Python installation problems

### Level 3: Application Developer
- Contact for application bugs
- Database corruption issues
- Feature requests

## 📈 Success Checklist

After installation, verify:
- [ ] Both applications start without errors
- [ ] Dropdowns contain data (projects, employees, etc.)
- [ ] Filtering works in List of Services
- [ ] Automatic booking works in Project Booking
- [ ] Data can be exported to Excel
- [ ] Changes are saved between sessions

## 🎯 Quick Reference

### File Locations
- **Applications**: `Start_List_of_Services.bat` and `Start_Project_Booking.bat`
- **Database**: `Database/workload.db` (BACKUP THIS FILE!)
- **Documentation**: `USER_GUIDE.md`, `TROUBLESHOOTING.md`

### Common Commands
- **Start**: Double-click .bat files
- **Stop**: Close using X button
- **Backup**: Copy `Database/workload.db` to safe location
- **Reset**: Close apps, restart computer, try again

### Emergency Contacts
- **Technical Issues**: Document error messages and contact IT
- **Application Bugs**: Contact development team
- **Data Loss**: Stop using immediately, restore from backup

---

## 📞 What to Do If You Have Problems

1. **Document the issue**:
   - What were you trying to do?
   - What error message appeared?
   - Take a screenshot if possible

2. **Try basic troubleshooting**:
   - Close all applications
   - Restart your computer
   - Try running as administrator

3. **Check the documentation**:
   - Look in TROUBLESHOOTING.md for your specific issue
   - Follow the step-by-step solutions

4. **Contact support**:
   - Provide the error details
   - Mention which application (List of Services or Project Booking)
   - Include your Windows version

---

**Remember**: These applications manage your organization's workload data. Treat them as business-critical software and maintain regular backups.

**Total setup time**: 10-15 minutes  
**Learning time**: 30 minutes with the user guide  
**Daily usage**: Simple and intuitive once familiar

Good luck with your FABSI applications!
