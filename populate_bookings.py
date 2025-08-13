import sqlite3
from datetime import datetime

def populate_project_bookings():
    """
    Populate project_bookings table from employee_extended data
    """
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    
    print("=== POPULATING PROJECT_BOOKINGS FROM EMPLOYEE_EXTENDED ===")
    
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
    
    # Clear existing project_bookings data
    cursor.execute("DELETE FROM project_bookings")
    
    # Get project and technical_unit IDs for mapping
    cursor.execute("SELECT id, name FROM project")
    projects = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM technical_unit")
    tech_units = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM employee")
    employees = {name: id for id, name in cursor.fetchall()}
    
    # Insert data into project_bookings
    inserted_count = 0
    for emp_data in employee_data:
        try:
            # Map the data
            emp_id = emp_data[0]
            cost_center = emp_data[1]
            ghrs_id = emp_data[2]
            last_name = emp_data[3] or ""
            first_name = emp_data[4] or ""
            employee_name = f"{last_name} {first_name}".strip()
            
            project_name = emp_data[20]  # project_assigned
            tech_unit_name = emp_data[22]  # technical_unit_assigned
            
            # Find matching IDs
            project_id = projects.get(project_name)
            tech_unit_id = tech_units.get(tech_unit_name)
            employee_db_id = employees.get(employee_name) or emp_id
            
            # Default service_id (we'll use 1 if it exists)
            cursor.execute("SELECT id FROM service LIMIT 1")
            service_result = cursor.fetchone()
            service_id = service_result[0] if service_result else None
            
            # Calculate values
            booking_hours = emp_data[24] or 0.0  # booking_hours
            hourly_rate = emp_data[13] or 0.0    # unit_rate_usd
            total_cost = float(booking_hours) * float(hourly_rate) if booking_hours and hourly_rate else 0.0
            
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
                cost_center, ghrs_id, employee_name, emp_data[5],  # dept_description
                emp_data[6], emp_data[7], emp_data[8], emp_data[9], emp_data[10],  # work_location, business_unit, tipo, tipo_description, sap_tipo
                emp_data[11], emp_data[12], emp_data[13], emp_data[14],  # rates
                emp_data[15], emp_data[16], emp_data[17], emp_data[18],  # hours and workload
                emp_data[19],  # remark
                project_name, emp_data[21], tech_unit_name, emp_data[23],  # project_name, item, technical_unit_name, activities
                emp_data[24], emp_data[25], emp_data[26],  # booking_hours, booking_cost_forecast, booking_period
                emp_data[27], emp_data[28], emp_data[29]   # booking_hours_accepted, booking_period_accepted, booking_hours_extra
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
        SELECT id, employee_name, project_name, technical_unit_name, booking_hours 
        FROM project_bookings LIMIT 5
    """)
    print("\nSample inserted data:")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Employee: {row[1]}, Project: {row[2]}, Tech Unit: {row[3]}, Hours: {row[4]}")
    
    conn.close()
    print("\nproject_bookings table populated successfully!")

if __name__ == "__main__":
    populate_project_bookings()
