import sqlite3
import tkinter as tk
from tkinter import messagebox

def test_add_booking():
    """Test the add booking process directly"""
    try:
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Get some test data
        cursor.execute("SELECT id, name FROM technical_unit LIMIT 1")
        tech_unit = cursor.fetchone()
        
        cursor.execute("SELECT id, name FROM project LIMIT 1")
        project = cursor.fetchone()
        
        cursor.execute("SELECT id, name FROM employee LIMIT 1")
        employee = cursor.fetchone()
        
        cursor.execute("SELECT id FROM service LIMIT 1")
        service = cursor.fetchone()
        
        if tech_unit and project and employee and service:
            print(f"Testing with:")
            print(f"  Technical Unit: {tech_unit[1]} (ID: {tech_unit[0]})")
            print(f"  Project: {project[1]} (ID: {project[0]})")
            print(f"  Employee: {employee[1]} (ID: {employee[0]})")
            print(f"  Service ID: {service[0]}")
            
            # Parse first_name and last_name from full name (if available)
            cursor.execute("SELECT name FROM employee WHERE id = ?", (employee[0],))
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
            
            # Test the exact INSERT statement from the code
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
            """, (employee[0], tech_unit[0], project[0], service[0],
                  40.0, "2024-01-01", "2024-01-31", "Test booking",
                  None, None, last_name, first_name, None,
                  None, None, None, None, None,
                  0.00, 0.00, 0.00, 0.00,
                  0, 0, 0.00, 0.00,
                  None, project[1], tech_unit[1], "Test Activity", employee[1]))
            
            conn.commit()
            print("✅ SUCCESS: Booking added successfully!")
            
            # Get the last inserted booking
            cursor.execute("SELECT COUNT(*) FROM project_bookings")
            count = cursor.fetchone()[0]
            print(f"Total bookings in database: {count}")
            
        else:
            print("❌ ERROR: Missing required test data")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_add_booking()
