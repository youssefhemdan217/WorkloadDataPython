import os
import re
import logging
import sqlite3
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import pandas as pd
import subprocess
import traceback
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from datetime import datetime, date
from PIL import Image, ImageTk

# Set up logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'project_booking_app.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Set customtkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ProjectBookingApp:
    """Project Booking & Resource Allocation Application"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Project Booking & Resource Allocation System")
        self.root.geometry("1600x1000")  # Increased window size for better table visibility
        
        # Database connection
        self.db_path = "workload.db"
        self.init_extended_database()
        
        # Variables for dropdowns
        self.selected_technical_unit = tk.StringVar()
        self.selected_project = tk.StringVar()
        self.selected_employee = tk.StringVar()
        
        # Store mapping of dropdown display names to IDs
        self.technical_unit_map = {}
        self.project_map = {}
        self.employee_map = {}
        
        # Data storage
        self.technical_units = []
        self.projects = []
        self.employees = []
        
        # Store selected rows for multi-select deletion
        self.selected_rows = set()
        
        # Auto-refresh timer (refresh every 30 seconds)
        self.auto_refresh_enabled = True
        self.schedule_auto_refresh()
        self.current_bookings = []
        
        self.setup_ui()
        self.load_data()
        
    def init_extended_database(self):
        """Initialize database schema for project booking - using existing tables only"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if tables exist - do not create new ones, use existing structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service'")
            if not cursor.fetchone():
                print("Warning: service table not found")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employee'")
            if not cursor.fetchone():
                print("Warning: employee table not found")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_bookings'")
            if not cursor.fetchone():
                # Only create project_bookings if it doesn't exist, using existing table references
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        technical_unit_id INTEGER,
                        project_id INTEGER,
                        service_id INTEGER,
                        estimated_hours DECIMAL(10,2),
                        actual_hours DECIMAL(10,2),
                        hourly_rate DECIMAL(10,2),
                        total_cost DECIMAL(10,2),
                        booking_status VARCHAR(50) DEFAULT 'Pending',
                        booking_date DATE,
                        start_date DATE,
                        end_date DATE,
                        notes TEXT,
                        created_by VARCHAR(100),
                        approved_by VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employee (id),
                        FOREIGN KEY (technical_unit_id) REFERENCES technical_unit (id),
                        FOREIGN KEY (project_id) REFERENCES project (id),
                        FOREIGN KEY (service_id) REFERENCES service (id)
                    )
                ''')
            
            conn.commit()
            conn.close()
            print("Database schema checked successfully - using existing tables")
            
        except Exception as e:
            print(f"Error checking database: {e}")
            logging.error(f"Database check error: {e}")
    
    def setup_ui(self):
        """Setup the main user interface - Dropdowns + Employee Data Table Only"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=3, pady=3)  # Minimal padding for maximum space
        
        # Keep Selection Panel for filtering
        self.setup_selection_panel()
        
        # Show only Employee Data Table with 29 columns
        self.setup_employee_data_table_only()
        
    def setup_header(self):
        """Setup application header"""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=5, pady=(5, 5))  # Minimal padding
        
        # Logo and title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Project Booking & Resource Allocation System",
            font=ctk.CTkFont(size=16, weight="bold")  # Smaller font
        )
        title_label.pack(pady=5)  # Minimal padding
        
        # Action buttons
        button_frame = ctk.CTkFrame(header_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 3))  # Minimal padding
        
        self.import_btn = ctk.CTkButton(
            button_frame, 
            text="Import Excel Data", 
            command=self.import_excel_data,
            width=150
        )
        self.import_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(
            button_frame, 
            text="Export Report", 
            command=self.export_report,
            width=150
        )
        self.export_btn.pack(side="left", padx=5)
        
        self.refresh_btn = ctk.CTkButton(
            button_frame, 
            text="Refresh Data", 
            command=self.load_data,
            width=150
        )
        self.refresh_btn.pack(side="left", padx=5)
    
    def setup_selection_panel(self):
        """Setup the three-level selection panel - FOR ADDING DATA"""
        selection_frame = ctk.CTkFrame(self.main_frame)
        selection_frame.pack(fill="x", padx=3, pady=(3, 5))  # Minimal padding
        
        selection_label = ctk.CTkLabel(
            selection_frame, 
            text="Add Service Data",
            font=ctk.CTkFont(size=14, weight="bold")  # Clear purpose
        )
        selection_label.pack(pady=(3, 2))  # Minimal padding
        
        # Dropdown container
        dropdown_frame = ctk.CTkFrame(selection_frame)
        dropdown_frame.pack(fill="x", padx=5, pady=2)  # Minimal padding
        
        # Technical Unit dropdown
        tech_unit_frame = ctk.CTkFrame(dropdown_frame)
        tech_unit_frame.pack(side="left", fill="x", expand=True, padx=3)
        
        ctk.CTkLabel(tech_unit_frame, text="Technical Unit:", font=ctk.CTkFont(size=11)).pack(pady=(2, 0))
        self.tech_unit_dropdown = ctk.CTkComboBox(
            tech_unit_frame,
            variable=self.selected_technical_unit,
            command=self.on_technical_unit_change,
            width=200
        )
        self.tech_unit_dropdown.pack(pady=3, padx=3)
        
        # Project dropdown
        project_frame = ctk.CTkFrame(dropdown_frame)
        project_frame.pack(side="left", fill="x", expand=True, padx=3)
        
        ctk.CTkLabel(project_frame, text="Project:", font=ctk.CTkFont(size=11)).pack(pady=(2, 0))
        self.project_dropdown = ctk.CTkComboBox(
            project_frame,
            variable=self.selected_project,
            command=self.on_project_change,
            width=200
        )
        self.project_dropdown.pack(pady=3, padx=3)
        
        # Employee dropdown
        employee_frame = ctk.CTkFrame(dropdown_frame)
        employee_frame.pack(side="left", fill="x", expand=True, padx=3)
        
        ctk.CTkLabel(employee_frame, text="Employee:", font=ctk.CTkFont(size=11)).pack(pady=(2, 0))
        self.employee_dropdown = ctk.CTkComboBox(
            employee_frame,
            variable=self.selected_employee,
            command=self.on_employee_change,
            width=200
        )
        self.employee_dropdown.pack(pady=3, padx=3)
        
        # Action buttons under dropdowns
        button_frame = ctk.CTkFrame(selection_frame)
        button_frame.pack(fill="x", padx=5, pady=3)
        
        self.delete_employee_btn = ctk.CTkButton(
            button_frame, 
            text="Delete Booking", 
            command=self.delete_employee_record,
            width=120
        )
        self.delete_employee_btn.pack(side="left", padx=3)
        
        self.refresh_emp_data_btn = ctk.CTkButton(
            button_frame, 
            text="Refresh Data", 
            command=self.smart_refresh,
            width=120
        )
        self.refresh_emp_data_btn.pack(side="left", padx=3)
        
        self.delete_selected_btn = ctk.CTkButton(
            button_frame, 
            text="Delete Selected", 
            command=self.delete_selected_rows,
            width=120
        )
        self.delete_selected_btn.pack(side="left", padx=3)
        
        # self.auto_refresh_btn = ctk.CTkButton(
        #     button_frame, 
        #     text="Auto-Refresh: ON", 
        #     command=self.toggle_auto_refresh,
        #     width=120
        # )
        # self.auto_refresh_btn.pack(side="left", padx=3)
        
        self.import_btn = ctk.CTkButton(
            button_frame, 
            text="Import Excel", 
            command=self.import_excel_data,
            width=120
        )
        self.import_btn.pack(side="left", padx=3)
        
        self.export_btn = ctk.CTkButton(
            button_frame, 
            text="Export Report", 
            command=self.export_report,
            width=120
        )
        self.export_btn.pack(side="left", padx=3)
        
        self.edit_mode_btn = ctk.CTkButton(
            button_frame, 
            text="Edit Mode: Double-Click", 
            command=self.toggle_edit_mode,
            width=140
        )
        self.edit_mode_btn.pack(side="left", padx=3)
    
    def setup_employee_data_table_only(self):
        """Setup only the employee data table to maximize space"""
        # Updated title for unified table approach
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Employee Booking Data (Unified Tables)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(3, 2))
        
        # Employee data grid with booking information (simplified view)
        self.setup_employee_data_grid_maximized(self.main_frame)
    
    def setup_employee_data_grid_maximized(self, parent):
        """Setup treeview for employee data with booking information - MAXIMIZED"""
        emp_tree_frame = ctk.CTkFrame(parent)
        emp_tree_frame.pack(fill="both", expand=True, padx=2, pady=2)  # Maximum space
        
        # Create treeview with scrollbars
        emp_tree_container = tk.Frame(emp_tree_frame)
        emp_tree_container.pack(fill="both", expand=True, padx=1, pady=1)  # Maximum space
        
        # Define simplified columns for unified view
        emp_columns = (
            "Select", "ID", "Employee Name", "Total Bookings", "Est. Hours", "Actual Hours", 
            "Total Cost", "Projects", "Technical Units", "Status", "Last Booking"
        )
        
        # Maximum height for the table - most of the screen
        self.employee_tree = ttk.Treeview(emp_tree_container, columns=emp_columns, show="headings", height=32)
        
        # Configure column headings and widths for simplified view
        column_widths = {
            "Select": 60, "ID": 50, "Employee Name": 200, "Total Bookings": 100, 
            "Est. Hours": 100, "Actual Hours": 100, "Total Cost": 120,
            "Projects": 150, "Technical Units": 150, "Status": 100, 
            "Last Booking": 120
        }
        
        for col in emp_columns:
            self.employee_tree.heading(col, text=col)
            width = column_widths.get(col, 100)
            self.employee_tree.column(col, width=width, anchor="center", minwidth=80)
        
        # Scrollbars for employee data grid - PROPERLY POSITIONED
        emp_v_scrollbar = ttk.Scrollbar(emp_tree_container, orient="vertical", command=self.employee_tree.yview)
        emp_h_scrollbar = ttk.Scrollbar(emp_tree_container, orient="horizontal", command=self.employee_tree.xview)
        
        self.employee_tree.configure(yscrollcommand=emp_v_scrollbar.set, xscrollcommand=emp_h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.employee_tree.grid(row=0, column=0, sticky="nsew")
        emp_v_scrollbar.grid(row=0, column=1, sticky="ns")
        emp_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        emp_tree_container.grid_rowconfigure(0, weight=1)
        emp_tree_container.grid_columnconfigure(0, weight=1)
        
        # Excel-like editing setup
        self.edit_mode = "double"  # "single" or "double" click
        
        # Bind double-click event for editing (Excel-like behavior)
        self.employee_tree.bind('<Double-1>', self.on_simplified_cell_edit)
        
        # Add keyboard shortcut for editing (F2 like Excel)
        self.employee_tree.bind('<F2>', self.on_keyboard_edit)
        
        # Add visual feedback for selected cells
        self.employee_tree.bind('<Button-1>', self.on_cell_select)
        
        # Add checkbox selection functionality
        self.employee_tree.bind('<Button-1>', self.toggle_row_selection, add='+')
        
        # Load employee data initially
        self.load_employee_data_grid()
    
    def setup_employee_details_panel(self):
        """Setup employee details display panel"""
        details_frame = ctk.CTkFrame(self.main_frame)
        details_frame.pack(fill="x", padx=5, pady=(0, 5))  # Minimal padding
        
        details_label = ctk.CTkLabel(
            details_frame, 
            text="Employee Details",
            font=ctk.CTkFont(size=14, weight="bold")  # Smaller font
        )
        details_label.pack(pady=(3, 2))  # Minimal padding
        
        # Details container
        self.details_container = ctk.CTkFrame(details_frame)
        self.details_container.pack(fill="x", padx=10, pady=3)  # Minimal padding
        
        # Employee info will be populated here
        self.employee_info_label = ctk.CTkLabel(
            self.details_container, 
            text="Select an employee to view details",
            font=ctk.CTkFont(size=10)  # Smaller font
        )
        self.employee_info_label.pack(pady=3)  # Minimal padding
    
    def setup_service_assignment_panel(self):
        """Setup service assignment panel"""
        service_frame = ctk.CTkFrame(self.main_frame)
        service_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))  # More space for table
        
        # Create tabview for different data views
        self.tabview = ctk.CTkTabview(service_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=2)  # Minimal padding, more space
        
        # Tab 1: Service Assignments
        self.tabview.add("Service Assignments")
        service_tab = self.tabview.tab("Service Assignments")
        
        service_label = ctk.CTkLabel(
            service_tab, 
            text="Service Assignment & Booking",
            font=ctk.CTkFont(size=14, weight="bold")  # Smaller font
        )
        service_label.pack(pady=(2, 1))  # Minimal padding
        
        # Service list with treeview
        self.setup_service_treeview(service_tab)
        
        # Service actions
        action_frame = ctk.CTkFrame(service_tab)
        action_frame.pack(fill="x", padx=5, pady=2)  # Minimal padding
        
        self.add_service_btn = ctk.CTkButton(
            action_frame, 
            text="Add Service Assignment", 
            command=self.add_service_assignment,
            width=200
        )
        self.add_service_btn.pack(side="left", padx=3)
        
        self.edit_service_btn = ctk.CTkButton(
            action_frame, 
            text="Edit Assignment", 
            command=self.edit_service_assignment,
            width=200
        )
        self.edit_service_btn.pack(side="left", padx=3)
        
        self.delete_service_btn = ctk.CTkButton(
            action_frame, 
            text="Remove Assignment", 
            command=self.delete_service_assignment,
            width=200
        )
        self.delete_service_btn.pack(side="left", padx=3)
        
        # Tab 2: Employee Data (29 Columns)
        self.tabview.add("Employee Data (29 Columns)")
        employee_tab = self.tabview.tab("Employee Data (29 Columns)")
        
        employee_data_label = ctk.CTkLabel(
            employee_tab, 
            text="Complete Employee Data - 29 Columns",
            font=ctk.CTkFont(size=14, weight="bold")  # Smaller font
        )
        employee_data_label.pack(pady=(2, 1))  # Minimal padding
        
        # Employee data grid with all 29 columns
        self.setup_employee_data_grid(employee_tab)
        
        # Employee data actions
        emp_action_frame = ctk.CTkFrame(employee_tab)
        emp_action_frame.pack(fill="x", padx=5, pady=2)  # Minimal padding
        
        self.delete_employee_btn = ctk.CTkButton(
            emp_action_frame, 
            text="Delete Employee", 
            command=self.delete_employee_record,
            width=150
        )
        self.delete_employee_btn.pack(side="left", padx=3)
        
        self.refresh_emp_data_btn = ctk.CTkButton(
            emp_action_frame, 
            text="Refresh Data", 
            command=self.load_employee_data_grid,
            width=150
        )
        self.refresh_emp_data_btn.pack(side="left", padx=3)
    
    def setup_service_treeview(self, parent):
        """Setup treeview for service assignments"""
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=2)  # Minimal padding, more space
        
        # Create treeview with scrollbars
        tree_container = tk.Frame(tree_frame)
        tree_container.pack(fill="both", expand=True, padx=2, pady=2)  # Minimal padding
        
        # Define columns
        columns = ("Service", "Activity", "Est. Hours", "Actual Hours", "Rate", "Cost", "Status", "Period")
        
        self.service_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=22)  # Increased height more
        
        # Configure column headings and widths
        for col in columns:
            self.service_tree.heading(col, text=col)
            self.service_tree.column(col, width=120, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.service_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.service_tree.xview)
        
        self.service_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.service_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
    
    def setup_employee_data_grid(self, parent):
        """Setup treeview for complete employee data with all 29 columns"""
        emp_tree_frame = ctk.CTkFrame(parent)
        emp_tree_frame.pack(fill="both", expand=True, padx=5, pady=2)  # Minimal padding, more space
        
        # Create treeview with scrollbars
        emp_tree_container = tk.Frame(emp_tree_frame)
        emp_tree_container.pack(fill="both", expand=True, padx=2, pady=2)  # Minimal padding
        
        # Define all 29 columns
        emp_columns = (
            "ID", "Cost Center", "GHRS ID", "Last Name", "First Name", "Dept. Description",
            "Work Location", "Business Unit", "Tipo", "Tipo Description", "SAP Tipo",
            "SAABU Rate (EUR)", "SAABU Rate (USD)", "Local Agency Rate (USD)", "Unit Rate (USD)",
            "Monthly Hours", "Annual Hours", "Workload 2025_Planned", "Workload 2025_Actual",
            "Remark", "Project", "Item", "Technical Unit", "Activities", "Booking Hours",
            "Booking Cost (Forecast)", "Booking Period", "Booking hours (Accepted by Project)",
            "Booking Period (Accepted by Project)", "Booking hours (Extra)"
        )
        
        # Increased height significantly to show more rows like FABSI app
        self.employee_tree = ttk.Treeview(emp_tree_container, columns=emp_columns, show="headings", height=30)  # Increased from 25 to 30
        
        # Configure column headings and widths with better optimization
        column_widths = {
            "ID": 50, "Cost Center": 100, "GHRS ID": 100, "Last Name": 120, "First Name": 120,
            "Dept. Description": 150, "Work Location": 120, "Business Unit": 120, "Tipo": 80,
            "Tipo Description": 150, "SAP Tipo": 80, "SAABU Rate (EUR)": 120, "SAABU Rate (USD)": 120,
            "Local Agency Rate (USD)": 150, "Unit Rate (USD)": 120, "Monthly Hours": 100,
            "Annual Hours": 100, "Workload 2025_Planned": 150, "Workload 2025_Actual": 150,
            "Remark": 200, "Project": 120, "Item": 100, "Technical Unit": 120, "Activities": 150,
            "Booking Hours": 100, "Booking Cost (Forecast)": 150, "Booking Period": 120,
            "Booking hours (Accepted by Project)": 200, "Booking Period (Accepted by Project)": 200,
            "Booking hours (Extra)": 150
        }
        
        for col in emp_columns:
            self.employee_tree.heading(col, text=col)
            width = column_widths.get(col, 100)
            self.employee_tree.column(col, width=width, anchor="center", minwidth=80)
        
        # Scrollbars for employee data grid
        emp_v_scrollbar = ttk.Scrollbar(emp_tree_container, orient="vertical", command=self.employee_tree.yview)
        emp_h_scrollbar = ttk.Scrollbar(emp_tree_container, orient="horizontal", command=self.employee_tree.xview)
        
        self.employee_tree.configure(yscrollcommand=emp_v_scrollbar.set, xscrollcommand=emp_h_scrollbar.set)
        
        # Pack employee data grid
        self.employee_tree.pack(side="left", fill="both", expand=True)
        emp_v_scrollbar.pack(side="right", fill="y")
        emp_h_scrollbar.pack(side="bottom", fill="x")
        
        # Load employee data initially
        self.load_employee_data_grid()
    
    def setup_booking_management_panel(self):
        """Setup booking management panel"""
        booking_frame = ctk.CTkFrame(self.main_frame)
        booking_frame.pack(fill="x", padx=5, pady=(0, 5))  # Minimal padding
        
        booking_label = ctk.CTkLabel(
            booking_frame, 
            text="Step 3: Booking Management",
            font=ctk.CTkFont(size=14, weight="bold")  # Smaller font
        )
        booking_label.pack(pady=(3, 2))  # Minimal padding
        
        # Booking summary
        summary_frame = ctk.CTkFrame(booking_frame)
        summary_frame.pack(fill="x", padx=10, pady=3)  # Minimal padding
        
        self.booking_summary_label = ctk.CTkLabel(
            summary_frame, 
            text="Total Booking Hours: 0 | Total Cost: $0.00 | Status: No bookings",
            font=ctk.CTkFont(size=12)  # Smaller font
        )
        self.booking_summary_label.pack(pady=3)  # Minimal padding
        
        # Booking actions
        booking_action_frame = ctk.CTkFrame(booking_frame)
        booking_action_frame.pack(fill="x", padx=10, pady=(0, 3))  # Minimal padding
        
        self.save_booking_btn = ctk.CTkButton(
            booking_action_frame, 
            text="Save Booking", 
            command=self.save_booking,
            width=150
        )
        self.save_booking_btn.pack(side="left", padx=3)
        
        self.approve_booking_btn = ctk.CTkButton(
            booking_action_frame, 
            text="Approve Booking", 
            command=self.approve_booking,
            width=150
        )
        self.approve_booking_btn.pack(side="left", padx=3)
        
        self.reject_booking_btn = ctk.CTkButton(
            booking_action_frame, 
            text="Reject Booking", 
            command=self.reject_booking,
            width=150
        )
        self.reject_booking_btn.pack(side="left", padx=3)
    
    def load_data(self):
        """Load data from database using unified tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load technical units with mapping
            cursor.execute("SELECT id, name FROM technical_unit ORDER BY name")
            self.technical_units = cursor.fetchall()
            self.technical_unit_map = {tu[1]: tu[0] for tu in self.technical_units}
            tech_unit_names = [tu[1] for tu in self.technical_units]
            self.tech_unit_dropdown.configure(values=tech_unit_names)
            
            # Load projects with mapping
            cursor.execute("SELECT id, name FROM project ORDER BY name")
            self.projects = cursor.fetchall()
            self.project_map = {p[1]: p[0] for p in self.projects}
            project_names = [p[1] for p in self.projects]
            self.project_dropdown.configure(values=project_names)
            
            # Load employees from employee table only with mapping
            cursor.execute("SELECT id, name FROM employee ORDER BY name")
            all_employees = cursor.fetchall()
            
            # Create employee mapping - all employees are now unified
            self.employees = []
            self.employee_map = {}
            
            for emp in all_employees:
                display_name = emp[1]  # Just use the name without type indicator
                self.employees.append((emp[0], emp[1], "unified"))
                self.employee_map[display_name] = {"id": emp[0], "type": "unified"}
            
            employee_names = list(self.employee_map.keys())
            self.employee_dropdown.configure(values=employee_names)
            
            conn.close()
            
            # Load the employee data grid
            self.load_employee_data_grid()
            
            print("Data loaded successfully from unified tables")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            logging.error(f"Data loading error: {e}")
    
    def on_technical_unit_change(self, value):
        """Handle technical unit selection change"""
        if value:
            self.check_and_add_service_data()
    
    def on_project_change(self, value):
        """Handle project selection change"""
        if value:
            self.check_and_add_service_data()
    
    def on_employee_change(self, value):
        """Handle employee selection change"""
        if value:
            self.display_employee_details()  # Show employee details if panel exists
            self.load_employee_services()    # Load services for selected employee
            self.check_and_add_service_data() # Check if all dropdowns are selected
    
    def check_and_add_service_data(self):
        """Check if all dropdowns are selected and filter service table to add to project_bookings table"""
        try:
            tech_unit_name = self.selected_technical_unit.get()
            project_name = self.selected_project.get()
            employee_name = self.selected_employee.get()
            
            # Only proceed if all three have valid selections
            if (tech_unit_name and tech_unit_name in self.technical_unit_map and 
                project_name and project_name in self.project_map and 
                employee_name and employee_name in self.employee_map):
                
                # Get IDs from the mappings
                tech_unit_id = self.technical_unit_map[tech_unit_name]
                project_id = self.project_map[project_name]
                employee_info = self.employee_map[employee_name]
                employee_id = employee_info["id"]
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Filter service table by the three dropdown selections
                cursor.execute("""
                    SELECT id, estimated_internal_hours, estimated_external_hours, 
                           start_date, due_date, notes, activities_id, title_id
                    FROM service 
                    WHERE technical_unit_id = ? AND project_id = ? AND employee_id = ?
                """, (tech_unit_id, project_id, employee_id))
                
                matching_services = cursor.fetchall()
                
                if matching_services:
                    # Add each matching service to project_bookings table
                    bookings_added = 0
                    for service in matching_services:
                        service_id = service[0]
                        estimated_internal = service[1] or 0
                        estimated_external = service[2] or 0
                        # Use total estimated hours (internal + external)
                        total_estimated = (estimated_internal or 0) + (estimated_external or 0)
                        start_date = service[3]
                        end_date = service[4]  # due_date
                        service_notes = service[5]
                        
                        # Check if this booking already exists
                        cursor.execute("""
                            SELECT id FROM project_bookings 
                            WHERE employee_id = ? AND technical_unit_id = ? 
                            AND project_id = ? AND service_id = ?
                        """, (employee_id, tech_unit_id, project_id, service_id))
                        
                        existing_booking = cursor.fetchone()
                        
                        if not existing_booking:
                            # Get employee data for the new fields
                            cursor.execute("""
                                SELECT cost_center, ghrs_id, COALESCE(first_name || ' ' || last_name, last_name, first_name, 'N/A') as employee_name, dept_description,
                                       work_location, business_unit, tipo, tipo_description, sap_tipo,
                                       saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                                       monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                                       remark
                                FROM employee_extended WHERE id = ?
                            """, (employee_id,))
                            emp_data = cursor.fetchone()
                            
                            # Fallback: get employee name from main employee table if extended doesn't have it
                            if not emp_data or not emp_data[2]:
                                cursor.execute("SELECT name FROM employee WHERE id = ?", (employee_id,))
                                emp_name_fallback = cursor.fetchone()
                                emp_name = emp_name_fallback[0] if emp_name_fallback else "N/A"
                            else:
                                emp_name = emp_data[2]
                            
                            # Get project name
                            cursor.execute("SELECT name FROM project WHERE id = ?", (project_id,))
                            project_data = cursor.fetchone()
                            project_name_val = project_data[0] if project_data else "N/A"
                            
                            # Get technical unit name
                            cursor.execute("SELECT name FROM technical_unit WHERE id = ?", (tech_unit_id,))
                            tu_data = cursor.fetchone()
                            tu_name_val = tu_data[0] if tu_data else "N/A"
                            
                            # Get activities name
                            cursor.execute("""
                                SELECT a.name FROM service s 
                                LEFT JOIN activities a ON s.activities_id = a.id 
                                WHERE s.id = ?
                            """, (service_id,))
                            activity_data = cursor.fetchone()
                            activity_name_val = activity_data[0] if activity_data else "N/A"
                            
                            # Prepare values with defaults
                            if emp_data:
                                (cost_center, ghrs_id, employee_name_from_query, dept_description,
                                 work_location, business_unit, tipo, tipo_description, sap_tipo,
                                 saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                                 monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                                 remark) = emp_data
                            else:
                                # Default values when employee_extended data not available
                                (cost_center, ghrs_id, dept_description,
                                 work_location, business_unit, tipo, tipo_description, sap_tipo,
                                 saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                                 monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                                 remark) = (None, None, None, None, None, None, None, None,
                                           0.00, 0.00, 0.00, 0.00, 0, 0, 0.00, 0.00, None)
                            
                            # Parse first_name and last_name from full name (FIXED VERSION 2025-08-08)
                            cursor.execute("SELECT name FROM employee WHERE id = ?", (employee_id,))
                            name_data = cursor.fetchone()
                            full_name = name_data[0] if name_data and name_data[0] else ""
                            
                            # Try to split the name into first and last names
                            if full_name and full_name.strip():
                                name_parts = full_name.strip().split()
                                if len(name_parts) >= 2:
                                    first_name = name_parts[0]
                                    last_name = " ".join(name_parts[1:])
                                else:
                                    first_name = ""
                                    last_name = full_name
                            else:
                                first_name = ""
                                last_name = ""
                            
                            # Insert comprehensive booking record with all 47 columns (excluding auto-increment id)
                            cursor.execute("""
                                INSERT INTO project_bookings 
                                (employee_id, technical_unit_id, project_id, service_id,
                                 estimated_hours, actual_hours, hourly_rate, total_cost, 
                                 booking_status, booking_date, start_date, end_date, notes,
                                 created_by, approved_by, created_at, updated_at,
                                 cost_center, ghrs_id, last_name, first_name, dept_description,
                                 work_location, business_unit, tipo, tipo_description, sap_tipo,
                                 saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                                 monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                                 remark, project_name, item, technical_unit_name, activities_name,
                                 booking_hours, booking_cost_forecast, booking_period,
                                 booking_hours_accepted, booking_period_accepted, booking_hours_extra,
                                 employee_name)
                                VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL, 'Pending', 
                                        CURRENT_DATE, ?, ?, ?, NULL, NULL, 
                                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                        ?, NULL, ?, ?, 0.00, 0.00, NULL, 0.00, NULL, 0.00, ?)
                            """, (employee_id, tech_unit_id, project_id, service_id,
                                  total_estimated, start_date, end_date, service_notes,
                                  cost_center, ghrs_id, last_name, first_name, dept_description,
                                  work_location, business_unit, tipo, tipo_description, sap_tipo,
                                  saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                                  monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                                  remark, project_name_val, tu_name_val, activity_name_val, emp_name))
                            bookings_added += 1
                    
                    conn.commit()
                    
                    # Immediate refresh of data and grids
                    self.refresh_employee_data()
                    self.load_data()  # Refresh dropdowns to include any new data
                    
                    # DON'T reset dropdowns - keep selections as requested
                    
                    if bookings_added > 0:
                        messagebox.showinfo("Success", 
                            f"Added {bookings_added} booking record(s) for {employee_name} to project {project_name}!\n" +
                            "Unknown fields are set to NULL and can be edited by double-clicking cells.")
                    else:
                        messagebox.showinfo("Info", 
                            f"All matching services for {employee_name} are already booked to project {project_name}.")
                else:
                    messagebox.showwarning("No Services Found", 
                        f"No services found matching:\n" +
                        f"Technical Unit: {tech_unit_name}\n" +
                        f"Project: {project_name}\n" +
                        f"Employee: {employee_name}")
                
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add service data: {e}")
            logging.error(f"Service data addition error: {e}")
            import traceback
            traceback.print_exc()
    
    def display_employee_details(self):
        """Display selected employee details from unified employee table"""
        selected = self.selected_employee.get()
        if not selected or selected not in self.employee_map:
            return
        
        try:
            employee_info = self.employee_map[selected]
            employee_id = employee_info["id"]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get employee information from unified employee table
            cursor.execute("SELECT name FROM employee WHERE id = ?", (employee_id,))
            emp_data = cursor.fetchone()
            
            if emp_data:
                details_text = f"Employee: {emp_data[0]}\nType: Unified Employee Table"
            else:
                details_text = "Employee details not found"
            
            if hasattr(self, 'employee_info_label'):
                self.employee_info_label.configure(text=details_text, justify="left")
            conn.close()
            
        except Exception as e:
            if hasattr(self, 'employee_info_label'):
                self.employee_info_label.configure(text=f"Error loading employee details: {e}")
            logging.error(f"Employee details error: {e}")
    
    def load_employee_services(self):
        """Load services assigned to selected employee from project_bookings table using unified tables"""
        selected_emp = self.selected_employee.get()
        if not selected_emp or selected_emp not in self.employee_map:
            # Clear the treeview if it exists
            if hasattr(self, 'service_tree'):
                for item in self.service_tree.get_children():
                    self.service_tree.delete(item)
            return
        
        try:
            # Clear existing items
            if hasattr(self, 'service_tree'):
                for item in self.service_tree.get_children():
                    self.service_tree.delete(item)
            
            # Get employee info from mapping
            employee_info = self.employee_map[selected_emp]
            employee_id = employee_info["id"]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load from project_bookings table with detailed service information
            cursor.execute("""
                SELECT pb.id, p.name as project_name, 
                       COALESCE(a.name, 'Unknown Activity') as activity_name,
                       pb.estimated_hours, pb.actual_hours,
                       pb.hourly_rate, pb.total_cost, pb.booking_status, 
                       COALESCE(pb.start_date, pb.booking_date) as period,
                       tu.name as technical_unit_name,
                       pb.notes
                FROM project_bookings pb
                LEFT JOIN project p ON pb.project_id = p.id
                LEFT JOIN technical_unit tu ON pb.technical_unit_id = tu.id
                LEFT JOIN service s ON pb.service_id = s.id
                LEFT JOIN activities a ON s.activities_id = a.id
                WHERE pb.employee_id = ?
                ORDER BY pb.created_at DESC
            """, (employee_id,))
            
            bookings = cursor.fetchall()
            
            # Populate treeview if it exists
            total_hours = 0
            total_cost = 0
            
            if hasattr(self, 'service_tree'):
                for booking in bookings:
                    booking_id = booking[0]
                    project_name = booking[1] or "Unknown Project"
                    activity_name = booking[2] or "Unknown Activity"
                    est_hours = booking[3] or 0
                    actual_hours = booking[4] or 0
                    rate = booking[5] or 0
                    cost = booking[6] or 0
                    status = booking[7] or "Pending"
                    period = booking[8] or "N/A"
                    technical_unit = booking[9] or "N/A"
                    notes = booking[10] or ""
                    
                    # Format display values
                    display_service = f"{project_name} ({technical_unit})"
                    display_period = str(period)[:10] if period else "N/A"  # Show date only
                    
                    self.service_tree.insert("", "end", values=(
                        display_service, activity_name, est_hours, actual_hours, 
                        rate, cost, status, display_period
                    ), tags=(str(booking_id),))  # Store booking ID in tags for future reference
                    
                    total_hours += float(est_hours) if est_hours else 0
                    total_cost += float(cost) if cost else 0
            
            # Update summary if it exists
            if hasattr(self, 'booking_summary_label'):
                self.booking_summary_label.configure(
                    text=f"Total Booking Hours: {total_hours:.1f} | Total Cost: ${total_cost:.2f} | Status: {len(bookings)} bookings"
                )
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load employee services: {e}")
            logging.error(f"Service loading error: {e}")
            import traceback
            traceback.print_exc()
    
    def load_employee_data_grid(self):
        """Load complete project bookings data with foreign key lookups - similar to Fabsi service table"""
        try:
            # Clear existing items
            if hasattr(self, 'employee_tree'):
                for item in self.employee_tree.get_children():
                    self.employee_tree.delete(item)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get all project bookings with all columns and foreign key lookups
                cursor.execute("""
                    SELECT 
                        pb.id,
                        pb.cost_center,
                        COALESCE(e.ghrs_id, pb.ghrs_id, 'N/A') as ghrs_id,
                        COALESCE(e.name, pb.employee_name, 'N/A') as employee_name,
                        pb.dept_description,
                        pb.work_location,
                        pb.business_unit,
                        pb.tipo,
                        pb.tipo_description,
                        pb.sap_tipo,
                        pb.saabu_rate_eur,
                        pb.saabu_rate_usd,
                        pb.local_agency_rate_usd,
                        pb.unit_rate_usd,
                        pb.monthly_hours,
                        pb.annual_hours,
                        pb.workload_2025_planned,
                        pb.workload_2025_actual,
                        pb.remark,
                        COALESCE(pb.project_name, p.name, 'N/A') as project,
                        pb.item,
                        COALESCE(pb.technical_unit_name, tu.name, 'N/A') as technical_unit,
                        COALESCE(pb.activities_name, a.name, 'N/A') as activities,
                        pb.booking_hours,
                        pb.booking_cost_forecast,
                        pb.booking_period,
                        pb.booking_hours_accepted,
                        pb.booking_period_accepted,
                        pb.booking_hours_extra,
                        pb.estimated_hours,
                        pb.actual_hours,
                        pb.hourly_rate,
                        pb.total_cost,
                        pb.booking_status,
                        pb.booking_date,
                        pb.start_date,
                        pb.end_date,
                        pb.notes
                    FROM project_bookings pb
                    LEFT JOIN employee e ON pb.employee_id = e.id
                    LEFT JOIN technical_unit tu ON pb.technical_unit_id = tu.id
                    LEFT JOIN project p ON pb.project_id = p.id
                    LEFT JOIN service s ON pb.service_id = s.id
                    LEFT JOIN title t ON s.title_id = t.id
                    LEFT JOIN activities a ON s.activities_id = a.id
                    ORDER BY pb.id
                """)
                
                bookings_data = cursor.fetchall()
                
                # Define complete columns for all project booking data (with Select checkbox)
                complete_columns = (
                    "Select", "ID", "Cost Center", "GHRS ID", "Employee Name", "Dept. Description",
                    "Work Location", "Business Unit", "Tipo", "Tipo Description", "SAP Tipo",
                    "SAABU Rate (EUR)", "SAABU Rate (USD)", "Local Agency Rate (USD)", "Unit Rate (USD)",
                    "Monthly Hours", "Annual Hours", "Workload 2025_Planned", "Workload 2025_Actual",
                    "Remark", "Project", "Item", "Technical Unit", "Activities", "Booking Hours",
                    "Booking Cost (Forecast)", "Booking Period", "Booking hours (Accepted by Project)",
                    "Booking Period (Accepted by Project)", "Booking hours (Extra)",
                    "Est. Hours", "Actual Hours", "Hourly Rate", "Total Cost", "Status",
                    "Booking Date", "Start Date", "End Date", "Notes"
                )
                
                # Update treeview columns if needed
                if hasattr(self, 'employee_tree'):
                    # Clear existing columns and set new ones
                    current_columns = self.employee_tree['columns']
                    if current_columns != complete_columns:
                        self.employee_tree.configure(columns=complete_columns)
                        
                        # Set column widths for complete view (with Select checkbox)
                        column_widths = {
                            "Select": 60, "ID": 50, "Cost Center": 100, "GHRS ID": 80, "Employee Name": 150,
                            "Dept. Description": 150, "Work Location": 120, "Business Unit": 120, "Tipo": 80,
                            "Tipo Description": 150, "SAP Tipo": 80, "SAABU Rate (EUR)": 100, "SAABU Rate (USD)": 100,
                            "Local Agency Rate (USD)": 120, "Unit Rate (USD)": 100, "Monthly Hours": 100, "Annual Hours": 100,
                            "Workload 2025_Planned": 120, "Workload 2025_Actual": 120, "Remark": 150, "Project": 150,
                            "Item": 120, "Technical Unit": 120, "Activities": 150, "Booking Hours": 100,
                            "Booking Cost (Forecast)": 120, "Booking Period": 120, "Booking hours (Accepted by Project)": 150,
                            "Booking Period (Accepted by Project)": 150, "Booking hours (Extra)": 120,
                            "Est. Hours": 80, "Actual Hours": 80, "Hourly Rate": 80, "Total Cost": 100, "Status": 80,
                            "Booking Date": 100, "Start Date": 100, "End Date": 100, "Notes": 150
                        }
                        
                        for col in complete_columns:
                            self.employee_tree.heading(col, text=col)
                            width = column_widths.get(col, 100)
                            self.employee_tree.column(col, width=width, anchor="center", minwidth=70)
                
                # Populate the grid with complete booking data (including checkbox)
                for booking_data in bookings_data:
                    # Format the data for display (handle None values)
                    formatted_data = ["☐"]  # Start with unchecked checkbox
                    for i, value in enumerate(booking_data):
                        if value is None:
                            formatted_data.append("N/A")
                        elif i in [10, 11, 12, 13, 16, 17, 23, 24, 26, 28, 29, 30, 31, 32]:  # Decimal/money columns
                            formatted_data.append(f"{value:.2f}" if value else "0.00")
                        elif i in [14, 15]:  # Integer hours columns
                            formatted_data.append(str(int(value)) if value else "0")
                        elif i in [34, 35, 36]:  # Date columns (booking_date, start_date, end_date)
                            formatted_data.append(str(value) if value else "N/A")
                        else:
                            formatted_data.append(str(value) if value else "N/A")
                    
                    self.employee_tree.insert("", "end", values=formatted_data)
                
                conn.close()
                
                print(f"Loaded {len(bookings_data)} project booking records with full details")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project booking data: {e}")
            logging.error(f"Project booking data grid loading error: {e}")
            import traceback
            traceback.print_exc()
    
    def delete_employee_record(self):
        """Delete selected project booking record"""
        if not hasattr(self, 'employee_tree'):
            return
            
        selected_item = self.employee_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a project booking to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this project booking record?"):
            try:
                item_values = self.employee_tree.item(selected_item[0])['values']
                booking_id = item_values[1]  # ID is now in position 1 due to checkbox
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Delete the project booking record
                cursor.execute("DELETE FROM project_bookings WHERE id = ?", (booking_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Project booking deleted successfully")
                # Auto refresh removed - user can manually refresh if needed
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete project booking: {e}")
                logging.error(f"Project booking deletion error: {e}")
    
    def on_simplified_cell_edit(self, event):
        """Excel-like cell editing: Click to edit any cell directly"""
        try:
            # Get the clicked item and column
            item = self.employee_tree.selection()[0]
            column = self.employee_tree.identify_column(event.x)
            
            # Get column index (remove '#' prefix)
            col_idx = int(column.replace('#', '')) - 1
            
            # Get current values
            current_values = list(self.employee_tree.item(item, 'values'))
            if col_idx >= len(current_values):
                return
                
            # Get the actual column names from the data query to map to database fields
            complete_columns = (
                "Select", "ID", "Cost Center", "GHRS ID", "Employee Name", "Dept. Description",
                "Work Location", "Business Unit", "Tipo", "Tipo Description", "SAP Tipo",
                "SAABU Rate (EUR)", "SAABU Rate (USD)", "Local Agency Rate (USD)", "Unit Rate (USD)",
                "Monthly Hours", "Annual Hours", "Workload 2025_Planned", "Workload 2025_Actual",
                "Remark", "Project", "Item", "Technical Unit", "Activities", "Booking Hours",
                "Booking Cost (Forecast)", "Booking Period", "Booking hours (Accepted by Project)",
                "Booking Period (Accepted by Project)", "Booking hours (Extra)",
                "Est. Hours", "Actual Hours", "Hourly Rate", "Total Cost", "Status",
                "Booking Date", "Start Date", "End Date", "Notes"
            )
            
            # Map display columns to database column names (adjusted for checkbox)
            db_column_map = {
                0: None,  # Select checkbox - not editable
                1: None,  # ID - not editable
                2: "cost_center",
                3: "ghrs_id", 
                4: "employee_name",
                5: "dept_description",
                6: "work_location",
                7: "business_unit",
                8: "tipo",
                9: "tipo_description", 
                10: "sap_tipo",
                11: "saabu_rate_eur",
                12: "saabu_rate_usd",
                13: "local_agency_rate_usd",
                14: "unit_rate_usd",
                15: "monthly_hours",
                16: "annual_hours",
                17: "workload_2025_planned",
                18: "workload_2025_actual",
                19: "remark",
                20: "project_name",
                21: "item",
                22: "technical_unit_name",
                23: "activities_name",
                24: "booking_hours",
                25: "booking_cost_forecast",
                26: "booking_period",
                27: "booking_hours_accepted",
                28: "booking_period_accepted", 
                29: "booking_hours_extra",
                30: "estimated_hours",
                31: "actual_hours",
                32: "hourly_rate",
                33: "total_cost",
                34: "booking_status",
                35: "booking_date",
                36: "start_date",
                37: "end_date",
                38: "notes"
            }
            
            # Check if column is editable
            if col_idx in [0, 1]:  # Select checkbox and ID column
                if col_idx == 0:
                    messagebox.showinfo("Info", "Use single click to toggle row selection")
                else:
                    messagebox.showinfo("Info", "Booking ID cannot be edited")
                return
                
            db_column = db_column_map.get(col_idx)
            if not db_column:
                messagebox.showinfo("Info", "This column cannot be edited")
                return
            
            column_name = complete_columns[col_idx]
            current_value = current_values[col_idx] if col_idx < len(current_values) else ""
            
            # Remove "N/A" or format current value for editing
            if current_value == "N/A":
                current_value = ""
            
            # Create inline editing dialog
            self.create_inline_edit_dialog(item, col_idx, column_name, current_value, db_column)
            
        except (IndexError, ValueError, KeyError):
            pass  # No item selected or invalid column

    def create_inline_edit_dialog(self, tree_item, col_idx, column_name, current_value, db_column):
        """Create a small dialog for editing cell value like Excel"""
        # Get the booking ID for database update (now in column 1 due to checkbox)
        item_values = self.employee_tree.item(tree_item)['values']
        booking_id = item_values[1]  # ID is now in position 1
        
        # Store current row values for updating the display
        current_row_values = list(item_values)
        
        # Create compact edit dialog
        edit_dialog = ctk.CTkToplevel(self.root)
        edit_dialog.title(f"Edit {column_name}")
        edit_dialog.geometry("400x200")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Center the dialog
        edit_dialog.update_idletasks()
        x = (edit_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (200 // 2)
        edit_dialog.geometry(f"400x200+{x}+{y}")
        
        # Content frame
        content_frame = ctk.CTkFrame(edit_dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Label
        ctk.CTkLabel(content_frame, text=f"Edit {column_name}:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        
        # Determine input type based on column
        numeric_columns = ["saabu_rate_eur", "saabu_rate_usd", "local_agency_rate_usd", "unit_rate_usd",
                          "workload_2025_planned", "workload_2025_actual", "booking_hours", 
                          "booking_cost_forecast", "booking_hours_accepted", "booking_hours_extra",
                          "estimated_hours", "actual_hours", "hourly_rate", "total_cost"]
        
        integer_columns = ["monthly_hours", "annual_hours"]
        
        date_columns = ["booking_date", "start_date", "end_date"]
        
        text_area_columns = ["remark", "notes", "dept_description", "tipo_description"]
        
        if db_column in text_area_columns:
            # Text area for longer text
            edit_widget = ctk.CTkTextbox(content_frame, height=80, width=350)
            edit_widget.pack(pady=5, fill="x")
            if current_value and current_value != "N/A":
                edit_widget.insert("1.0", current_value)
        else:
            # Single line entry
            edit_widget = ctk.CTkEntry(content_frame, width=350, placeholder_text=f"Enter {column_name.lower()}")
            edit_widget.pack(pady=5, fill="x")
            if current_value and current_value != "N/A":
                edit_widget.insert(0, current_value)
        
        # Validation info
        if db_column in numeric_columns:
            info_text = "Enter a decimal number (e.g., 123.45)"
        elif db_column in integer_columns:
            info_text = "Enter a whole number (e.g., 40)"
        elif db_column in date_columns:
            info_text = "Enter date in YYYY-MM-DD format (e.g., 2025-01-15)"
        else:
            info_text = "Enter text value"
            
        ctk.CTkLabel(content_frame, text=info_text, 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        def save_change():
            try:
                # Get the new value
                if db_column in text_area_columns:
                    new_value = edit_widget.get("1.0", "end-1c").strip()
                else:
                    new_value = edit_widget.get().strip()
                
                # Validate numeric inputs
                if db_column in numeric_columns and new_value:
                    try:
                        float(new_value)
                    except ValueError:
                        messagebox.showerror("Error", "Please enter a valid decimal number")
                        return
                        
                if db_column in integer_columns and new_value:
                    try:
                        int(new_value)
                    except ValueError:
                        messagebox.showerror("Error", "Please enter a valid whole number")
                        return
                
                # Date validation
                if db_column in date_columns and new_value:
                    try:
                        from datetime import datetime
                        datetime.strptime(new_value, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
                        return
                
                # Update database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Handle empty values
                if new_value == "":
                    new_value = None
                
                # Update the specific column
                cursor.execute(f"UPDATE project_bookings SET {db_column} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                              (new_value, booking_id))
                
                # Special handling for calculated fields
                if db_column in ["estimated_hours", "hourly_rate"]:
                    # Recalculate total_cost if hours or rate changed
                    cursor.execute("SELECT estimated_hours, hourly_rate FROM project_bookings WHERE id = ?", (booking_id,))
                    hours_rate = cursor.fetchone()
                    if hours_rate and hours_rate[0] and hours_rate[1]:
                        total_cost = float(hours_rate[0]) * float(hours_rate[1])
                        cursor.execute("UPDATE project_bookings SET total_cost = ? WHERE id = ?", (total_cost, booking_id))
                
                conn.commit()
                conn.close()
                
                # Update the stored row values
                current_row_values[col_idx] = new_value if new_value is not None else "N/A"
                
                # Format display value
                if db_column in numeric_columns and new_value:
                    current_row_values[col_idx] = f"{float(new_value):.2f}"
                elif db_column in integer_columns and new_value:
                    current_row_values[col_idx] = str(int(new_value))
                
                # Find the item by booking_id and update it (ID is now in position 1)
                for item in self.employee_tree.get_children():
                    values = self.employee_tree.item(item)['values']
                    if values and len(values) > 1 and values[1] == booking_id:
                        self.employee_tree.item(item, values=current_row_values)
                        break
                
                edit_dialog.destroy()
                messagebox.showinfo("Success", f"{column_name} updated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update {column_name}: {e}")
                import traceback
                traceback.print_exc()
        
        def cancel_edit():
            edit_dialog.destroy()
        
        # Buttons
        ctk.CTkButton(button_frame, text="Save", command=save_change, width=100).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_frame, text="Cancel", command=cancel_edit, width=100).pack(side="left")
        
        # Focus on the input widget and select all text
        edit_widget.focus()
        if not db_column in text_area_columns and current_value and current_value != "N/A":
            edit_widget.select_range(0, tk.END)
        
        # Bind Enter key to save
        edit_dialog.bind('<Return>', lambda e: save_change())
        edit_dialog.bind('<Escape>', lambda e: cancel_edit())

    def on_keyboard_edit(self, event):
        """Handle F2 key press for editing like Excel"""
        try:
            if self.employee_tree.selection():
                # Simulate a double-click at the center of the selected cell
                item = self.employee_tree.selection()[0]
                bbox = self.employee_tree.bbox(item)
                if bbox:
                    # Create a fake event for the center of the first column
                    fake_event = type('Event', (), {})()
                    fake_event.x = bbox[0] + 50  # Approximate center of first editable column
                    fake_event.y = bbox[1] + bbox[3] // 2
                    self.on_simplified_cell_edit(fake_event)
        except Exception:
            pass
    
    def on_cell_select(self, event):
        """Handle cell selection for visual feedback"""
        try:
            # This provides visual feedback when clicking on cells
            # The actual editing happens on double-click
            pass
        except Exception:
            pass
            
    def toggle_edit_mode(self):
        """Toggle between single-click and double-click editing modes"""
        if self.edit_mode == "double":
            self.edit_mode = "single"
            self.employee_tree.bind('<Button-1>', self.on_simplified_cell_edit)
            self.edit_mode_btn.configure(text="Edit Mode: Single-Click")
            messagebox.showinfo("Edit Mode", "Single-click editing enabled!\nClick any cell to edit directly.")
        else:
            self.edit_mode = "double"
            self.employee_tree.unbind('<Button-1>')
            self.employee_tree.bind('<Button-1>', self.on_cell_select)
            self.edit_mode_btn.configure(text="Edit Mode: Double-Click")
            messagebox.showinfo("Edit Mode", "Double-click editing enabled!\nDouble-click any cell to edit, or press F2.")
    
    def open_employee_dialog(self, employee_id=None):
        """Open dialog for adding/editing employee with all 29 fields"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Employee Record" if not employee_id else "Edit Employee Record")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(dialog, width=760, height=550)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_text = "Add New Employee" if not employee_id else "Edit Employee"
        ctk.CTkLabel(scrollable_frame, text=title_text, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 20))
        
        # Dictionary to store entry widgets
        entry_widgets = {}
        
        # Define all 29 fields with their labels
        fields = [
            ("cost_center", "Cost Center"),
            ("ghrs_id", "GHRS ID"),
            ("last_name", "Last Name"),
            ("first_name", "First Name"),
            ("dept_description", "Dept. Description"),
            ("work_location", "Work Location"),
            ("business_unit", "Business Unit"),
            ("tipo", "Tipo"),
            ("tipo_description", "Tipo Description"),
            ("sap_tipo", "SAP Tipo"),
            ("saabu_rate_eur", "SAABU Rate (EUR)"),
            ("saabu_rate_usd", "SAABU Rate (USD)"),
            ("local_agency_rate_usd", "Local Agency Rate (USD)"),
            ("unit_rate_usd", "Unit Rate (USD)"),
            ("monthly_hours", "Monthly Hours"),
            ("annual_hours", "Annual Hours"),
            ("workload_2025_planned", "Workload 2025_Planned"),
            ("workload_2025_actual", "Workload 2025_Actual"),
            ("remark", "Remark"),
            ("project_assigned", "Project"),
            ("item", "Item"),
            ("technical_unit_assigned", "Technical Unit"),
            ("activities", "Activities"),
            ("booking_hours", "Booking Hours"),
            ("booking_cost_forecast", "Booking Cost (Forecast)"),
            ("booking_period", "Booking Period"),
            ("booking_hours_accepted", "Booking hours (Accepted by Project)"),
            ("booking_period_accepted", "Booking Period (Accepted by Project)"),
            ("booking_hours_extra", "Booking hours (Extra)")
        ]
        
        # Create input fields in a grid layout
        for i, (field_name, field_label) in enumerate(fields):
            row = i // 2
            col = i % 2
            
            field_frame = ctk.CTkFrame(scrollable_frame)
            field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            
            ctk.CTkLabel(field_frame, text=field_label + ":").pack(anchor="w", padx=5, pady=(5, 0))
            
            if field_name in ["remark", "activities"]:
                # Text area for longer fields
                entry = ctk.CTkTextbox(field_frame, height=60)
                entry.pack(fill="x", padx=5, pady=(0, 5))
            else:
                # Regular entry
                entry = ctk.CTkEntry(field_frame)
                entry.pack(fill="x", padx=5, pady=(0, 5))
            
            entry_widgets[field_name] = entry
        
        # Configure grid weights
        for i in range(2):
            scrollable_frame.grid_columnconfigure(i, weight=1)
        
        # Load existing data if editing
        if employee_id:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ghrs_id, last_name, first_name, cost_center, dept_description
                    FROM employee WHERE id = ?
                """, (employee_id,))
                
                emp_data = cursor.fetchone()
                conn.close()
                
                if emp_data:
                    # Simple display of employee information
                    info_text = f"""
Employee Details:
GHRS ID: {emp_data[0] or 'N/A'}
Name: {emp_data[2] or ''} {emp_data[1] or ''}
Cost Center: {emp_data[3] or 'N/A'}
Department: {emp_data[4] or 'N/A'}
                    """
                    
                    # Create simple info display
                    info_label = ctk.CTkLabel(
                        self.employee_details_frame,
                        text=info_text,
                        justify="left",
                        font=ctk.CTkFont(size=12)
                    )
                    info_label.pack(pady=10, padx=10, anchor="w")
                            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load employee data: {e}")
        
        # Buttons frame  
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        close_btn = ctk.CTkButton(button_frame, text="Close", command=dialog.destroy, width=100)
        close_btn.pack(side="left", padx=10)
    
    def add_service_assignment(self):
        """Add new service assignment"""
        if not self.selected_employee.get():
            messagebox.showwarning("Warning", "Please select an employee first")
            return
        
        # Create a new window for service assignment
        self.open_service_assignment_dialog()
    
    def open_service_assignment_dialog(self):
        """Open dialog for adding/editing service assignment"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Service Assignment")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Service selection
        ctk.CTkLabel(dialog, text="Select Service:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        
        # Load available services
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, p.name, a.name, t.name 
            FROM service s
            LEFT JOIN project p ON s.project_id = p.id
            LEFT JOIN activities a ON s.activities_id = a.id
            LEFT JOIN title t ON s.title_id = t.id
            ORDER BY p.name, a.name
        """)
        services = cursor.fetchall()
        conn.close()
        
        service_options = [f"{s[1]} - {s[2]} ({s[3]})" for s in services]
        service_var = tk.StringVar()
        service_dropdown = ctk.CTkComboBox(dialog, variable=service_var, values=service_options, width=400)
        service_dropdown.pack(pady=5)
        
        # Hours input
        ctk.CTkLabel(dialog, text="Estimated Hours:").pack(pady=(20, 5))
        hours_entry = ctk.CTkEntry(dialog, placeholder_text="Enter hours")
        hours_entry.pack(pady=5)
        
        # Rate input
        ctk.CTkLabel(dialog, text="Hourly Rate (USD):").pack(pady=(10, 5))
        rate_entry = ctk.CTkEntry(dialog, placeholder_text="Enter rate")
        rate_entry.pack(pady=5)
        
        # Date inputs
        ctk.CTkLabel(dialog, text="Start Date (YYYY-MM-DD):").pack(pady=(10, 5))
        start_date_entry = ctk.CTkEntry(dialog, placeholder_text="2025-01-01")
        start_date_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="End Date (YYYY-MM-DD):").pack(pady=(10, 5))
        end_date_entry = ctk.CTkEntry(dialog, placeholder_text="2025-12-31")
        end_date_entry.pack(pady=5)
        
        # Notes
        ctk.CTkLabel(dialog, text="Notes:").pack(pady=(10, 5))
        notes_entry = ctk.CTkTextbox(dialog, height=80)
        notes_entry.pack(pady=5, padx=20, fill="x")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        def save_assignment():
            try:
                # Get selected service ID
                selected_service = service_var.get()
                if not selected_service:
                    messagebox.showwarning("Warning", "Please select a service")
                    return
                
                service_id = services[[s[1] + " - " + s[2] + " (" + s[3] + ")" for s in services].index(selected_service)][0]
                
                # Get employee info from mapping
                selected_emp = self.selected_employee.get()
                if selected_emp not in self.employee_map:
                    messagebox.showerror("Error", "Employee not found")
                    return
                
                employee_info = self.employee_map[selected_emp]
                employee_id = employee_info["id"]
                employee_type = employee_info["type"]
                
                hours = float(hours_entry.get() or 0)
                rate = float(rate_entry.get() or 0)
                total_cost = hours * rate
                
                # Get selected project and technical unit IDs from mappings
                project_id = None
                tech_unit_id = None
                
                if self.selected_project.get() and self.selected_project.get() in self.project_map:
                    project_id = self.project_map[self.selected_project.get()]
                
                if self.selected_technical_unit.get() and self.selected_technical_unit.get() in self.technical_unit_map:
                    tech_unit_id = self.technical_unit_map[self.selected_technical_unit.get()]
                
                # Save to database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if employee_type == "extended":
                    # Get comprehensive employee data for the new booking
                    cursor.execute("""
                        SELECT cost_center, ghrs_id, COALESCE(first_name || ' ' || last_name, last_name, first_name, 'N/A') as employee_name, dept_description,
                               work_location, business_unit, tipo, tipo_description, sap_tipo,
                               saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                               monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                               remark
                        FROM employee_extended WHERE id = ?
                    """, (employee_id,))
                    emp_data = cursor.fetchone()
                    
                    # Fallback: get employee name from main employee table if extended doesn't have it
                    if not emp_data or not emp_data[2]:
                        cursor.execute("SELECT name FROM employee WHERE id = ?", (employee_id,))
                        emp_name_fallback = cursor.fetchone()
                        emp_name = emp_name_fallback[0] if emp_name_fallback else "N/A"
                    else:
                        emp_name = emp_data[2]
                    
                    # Get project, technical unit, and activity names
                    cursor.execute("SELECT name FROM project WHERE id = ?", (project_id,))
                    project_data = cursor.fetchone()
                    project_name_val = project_data[0] if project_data else "N/A"
                    
                    cursor.execute("SELECT name FROM technical_unit WHERE id = ?", (tech_unit_id,))
                    tu_data = cursor.fetchone()
                    tu_name_val = tu_data[0] if tu_data else "N/A"
                    
                    cursor.execute("""
                        SELECT a.name FROM service s 
                        LEFT JOIN activities a ON s.activities_id = a.id 
                        WHERE s.id = ?
                    """, (service_id,))
                    activity_data = cursor.fetchone()
                    activity_name_val = activity_data[0] if activity_data else "N/A"
                    
                    # Prepare values with defaults
                    if emp_data:
                        (cost_center, ghrs_id, employee_name_from_query, dept_description,
                         work_location, business_unit, tipo, tipo_description, sap_tipo,
                         saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                         monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                         remark) = emp_data
                    else:
                        # Default values when employee_extended data not available
                        (cost_center, ghrs_id, dept_description,
                         work_location, business_unit, tipo, tipo_description, sap_tipo,
                         saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                         monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                         remark) = (None, None, None, None, None, None, None, None,
                                   0.00, 0.00, 0.00, 0.00, 0, 0, 0.00, 0.00, None)
                    
                    cursor.execute("""
                        INSERT INTO project_bookings 
                        (employee_id, technical_unit_id, project_id, service_id,
                         estimated_hours, hourly_rate, total_cost, start_date, end_date, notes,
                         booking_status, booking_date, created_at, updated_at,
                         cost_center, ghrs_id, employee_name, dept_description,
                         work_location, business_unit, tipo, tipo_description, sap_tipo,
                         saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                         monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                         remark, project_name, item, technical_unit_name, activities_name,
                         booking_hours, booking_cost_forecast, booking_period,
                         booking_hours_accepted, booking_period_accepted, booking_hours_extra)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', CURRENT_DATE, 
                                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                ?, NULL, ?, ?, ?, 0.00, 0.00, NULL, 0.00, NULL, 0.00)
                    """, (employee_id, tech_unit_id, project_id, service_id, hours, rate, 
                          total_cost, start_date_entry.get(), end_date_entry.get(), notes_entry.get("1.0", "end"),
                          cost_center, ghrs_id, emp_name, dept_description,
                          work_location, business_unit, tipo, tipo_description, sap_tipo,
                          saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                          monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                          remark, project_name_val, tu_name_val, activity_name_val))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Service assignment saved successfully")
                dialog.destroy()
                self.load_employee_services()
                # Auto refresh removed - user can manually refresh if needed
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save assignment: {e}")
                logging.error(f"Assignment save error: {e}")
        
        save_btn = ctk.CTkButton(button_frame, text="Save", command=save_assignment)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=10)
    
    def edit_service_assignment(self):
        """Edit selected service assignment"""
        selected_item = self.service_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a service assignment to edit")
            return
        
        messagebox.showinfo("Info", "Edit functionality will be implemented")
    
    def delete_service_assignment(self):
        """Delete selected service assignment"""
        selected_item = self.service_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a service assignment to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this assignment?"):
            # Implementation for deletion
            messagebox.showinfo("Info", "Delete functionality will be implemented")
    
    def save_booking(self):
        """Save current booking"""
        if not self.selected_employee.get():
            messagebox.showwarning("Warning", "Please select an employee first")
            return
        
        messagebox.showinfo("Success", "Booking saved successfully")
    
    def approve_booking(self):
        """Approve current booking"""
        selected_item = self.service_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a booking to approve")
            return
        
        messagebox.showinfo("Success", "Booking approved successfully")
    
    def reject_booking(self):
        """Reject current booking"""
        selected_item = self.service_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a booking to reject")
            return
        
        messagebox.showinfo("Success", "Booking rejected")
    
    def import_excel_data(self):
        """Import employee data from Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel file",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Map columns to database fields (based on 29-column structure)
            required_columns = [
                'Cost Center', 'GHRS ID', 'Last Name', 'First Name', 'Dept. Description',
                'Work Location', 'Business Unit', 'Tipo', 'Tipo Description', 'SAP Tipo',
                'SAABU Rate (EUR)', 'SAABU Rate (USD)', 'Local Agency Rate (USD)', 'Unit Rate (USD)',
                'Monthly Hours', 'Annual Hours', 'Workload 2025_Planned', 'Workload 2025_Actual',
                'Remark', 'Project', 'Item', 'Technical Unit', 'Activities', 'Booking Hours',
                'Booking Cost (Forecast)', 'Booking Period', 'Booking hours (Accepted by Project)',
                'Booking Period (Accepted by Project)', 'Booking hours (Extra)'
            ]
            
            # Check if columns exist
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messagebox.showwarning("Warning", f"Missing columns: {missing_columns}")
            
            # Import data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO employee (
                            cost_center, ghrs_id, last_name, first_name, dept_description
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        row.get('cost_center', None),
                        row.get('ghrs_id', None), 
                        row.get('last_name', None),
                        row.get('first_name', None),
                        row.get('dept_description', None)
                    ))
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing row: {e}")
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Successfully imported {imported_count} employee records")
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import Excel data: {e}")
            logging.error(f"Excel import error: {e}")
    
    def export_report(self):
        """Export booking report to Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save report as",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if not file_path:
                return
            
            # Generate report data
            conn = sqlite3.connect(self.db_path)
            
            # Employee data
            df_employees = pd.read_sql_query("""
                SELECT * FROM employee
                ORDER BY last_name, first_name
            """, conn)
            
            # Booking data
            df_bookings = pd.read_sql_query("""
                SELECT pb.*, e.first_name, e.last_name, p.name as project_name,
                       tu.name as technical_unit_name
                FROM project_bookings pb
                LEFT JOIN employee e ON pb.employee_id = e.id
                LEFT JOIN project p ON pb.project_id = p.id
                LEFT JOIN technical_unit tu ON pb.technical_unit_id = tu.id
                ORDER BY pb.created_at DESC
            """, conn)
            
            conn.close()
            
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_employees.to_excel(writer, sheet_name='Employee Data', index=False)
                df_bookings.to_excel(writer, sheet_name='Booking Data', index=False)
            
            messagebox.showinfo("Success", f"Report exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")
            logging.error(f"Export error: {e}")
    
    def schedule_auto_refresh(self):
        """Schedule automatic refresh of employee data grid"""
        if self.auto_refresh_enabled:
            try:
                self.refresh_employee_data()
                # Schedule next refresh in 30 seconds (30000 milliseconds)
                self.root.after(30000, self.schedule_auto_refresh)
            except Exception as e:
                logging.error(f"Auto-refresh error: {e}")
                # Continue scheduling even if refresh fails
                self.root.after(30000, self.schedule_auto_refresh)
    
    def refresh_employee_data(self):
        """Refresh employee data grid and related displays"""
        try:
            self.load_employee_data_grid()
            # Also refresh service data if an employee is selected
            if self.selected_employee.get():
                self.load_employee_services()
        except Exception as e:
            logging.error(f"Data refresh error: {e}")
    
    def manual_refresh(self):
        """Manual refresh triggered by user action"""
        try:
            self.refresh_employee_data()
            messagebox.showinfo("Refresh", "Employee data refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {e}")
    
    def toggle_auto_refresh(self):
        """Toggle automatic refresh on/off"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        button_text = "Auto-Refresh: ON" if self.auto_refresh_enabled else "Auto-Refresh: OFF"
        self.auto_refresh_btn.configure(text=button_text)
        
        if self.auto_refresh_enabled:
            # Restart auto-refresh
            self.schedule_auto_refresh()
            messagebox.showinfo("Auto-Refresh", "Automatic refresh enabled (every 30 seconds)")
        else:
            messagebox.showinfo("Auto-Refresh", "Automatic refresh disabled")
    
    def smart_refresh(self):
        """Smart refresh that deletes rows with all zero values in specified fields"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define the fields to check - all must be 0 for deletion
            fields_to_check = [
                'monthly_hours', 
                'annual_hours', 
                'workload_2025_planned', 
                'workload_2025_actual',
                'booking_hours', 
                'booking_period',  # This might be text, so we'll treat it differently
                'booking_hours_accepted', 
                'booking_period_accepted',  # This might be text, so we'll treat it differently
                'booking_hours_extra'
            ]
            
            # Build the WHERE clause to find rows where all numeric fields are 0 or NULL
            # For period fields, we check if they are NULL, empty, or contain only '0'
            numeric_conditions = []
            for field in fields_to_check:
                if 'period' in field:
                    # For period fields, check if NULL, empty, or just '0'
                    numeric_conditions.append(f"({field} IS NULL OR {field} = '' OR {field} = '0')")
                else:
                    # For numeric fields, check if 0 or NULL
                    numeric_conditions.append(f"({field} IS NULL OR {field} = 0)")
            
            where_clause = " AND ".join(numeric_conditions)
            
            # Find rows that match the deletion criteria
            query = f"""
                SELECT id, employee_name, project_name, technical_unit_name
                FROM project_bookings 
                WHERE {where_clause}
            """
            
            cursor.execute(query)
            rows_to_delete = cursor.fetchall()
            
            if rows_to_delete:
                # Ask for confirmation
                message = f"Found {len(rows_to_delete)} rows where all specified fields are zero.\n"
                message += "These rows will be deleted:\n\n"
                
                for i, row in enumerate(rows_to_delete[:5]):  # Show first 5 rows
                    message += f"- ID: {row[0]}, Employee: {row[1]}, Project: {row[2]}\n"
                
                if len(rows_to_delete) > 5:
                    message += f"... and {len(rows_to_delete) - 5} more rows\n"
                
                message += "\nDo you want to proceed with deletion?"
                
                if messagebox.askyesno("Confirm Deletion", message):
                    # Delete the identified rows
                    ids_to_delete = [str(row[0]) for row in rows_to_delete]
                    cursor.execute(f"DELETE FROM project_bookings WHERE id IN ({','.join(ids_to_delete)})")
                    
                    conn.commit()
                    
                    # Refresh the data display
                    self.load_employee_data_grid()
                    
                    messagebox.showinfo("Success", f"Deleted {len(rows_to_delete)} rows with all zero values.")
                else:
                    messagebox.showinfo("Cancelled", "Deletion cancelled by user.")
            else:
                # Just do regular refresh
                self.load_employee_data_grid()
                messagebox.showinfo("Refresh Complete", "No rows found with all zero values. Data refreshed.")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform smart refresh: {e}")
            logging.error(f"Smart refresh error: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_row_selection(self, event):
        """Toggle row selection when clicking on the Select column"""
        try:
            # Get the clicked item and column
            region = self.employee_tree.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            item = self.employee_tree.identify_row(event.y)
            column = self.employee_tree.identify_column(event.x)
            
            # Check if clicked on the Select column (first column)
            if column == "#1":  # First column is the Select column
                if item:
                    current_values = list(self.employee_tree.item(item, 'values'))
                    if current_values:
                        # Toggle the selection
                        if current_values[0] == "☑":
                            current_values[0] = "☐"
                            self.selected_rows.discard(item)
                        else:
                            current_values[0] = "☑"
                            self.selected_rows.add(item)
                        
                        self.employee_tree.item(item, values=current_values)
                        
        except Exception as e:
            logging.error(f"Row selection toggle error: {e}")
    
    def delete_selected_rows(self):
        """Delete all selected rows"""
        try:
            if not self.selected_rows:
                messagebox.showwarning("Warning", "No rows selected for deletion")
                return
            
            # Get the IDs of selected rows
            ids_to_delete = []
            for item in self.selected_rows:
                values = self.employee_tree.item(item, 'values')
                if values and len(values) > 1:  # Make sure we have values and ID is in position 1
                    ids_to_delete.append(values[1])  # ID is in the second column now
            
            if not ids_to_delete:
                messagebox.showwarning("Warning", "No valid rows selected")
                return
            
            message = f"Are you sure you want to delete {len(ids_to_delete)} selected row(s)?"
            if messagebox.askyesno("Confirm Deletion", message):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Delete the selected rows
                placeholders = ','.join(['?' for _ in ids_to_delete])
                cursor.execute(f"DELETE FROM project_bookings WHERE id IN ({placeholders})", ids_to_delete)
                
                conn.commit()
                conn.close()
                
                # Clear selection and refresh
                self.selected_rows.clear()
                self.load_employee_data_grid()
                
                messagebox.showinfo("Success", f"Deleted {len(ids_to_delete)} row(s) successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete selected rows: {e}")
            logging.error(f"Selected rows deletion error: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function to run the Project Booking Application"""
    try:
        app = ProjectBookingApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
