# Project Booking & Resource Allocation Application - Development Prompt

## Application Overview
Create a comprehensive workforce management application that handles employee project assignments, resource booking, and workload planning. This application should manage the complete lifecycle from employee selection to project booking and cost forecasting.

## Core Functionality (Based on Diagram Analysis)

### Step 1: Multi-Level Selection Interface
The application should provide a user-friendly interface with three primary selection dropdowns:
1. **Technical Unit** - Select the functional/technical department
2. **Project** - Choose from available projects
3. **Employee** - Select specific employee for assignment

### Step 2: Service Assignment & Booking Process
After selections are made:
- Display all project services assigned to the selected employee
- Allow users to add/assign services to hub personnel (like Alex in the example)
- Include estimated hours for each service
- Enable editing of assignments directly from the interface

### Step 3: Data Management & Integration
- Integrate with services database table
- Handle cases where database columns don't exist (keep null/empty values)
- Provide table/grid view for editing current assignments
- Support real-time data updates

## Database Schema Requirements

The application should handle a comprehensive employee and project booking dataset with the following 29 columns:

### Employee Information (Columns 1-6)
1. **Cost Center** - Employee's cost center code
2. **GHRS ID** - Global HR System identifier
3. **Last Name** - Employee surname
4. **First Name** - Employee given name
5. **Dept. Description** - Department description
6. **Work Location** - Employee's primary work location

### Employment Details (Columns 7-11)
7. **Business Unit** - Organizational business unit
8. **Tipo** - Employee type code
9. **Tipo Description** - Employee type description
10. **SAP Tipo** - SAP system employee type
11. **SAABU Rate (EUR)** - Standard rate in Euros

### Financial Rates (Columns 12-16)
12. **SAABU Rate (USD)** - Standard rate in US Dollars
13. **Local Agency Rate (USD)** - Local agency rate in USD
14. **Unit Rate (USD)** - Unit rate in USD
15. **Monthly Hours** - Standard monthly working hours
16. **Annual Hours** - Standard annual working hours

### Workload Planning (Columns 17-19)
17. **Workload 2025_Planned** - Planned workload for 2025
18. **Workload 2025_Actual** - Actual workload for 2025
19. **Remark** - Additional comments/remarks

### Project Assignment (Columns 20-23)
20. **Project** - Assigned project identifier
21. **Item** - Project item/task identifier
22. **Technical Unit** - Technical unit responsible
23. **Activities** - Specific activities assigned

### Booking Management (Columns 24-29)
24. **Booking Hours** - Total hours booked
25. **Booking Cost (Forecast)** - Forecasted cost for booking
26. **Booking Period** - Period for the booking
27. **Booking hours (Accepted by Project)** - Hours accepted by project manager
28. **Booking Period (Accepted by Project)** - Accepted booking period
29. **Booking hours (Extra)** - Additional/overtime hours

## Key Features to Implement

### 1. Intelligent Employee Identification
- **Challenge**: Employees may not select their exact name from dropdown
- **Solution**: Implement fuzzy matching or alternative identification methods
- Support multiple name variations (e.g., "Alex", "Mohamed", "Bassel", etc.)
- Provide search functionality with partial name matching

### 2. Dynamic Service Assignment
- Load all services assigned to selected employee
- Display services in an editable grid/table format
- Allow real-time addition and modification of service assignments
- Support bulk operations for multiple service assignments

### 3. Resource Planning & Forecasting
- Calculate booking costs based on different rate types
- Support multiple currencies (EUR, USD)
- Provide planned vs actual workload comparison
- Generate forecasting reports for resource allocation

### 4. Project Integration
- Link employees to specific projects and technical units
- Track project acceptance status for booked hours
- Manage project-specific activities and items
- Handle project booking periods and deadlines

### 5. User Interface Requirements
- Clean, intuitive interface similar to existing "List of Service" tool
- Responsive design for different screen sizes
- Real-time data validation and error handling
- Export functionality for reports and data analysis

## Technical Specifications

### Technology Stack Recommendations
- **Backend**: Python (Flask/FastAPI) for API development
- **Frontend**: HTML/CSS/JavaScript or Python GUI (tkinter/customtkinter)
- **Database**: SQLite for local deployment, PostgreSQL for enterprise
- **Data Processing**: Pandas for data manipulation and Excel integration

### Database Design
- Create normalized tables for employees, projects, services, and bookings
- Implement proper foreign key relationships
- Include audit trails for booking changes and approvals
- Support data import from Excel files

### Security & Access Control
- Implement user authentication and authorization
- Role-based access (Employee, Project Manager, Admin)
- Data encryption for sensitive employee information
- Audit logging for all booking changes

## Integration Requirements

### Excel File Support
- Import/export functionality for Excel files
- Support for the existing data structure (29 columns)
- Batch processing for large datasets
- Data validation during import process

### Reporting & Analytics
- Generate workload reports by technical unit, project, or employee
- Cost analysis and budget tracking
- Resource utilization reports
- Booking acceptance rate analytics

## User Workflow

### Primary Use Case
1. User selects Technical Unit from dropdown
2. User selects Project from filtered list
3. User selects Employee (with intelligent matching)
4. System displays all services assigned to the employee
5. User can add/edit service assignments with estimated hours
6. System updates booking hours and calculates costs
7. Project manager can review and accept/reject bookings
8. System tracks planned vs actual workload

### Administrative Functions
- Manage employee master data
- Configure project and service catalogs
- Set up rate tables and cost centers
- Generate management reports

## Success Criteria

The application should successfully:
1. Handle the complete employee project booking lifecycle
2. Provide accurate cost forecasting and resource planning
3. Support multiple user roles and access levels
4. Integrate seamlessly with existing Excel-based workflows
5. Offer real-time data updates and validation
6. Generate comprehensive reports for management decision-making

## Development Approach

1. **Phase 1**: Core database design and basic CRUD operations
2. **Phase 2**: User interface development with dropdown functionality
3. **Phase 3**: Service assignment and booking logic implementation
4. **Phase 4**: Reporting and analytics features
5. **Phase 5**: Excel integration and data migration tools
6. **Phase 6**: User testing and deployment

This application will serve as a comprehensive workforce management solution, enabling efficient project resource allocation, accurate cost forecasting, and streamlined booking processes for the organization.
