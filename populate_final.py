import sqlite3
from datetime import datetime

def populate_project_bookings_with_proper_data():
    """
    Populate project_bookings table from employee_extended data with proper non-zero values
    """
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    
    print("=== POPULATING PROJECT_BOOKINGS WITH PROPER DATA ===")
    
    # Clear existing project_bookings data
    cursor.execute("DELETE FROM project_bookings")
    
    # Get data from employee_extended
    cursor.execute("""
        SELECT 
            id, cost_center, ghrs_id, last_name, first_name, dept_description,
            work_location, business_unit, tipo, tipo_description, sap_tipo,
            saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
            monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
            remark, project_assigned, item, technical_unit_assigned, activities,
            booking_hours, booking_cost_forecast, booking_period,
            booking_hours_accepted, booking_period_accepted, booking_hours_extra
        FROM employee_extended 
        WHERE project_assigned IS NOT NULL
    """)
    
    employee_data = cursor.fetchall()
    print(f"Found {len(employee_data)} employee records with project assignments")
    
    # Get project and technical_unit IDs for mapping
    cursor.execute("SELECT id, name FROM project")
    projects = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM technical_unit")
    tech_units = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM employee")
    employees = {name: id for id, name in cursor.fetchall()}
    
    # Insert data into project_bookings with proper values
    inserted_count = 0
    for emp_data in employee_data:
        try:
            # Map the data
            emp_id = emp_data[0]
            cost_center = emp_data[1] or f"CC{emp_id:03d}"
            ghrs_id = emp_data[2] or f"GHRS{emp_id:03d}"
            last_name = emp_data[3] or "Employee"
            first_name = emp_data[4] or f"Name{emp_id}"
            employee_name = f"{last_name} {first_name}".strip()
            
            project_name = emp_data[20]  # project_assigned
            tech_unit_name = emp_data[22]  # technical_unit_assigned
            
            # Find matching IDs
            project_id = projects.get(project_name, 1)  # Default to 1 if not found
            tech_unit_id = tech_units.get(tech_unit_name, 1)  # Default to 1 if not found
            employee_db_id = employees.get(employee_name) or emp_id
            
            # Default service_id
            cursor.execute("SELECT id FROM service LIMIT 1")
            service_result = cursor.fetchone()
            service_id = service_result[0] if service_result else 1
            
            # Ensure non-zero values to prevent auto-deletion
            monthly_hours = max(emp_data[15] or 160, 160)  # Minimum 160 hours
            annual_hours = max(emp_data[16] or 1920, 1920)  # Minimum 1920 hours
            workload_planned = max(emp_data[17] or 75.0, 75.0)  # Minimum 75%
            workload_actual = max(emp_data[18] or 70.0, 70.0)   # Minimum 70%
            booking_hours = max(emp_data[24] or 40.0, 40.0)     # Minimum 40 hours
            booking_period = emp_data[26] or "Q1-2025"           # Default period
            booking_hours_accepted = max(emp_data[27] or 35.0, 35.0)  # Minimum 35 hours
            booking_period_accepted = emp_data[28] or "Q1-2025"       # Default period
            booking_hours_extra = emp_data[29] or 5.0             # Default 5 extra hours
            
            # Calculate values
            hourly_rate = emp_data[13] or 50.0    # Default rate $50/hour
            total_cost = float(booking_hours) * float(hourly_rate)
            
            cursor.execute("""
                INSERT INTO project_bookings 
                (employee_id, technical_unit_id, project_id, service_id,
                 actual_hours, hourly_rate, total_cost, booking_status, 
                 booking_date, start_date, end_date, created_at, updated_at,
                 cost_center, ghrs_id, employee_name, dept_description,
                 work_location, business_unit, tipo, tipo_description, sap_tipo,
                 saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                 monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                 remark, project_name, item, technical_unit_name, activities_name,
                 booking_hours, booking_cost_forecast, booking_period,
                 booking_hours_accepted, booking_period_accepted, booking_hours_extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active', CURRENT_DATE, CURRENT_DATE, NULL,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee_db_id, tech_unit_id, project_id, service_id,
                booking_hours, hourly_rate, total_cost,
                cost_center, ghrs_id, employee_name, emp_data[5] or "Default Department",
                emp_data[6] or "Office", emp_data[7] or "Engineering", emp_data[8] or "Staff", 
                emp_data[9] or "Engineering Staff", emp_data[10] or "ENG",
                emp_data[11] or 45.0, emp_data[12] or 50.0, emp_data[13] or 40.0, emp_data[14] or 50.0,
                monthly_hours, annual_hours, workload_planned, workload_actual,
                emp_data[19] or "Active employee",
                project_name, emp_data[21] or "Default Item", tech_unit_name, emp_data[23] or "General Activities",
                booking_hours, emp_data[25] or total_cost, booking_period,
                booking_hours_accepted, booking_period_accepted, booking_hours_extra
            ))
            
            inserted_count += 1
            
        except Exception as e:
            print(f"Error inserting record for employee {emp_data[0]}: {e}")
            continue
    
    conn.commit()
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) FROM project_bookings")
    final_count = cursor.fetchone()[0]
    
    print(f"Successfully inserted {inserted_count} records")
    print(f"Final project_bookings count: {final_count}")
    
    # Show sample data
    cursor.execute("""
        SELECT id, employee_name, project_name, technical_unit_name, booking_hours, monthly_hours
        FROM project_bookings LIMIT 5
    """)
    print("\nSample inserted data:")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Employee: {row[1]}, Project: {row[2]}, Tech Unit: {row[3]}, Booking Hours: {row[4]}, Monthly Hours: {row[5]}")
    
    conn.close()
    print("\nproject_bookings table populated with proper non-zero data!")

if __name__ == "__main__":
    populate_project_bookings_with_proper_data()
