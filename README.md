# FABSI - List of Service Application

## Overview
This application is a full-stack workload management tool for engineering projects. It features:
- A Tkinter-based GUI for managing and viewing services and activities
- A Flask RESTful API for CRUD operations and integration
- SQLite database for persistent storage
- Excel import/export for bulk data management

## 🚀 Quick Deployment (For Company Workstations)

### For End Users:
1. Download the deployment package from your IT department
2. Run `install_fabsi.bat` as Administrator
3. Use the desktop shortcut to start the application
4. **No Python installation required!**

### For IT Administrators:
See `DEPLOYMENT_GUIDE.md` for complete deployment instructions.

### For Developers:
Run `build_deployment.bat` to create a standalone executable.

## How to Run the Application

### 1. Set up the Python Environment
- Make sure you have Python 3.8+ installed.
- (Recommended) Create a virtual environment:
  ```
  python -m venv .venv
  .venv\Scripts\activate  # On Windows
  ```
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

### 2. Prepare the Database
- Ensure `workload.db` exists in the project folder. If not, run the database setup and seeding scripts (e.g., `db_setup.py`, `seed_service.py`).
- The database is seeded from the Excel file `FABSI_List of Service HO_Master_R1.xlsx`.

### 3. Run the Flask API (for testing or integration)
- In one terminal:
  ```
  python api.py
  ```
- The API will be available at `http://localhost:5000/` and includes Swagger UI for testing endpoints.

### 4. Run the Main Application (Tkinter GUI)
- In another terminal:
  ```
  python Fabsi_List_of_Service.py
  ```
- The GUI will open. Use the dropdowns to select foreign key values, import Excel data, and manage services.

## Features & Tasks Completed

### Database & Backend
- Designed and created all required tables: StickBuilt, Module, Activities, Title, TechnicalUnit, Employee, Progress, ProfessionalUnit, Project, Service
- Seeded all tables from Excel sheets (TemplateList, List Of Service, and project-specific sheets)
- Service table links all foreign keys and includes extra fields (department, hours, dates, notes)

### API
- Built with Flask-RESTful
- CRUD endpoints for all entities
- Swagger UI for easy API testing
- API used for integration and testing (main app reads directly from DB)

### Tkinter GUI
- Dropdowns for all foreign key fields, populated from the database
- Add new service (saved to Service table)
- Import data from Excel (saves to Service table)
- Table/grid view of all services, with filter by project
- Data only shown after selecting a project
- Export to Excel and PDF
- Clean, organized, and user-friendly interface

### Integration & Workflow
- Both API and GUI can be run in parallel for full-stack testing
- All data flows from Excel → DB → GUI/API
- All code is modular and organized for maintainability

## Daily Summary of Work
- Environment setup and dependency installation
- Database schema design and creation
- Data seeding from Excel
- Flask API development (CRUD, Swagger)
- Tkinter GUI development and integration
- Implemented dropdowns and project filter
- Ensured all data flows and UI actions work as required
- Added error handling and logging for easier debugging
- Switched to use `workload.db` as the main database

## Contact
For any issues or questions, contact the project maintainer.
# WorkloadDataPython