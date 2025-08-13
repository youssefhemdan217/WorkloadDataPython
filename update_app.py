import re

def update_project_booking_app():
    """
    Update project_booking_app.py to remove references to estimated_hours and notes columns
    """
    
    # Read the current file
    with open('project_booking_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track all changes made
    changes_made = []
    
    # 1. Remove estimated_hours from table creation SQL
    old_create_table = '''CREATE TABLE IF NOT EXISTS project_bookings (
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
                    )'''
    
    new_create_table = '''CREATE TABLE IF NOT EXISTS project_bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        technical_unit_id INTEGER,
                        project_id INTEGER,
                        service_id INTEGER,
                        actual_hours DECIMAL(10,2),
                        hourly_rate DECIMAL(10,2),
                        total_cost DECIMAL(10,2),
                        booking_status VARCHAR(50) DEFAULT 'Pending',
                        booking_date DATE,
                        start_date DATE,
                        end_date DATE,
                        created_by VARCHAR(100),
                        approved_by VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employee (id),
                        FOREIGN KEY (technical_unit_id) REFERENCES technical_unit (id),
                        FOREIGN KEY (project_id) REFERENCES project (id),
                        FOREIGN KEY (service_id) REFERENCES service (id)
                    )'''
    
    if old_create_table in content:
        content = content.replace(old_create_table, new_create_table)
        changes_made.append("Updated CREATE TABLE project_bookings")
    
    # 2. Update SQL queries that select estimated_hours and notes
    
    # Query 1: In load_services_for_employee
    old_query1 = '''SELECT pb.id, p.name as project_name, 
                       COALESCE(a.name, 'Unknown Activity') as activity_name,
                       pb.estimated_hours, pb.actual_hours,
                       pb.hourly_rate, pb.total_cost, pb.booking_status, 
                       COALESCE(pb.start_date, pb.booking_date) as period,
                       tu.name as technical_unit_name,
                       pb.notes'''
    
    new_query1 = '''SELECT pb.id, p.name as project_name, 
                       COALESCE(a.name, 'Unknown Activity') as activity_name,
                       pb.actual_hours,
                       pb.hourly_rate, pb.total_cost, pb.booking_status, 
                       COALESCE(pb.start_date, pb.booking_date) as period,
                       tu.name as technical_unit_name'''
    
    if old_query1 in content:
        content = content.replace(old_query1, new_query1)
        changes_made.append("Updated query in load_services_for_employee")
    
    # Query 2: In load_employee_data_only
    old_query2 = '''pb.estimated_hours,
                        pb.actual_hours,'''
    
    new_query2 = '''pb.actual_hours,'''
    
    if old_query2 in content:
        content = content.replace(old_query2, new_query2)
        changes_made.append("Updated query in load_employee_data_only")
    
    # Query 3: Remove notes from column list
    old_query3 = '''pb.notes'''
    
    # For queries where notes is at the end
    content = re.sub(r',\s*pb\.notes\s*FROM', ' FROM', content)
    content = re.sub(r'pb\.notes\s*FROM', 'FROM', content)
    
    # 3. Update column definitions in complete_columns
    old_columns = '''complete_columns = (
                    "Select", "ID", "Cost Center", "GHRS ID", "Employee Name", "Dept. Description",
                    "Work Location", "Business Unit", "Tipo", "Tipo Description", "SAP Tipo",
                    "SAABU Rate (EUR)", "SAABU Rate (USD)", "Local Agency Rate (USD)", "Unit Rate (USD)",
                    "Monthly Hours", "Annual Hours", "Workload 2025_Planned", "Workload 2025_Actual",
                    "Remark", "Project", "Item", "Technical Unit", "Activities", "Booking Hours",
                    "Booking Cost (Forecast)", "Booking Period", "Booking hours (Accepted by Project)",
                    "Booking Period (Accepted by Project)", "Booking hours (Extra)",
                    "Est. Hours", "Actual Hours", "Hourly Rate", "Total Cost", "Status",
                    "Booking Date", "Start Date", "End Date", "Notes"
                )'''
    
    new_columns = '''complete_columns = (
                    "Select", "ID", "Cost Center", "GHRS ID", "Employee Name", "Dept. Description",
                    "Work Location", "Business Unit", "Tipo", "Tipo Description", "SAP Tipo",
                    "SAABU Rate (EUR)", "SAABU Rate (USD)", "Local Agency Rate (USD)", "Unit Rate (USD)",
                    "Monthly Hours", "Annual Hours", "Workload 2025_Planned", "Workload 2025_Actual",
                    "Remark", "Project", "Item", "Technical Unit", "Activities", "Booking Hours",
                    "Booking Cost (Forecast)", "Booking Period", "Booking hours (Accepted by Project)",
                    "Booking Period (Accepted by Project)", "Booking hours (Extra)",
                    "Actual Hours", "Hourly Rate", "Total Cost", "Status",
                    "Booking Date", "Start Date", "End Date"
                )'''
    
    if old_columns in content:
        content = content.replace(old_columns, new_columns)
        changes_made.append("Updated complete_columns definition")
    
    # 4. Update column_widths dictionary
    old_widths = '''"Est. Hours": 80, "Actual Hours": 80, "Hourly Rate": 80, "Total Cost": 100, "Status": 80,
                            "Booking Date": 100, "Start Date": 100, "End Date": 100, "Notes": 150'''
    
    new_widths = '''"Actual Hours": 80, "Hourly Rate": 80, "Total Cost": 100, "Status": 80,
                            "Booking Date": 100, "Start Date": 100, "End Date": 100'''
    
    if old_widths in content:
        content = content.replace(old_widths, new_widths)
        changes_made.append("Updated column_widths dictionary")
    
    # 5. Update references to est_hours and notes variables
    
    # Find and update the data parsing section
    old_parsing = '''est_hours = booking[3] or 0
                    actual_hours = booking[4] or 0
                    rate = booking[5] or 0
                    cost = booking[6] or 0
                    status = booking[7] or "Pending"
                    period = booking[8] or "N/A"
                    technical_unit = booking[9] or "N/A"
                    notes = booking[10] or ""'''
    
    new_parsing = '''actual_hours = booking[3] or 0
                    rate = booking[4] or 0
                    cost = booking[5] or 0
                    status = booking[6] or "Pending"
                    period = booking[7] or "N/A"
                    technical_unit = booking[8] or "N/A"'''
    
    if old_parsing in content:
        content = content.replace(old_parsing, new_parsing)
        changes_made.append("Updated data parsing in load_services_for_employee")
    
    # 6. Update service_tree.insert values
    old_insert = '''self.service_tree.insert("", "end", values=(
                        display_service, activity_name, est_hours, actual_hours, 
                        rate, cost, status, display_period
                    ), tags=(str(booking_id),))'''
    
    new_insert = '''self.service_tree.insert("", "end", values=(
                        display_service, activity_name, actual_hours, 
                        rate, cost, status, display_period
                    ), tags=(str(booking_id),))'''
    
    if old_insert in content:
        content = content.replace(old_insert, new_insert)
        changes_made.append("Updated service_tree.insert values")
    
    # 7. Update total_hours calculation
    old_total = '''total_hours += float(est_hours) if est_hours else 0'''
    new_total = '''total_hours += float(actual_hours) if actual_hours else 0'''
    
    if old_total in content:
        content = content.replace(old_total, new_total)
        changes_made.append("Updated total_hours calculation")
    
    # 8. Remove any other references to estimated_hours in INSERT/UPDATE statements
    content = re.sub(r',\s*estimated_hours[^,]*,', ',', content)
    content = re.sub(r'estimated_hours[^,]*,\s*', '', content)
    content = re.sub(r',\s*notes[^,)]*', '', content)
    
    # Write the updated content back to the file
    with open('project_booking_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated project_booking_app.py successfully!")
    print("Changes made:")
    for change in changes_made:
        print(f"  - {change}")
    
    return len(changes_made)

if __name__ == "__main__":
    changes = update_project_booking_app()
    print(f"\nTotal changes made: {changes}")
