# FABSI Workload Management Applications
## Installation and User Guide

---

## 📦 Package Contents

Your deployment package contains:

```
FABSI_Deployment/
├── FABSI_List_of_Services.exe          # Main List of Services Application
├── FABSI_Project_Booking.exe            # Project Booking & Resource Allocation
├── Database/
│   └── workload.db                      # SQLite Database (contains all data)
├── Photos/
│   ├── fabsi_logo.png                   # FABSI Logo
│   └── saipem_logo.png                  # Saipem Logo
├── Templates/
│   ├── FABSI_List of Service HO_Master_R1.xlsx  # Excel Template
│   ├── test.xlsm                        # Excel Test File
│   └── excel_booking_data_for_import.csv # Import Data Template
├── USER_GUIDE.md                        # This file
├── QUICK_START.md                       # Quick start instructions
└── TROUBLESHOOTING.md                   # Common issues and solutions
```

---

## 🚀 Quick Start Instructions

### System Requirements
- **Operating System**: Windows 10 or Windows 11
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 100MB free disk space
- **Display**: 1366x768 minimum resolution (1920x1080 recommended)

### Installation Steps
1. **Extract the package** to any folder on your computer (e.g., `C:\FABSI_Apps\`)
2. **No additional installation required** - the applications are portable
3. **Keep all files together** - do not separate the executable files from the Database and Photos folders

---

## 🎯 Application Overview

### FABSI List of Services (`FABSI_List_of_Services.exe`)
**Purpose**: Manage and view service records with filtering and reporting capabilities

**Key Features**:
- Service record management and filtering
- Project, employee, and technical unit filtering
- Excel export functionality
- Real-time data updates
- Estimated hours tracking (internal and external)

### FABSI Project Booking (`FABSI_Project_Booking.exe`)
**Purpose**: Resource allocation and project booking management

**Key Features**:
- Project booking creation and management
- Employee assignment to projects
- Resource allocation tracking
- Booking hours management (internal, external, extra)
- Comprehensive reporting and data export

---

## 📋 How to Use the Applications

### Starting the Applications

#### Method 1: Double-Click
1. Navigate to the `FABSI_Deployment` folder
2. Double-click on `FABSI_List_of_Services.exe` or `FABSI_Project_Booking.exe`
3. The application will start automatically

#### Method 2: Create Desktop Shortcuts
1. Right-click on the executable file
2. Select "Create shortcut"
3. Move the shortcut to your desktop
4. Rename it to "FABSI List of Services" or "FABSI Project Booking"

### Using FABSI List of Services

#### Main Features:
1. **Filter by Dropdowns**:
   - Select Project from dropdown
   - Select Technical Unit
   - Select Employee
   - Select Activities, Progress, etc.

2. **View Service Records**:
   - Services are displayed in a grid format
   - Each record shows: Stick-Built, Module, Document Number, Activities, Title, Department, etc.
   - Estimated Internal and External hours are displayed

3. **Export to Excel**:
   - Click "Open Excel File" button
   - Data will be exported to Excel format
   - You can save the file to any location

4. **Add/Edit Records**:
   - Double-click on any cell to edit
   - Changes are saved automatically to the database

#### Step-by-Step Usage:
1. **Start the application** by double-clicking `FABSI_List_of_Services.exe`
2. **Wait for loading** - you'll see "Updated totals" messages in the background
3. **Use filters** to narrow down the services you want to view
4. **Review data** in the main grid
5. **Export if needed** using the Excel export button

### Using FABSI Project Booking

#### Main Features:
1. **Resource Allocation**:
   - Assign employees to projects
   - Set booking hours (internal, accepted, extra)
   - Track project progress

2. **Booking Management**:
   - Create new project bookings
   - Edit existing bookings
   - Delete or modify assignments

3. **Automatic Service Integration**:
   - When you select Technical Unit + Project + Employee, the system automatically finds matching services
   - Estimated hours from services are mapped to booking hours

#### Step-by-Step Usage:
1. **Start the application** by double-clicking `FABSI_Project_Booking.exe`
2. **Wait for data loading** - you'll see loading messages
3. **Select from dropdowns**:
   - Choose Technical Unit
   - Choose Project  
   - Choose Employee
4. **Automatic record creation**: When all three are selected, matching services are automatically added to project bookings
5. **Review and edit**: Check the booking grid and edit any fields as needed
6. **Save changes**: All changes are automatically saved to the database

---

## 🔄 Data Management

### Database Location
- The main database file is located at: `Database/workload.db`
- **IMPORTANT**: Do not delete or move this file - it contains all your data

### Backup Recommendations
1. **Regular backups**: Copy the entire `FABSI_Deployment` folder to a backup location weekly
2. **Database backup**: Specifically backup the `Database/workload.db` file daily
3. **Cloud storage**: Consider storing backups on cloud storage (OneDrive, Google Drive, etc.)

### Data Sharing Between Applications
- Both applications use the same database (`workload.db`)
- Changes made in one application are immediately available in the other
- You can run both applications simultaneously if needed

---

## ⚠️ Important Usage Notes

### Application Startup
- **First startup** may take 30-60 seconds
- **Subsequent startups** are typically faster (10-20 seconds)
- **Large datasets** may require additional loading time

### Data Editing
- **Auto-save**: All changes are saved automatically
- **Double-click to edit**: Most cells can be edited by double-clicking
- **Validation**: The system prevents invalid data entry

### Performance Tips
1. **Close unused applications** to free up memory
2. **Use filters** to reduce the amount of data displayed
3. **Regular restarts** if the application becomes slow
4. **Keep database size manageable** (under 100MB for best performance)

---

## 🆘 Common Issues and Solutions

### Application Won't Start
- **Check file permissions**: Make sure you have read/write access to the folder
- **Antivirus interference**: Add the folder to your antivirus whitelist
- **Run as administrator**: Right-click the executable and select "Run as administrator"

### Database Errors
- **Database locked**: Close all instances of both applications and restart
- **Corrupted database**: Restore from your most recent backup
- **Permission denied**: Ensure the Database folder is not read-only

### Performance Issues
- **Slow loading**: Check available disk space and RAM
- **Application freezing**: Wait for operations to complete, or restart the application
- **Large dataset**: Use filters to reduce the amount of data displayed

### Display Issues
- **Screen too small**: Increase your display resolution or use zoom features
- **Text too small**: Use Windows display scaling (150% or 200%)
- **Interface cut off**: Maximize the application window

---

## 📞 Support Information

### Application Information
- **Version**: August 2025 Release
- **Developer**: Internal Development Team
- **Database**: SQLite (embedded)
- **Platform**: Windows Desktop Application

### For Technical Support
1. **Document the issue**: Take screenshots of any error messages
2. **Note the steps**: Write down what you were doing when the issue occurred
3. **Check this guide**: Review the troubleshooting section
4. **Backup your data**: Ensure you have a recent backup before any fixes

### Data Recovery
If you experience data loss:
1. **Stop using the application** immediately
2. **Check your backups** in the backup location
3. **Restore from backup**: Copy the backup `workload.db` file to the Database folder
4. **Contact support** if backups are not available

---

## 🔧 Advanced Usage

### Multiple Installations
- You can install the applications on multiple computers
- Copy the entire `FABSI_Deployment` folder to each computer
- Each installation will have its own database copy

### Network Usage
- The applications are designed for single-user desktop use
- For multi-user scenarios, consider setting up shared database location
- **Note**: Network database usage requires additional configuration

### Customization
- Logo files can be replaced in the `Photos` folder
- Excel templates can be modified in the `Templates` folder
- **Important**: Keep original file names and formats

---

## 📈 Best Practices

### Daily Operations
1. **Start applications** from the main FABSI_Deployment folder
2. **Use filters** to find specific data quickly
3. **Save exports** to a dedicated folder for reports
4. **Close applications** properly using the X button

### Weekly Maintenance
1. **Backup the database** to a secure location
2. **Check disk space** on your computer
3. **Restart applications** to clear memory
4. **Review and clean up** old export files

### Monthly Tasks
1. **Full system backup** including all FABSI files
2. **Performance check** - ensure applications start quickly
3. **Update documentation** if you discover new usage patterns
4. **Archive old data** if the database becomes very large

---

*This user guide is designed to help you effectively use the FABSI Workload Management Applications. Keep this document accessible for reference.*
