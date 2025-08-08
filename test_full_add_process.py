import sqlite3
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

def create_minimal_test():
    """Create a minimal test that simulates the exact add process"""
    try:
        # Test with actual database
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Get test data for dropdown simulation
        cursor.execute("SELECT id, name FROM technical_unit LIMIT 1")
        tech_unit = cursor.fetchone()
        
        cursor.execute("SELECT id, name FROM project LIMIT 1") 
        project = cursor.fetchone()
        
        cursor.execute("SELECT id, name FROM employee LIMIT 1")
        employee = cursor.fetchone()
        
        cursor.execute("SELECT id FROM service WHERE technical_unit_id = ? AND project_id = ? LIMIT 1", (tech_unit[0], project[0]))
        service = cursor.fetchone()
        
        if not service:
            cursor.execute("SELECT id FROM service LIMIT 1")
            service = cursor.fetchone()
        
        print(f"Using test data:")
        print(f"  Technical Unit: {tech_unit[1]} (ID: {tech_unit[0]})")
        print(f"  Project: {project[1]} (ID: {project[0]})") 
        print(f"  Employee: {employee[1]} (ID: {employee[0]})")
        print(f"  Service ID: {service[0] if service else 'None'}")
        
        if not service:
            print("❌ No service found, creating test record manually")
            return
            
        # Simulate the exact workflow from check_and_add_service_data
        tech_unit_id = tech_unit[0]
        project_id = project[0] 
        employee_id = employee[0]
        service_id = service[0]
        
        # Get employee extended data (same as the real method)
        cursor.execute("""
            SELECT cost_center, ghrs_id, COALESCE(first_name || ' ' || last_name, last_name, first_name, 'N/A') as employee_name, dept_description,
                   work_location, business_unit, tipo, tipo_description, sap_tipo,
                   saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                   monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                   remark
            FROM employee_extended WHERE id = ?
        """, (employee_id,))
        emp_data = cursor.fetchone()
        
        # Get service data
        cursor.execute("""
            SELECT id, estimated_internal_hours, estimated_external_hours, 
                   start_date, due_date, notes, activities_id, title_id
            FROM service 
            WHERE id = ?
        """, (service_id,))
        service_data = cursor.fetchone()
        
        if service_data:
            estimated_internal = service_data[1] or 0
            estimated_external = service_data[2] or 0
            total_estimated = (estimated_internal or 0) + (estimated_external or 0)
            start_date = service_data[3]
            end_date = service_data[4]
            service_notes = service_data[5]
            
            # Get related names
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
            
            # Parse employee name
            cursor.execute("SELECT name FROM employee WHERE id = ?", (employee_id,))
            name_data = cursor.fetchone()
            full_name = name_data[0] if name_data and name_data[0] else ""
            emp_name = full_name
            
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
            
            # Prepare emp_data values with defaults
            if emp_data:
                (cost_center, ghrs_id, employee_name_from_query, dept_description,
                 work_location, business_unit, tipo, tipo_description, sap_tipo,
                 saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                 monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                 remark) = emp_data
            else:
                (cost_center, ghrs_id, dept_description,
                 work_location, business_unit, tipo, tipo_description, sap_tipo,
                 saabu_rate_eur, saabu_rate_usd, local_agency_rate_usd, unit_rate_usd,
                 monthly_hours, annual_hours, workload_2025_planned, workload_2025_actual,
                 remark) = (None, None, None, None, None, None, None, None,
                           0.00, 0.00, 0.00, 0.00, 0, 0, 0.00, 0.00, None)
            
            # Check if booking already exists
            cursor.execute("""
                SELECT id FROM project_bookings 
                WHERE employee_id = ? AND technical_unit_id = ? 
                AND project_id = ? AND service_id = ?
            """, (employee_id, tech_unit_id, project_id, service_id))
            
            existing_booking = cursor.fetchone()
            
            if existing_booking:
                print(f"⚠️  Booking already exists with ID: {existing_booking[0]}")
                return
            
            print("✅ Inserting new booking record...")
            
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
            
            conn.commit()
            
            # Get count
            cursor.execute("SELECT COUNT(*) FROM project_bookings")
            count = cursor.fetchone()[0]
            
            print(f"✅ SUCCESS: Booking added successfully!")
            print(f"Total bookings in database: {count}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_minimal_test()
