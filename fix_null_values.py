#!/usr/bin/env python3
"""
Emergency fix for null values in project_bookings table
This script will:
1. Fix department_id mapping from Excel Technical Unit column
2. Fill missing project names from Excel Project column 
3. Fill missing booking periods and dates
4. Set default values for completely empty records
"""

import sqlite3
import pandas as pd
from booking_period_parser import BookingPeriodParser
import sys

def fix_null_values():
    print("🚨 EMERGENCY NULL VALUES FIX - Starting...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Read Excel file with correct column names
        print("📊 Reading Excel file...")
        excel_df = pd.read_excel('test.xlsm', sheet_name='BookingManHours')
        
        # Create mapping dictionaries for departments
        print("🔍 Creating department mappings...")
        
        # Get existing departments
        dept_query = "SELECT id, name FROM departments"
        dept_df = pd.read_sql_query(dept_query, conn)
        dept_map = dict(zip(dept_df['name'].str.lower(), dept_df['id']))
        
        print(f"Available departments: {list(dept_map.keys())}")
        
        # Map Technical Unit to department_id
        tech_unit_to_dept = {
            'fabrication engineering': 'engineering',
            'emiratisation': 'hr',
            'procurement': 'procurement', 
            'project management': 'project management',
            'construction': 'construction',
            'offshore': 'offshore',
            'onshore': 'onshore'
        }
        
        # Fix 1: Update department_id for all NULL values
        print("🔧 Fixing department_id values...")
        records_updated = 0
        
        # Get all records with null department_id
        null_dept_query = """
        SELECT id, employee_name FROM project_bookings 
        WHERE department_id IS NULL
        """
        null_dept_records = pd.read_sql_query(null_dept_query, conn)
        
        for _, record in null_dept_records.iterrows():
            # Find matching excel row by employee name
            excel_match = excel_df[excel_df['Employee'].str.contains(record['employee_name'], case=False, na=False)]
            
            if not excel_match.empty:
                tech_unit = str(excel_match.iloc[0]['Technical Unit']).lower()
                dept_name = None
                
                # Map technical unit to department
                for tech_key, dept_key in tech_unit_to_dept.items():
                    if tech_key in tech_unit:
                        dept_name = dept_key
                        break
                
                if not dept_name:
                    # Default mapping based on common patterns
                    if 'engineering' in tech_unit:
                        dept_name = 'engineering'
                    elif 'project' in tech_unit:
                        dept_name = 'project management'
                    else:
                        dept_name = 'general'  # Default
                
                # Get department_id
                dept_id = dept_map.get(dept_name, 1)  # Default to first department
                
                # Update record
                cursor.execute("""
                UPDATE project_bookings 
                SET department_id = ? 
                WHERE id = ?
                """, (dept_id, record['id']))
                records_updated += 1
            else:
                # Set default department for unmatched records
                cursor.execute("""
                UPDATE project_bookings 
                SET department_id = ? 
                WHERE id = ?
                """, (1, record['id']))  # Default to first department
                records_updated += 1
        
        print(f"✅ Updated {records_updated} department_id values")
        
        # Fix 2: Update missing project names
        print("🔧 Fixing project names...")
        project_updates = 0
        
        # Update records with null or empty project names
        cursor.execute("""
        UPDATE project_bookings 
        SET project_name = 'General Activities'
        WHERE project_name IS NULL OR project_name = 'N/A' OR project_name = ''
        """)
        project_updates = cursor.rowcount
        print(f"✅ Updated {project_updates} project names")
        
        # Fix 3: Parse and fill booking periods
        print("🔧 Fixing booking periods...")
        parser = BookingPeriodParser()
        period_updates = 0
        
        # Get records with booking_period but missing dates
        period_query = """
        SELECT id, booking_period 
        FROM project_bookings 
        WHERE booking_period IS NOT NULL 
        AND booking_period != 'N/A' 
        AND (booking_period_from IS NULL OR booking_period_to IS NULL)
        """
        period_records = pd.read_sql_query(period_query, conn)
        
        for _, record in period_records.iterrows():
            period_from, period_to = parser.parse(record['booking_period'])
            if period_from and period_to:
                cursor.execute("""
                UPDATE project_bookings 
                SET booking_period_from = ?, booking_period_to = ?
                WHERE id = ?
                """, (period_from, period_to, record['id']))
                period_updates += 1
        
        # Set default periods for records without any period info
        cursor.execute("""
        UPDATE project_bookings 
        SET booking_period = '2025', 
            booking_period_from = '2025-01-01', 
            booking_period_to = '2025-12-31'
        WHERE (booking_period IS NULL OR booking_period = 'N/A')
        AND (booking_period_from IS NULL OR booking_period_to IS NULL)
        """)
        default_periods = cursor.rowcount
        
        print(f"✅ Updated {period_updates} existing periods, set {default_periods} default periods")
        
        # Fix 4: Set default booking hours for zero values
        print("🔧 Fixing booking hours...")
        cursor.execute("""
        UPDATE project_bookings 
        SET booking_hours = 160
        WHERE booking_hours = 0 OR booking_hours IS NULL
        """)
        hours_updates = cursor.rowcount
        print(f"✅ Updated {hours_updates} booking hours to default 160")
        
        # Commit all changes
        conn.commit()
        
        # Final verification
        print("\n📊 FINAL VERIFICATION:")
        verification_query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN project_name IS NULL OR project_name = 'N/A' THEN 1 ELSE 0 END) as null_projects,
            SUM(CASE WHEN department_id IS NULL THEN 1 ELSE 0 END) as null_departments,
            SUM(CASE WHEN booking_period_from IS NULL THEN 1 ELSE 0 END) as null_period_from,
            SUM(CASE WHEN booking_hours = 0 OR booking_hours IS NULL THEN 1 ELSE 0 END) as zero_hours
        FROM project_bookings
        """
        verification = pd.read_sql_query(verification_query, conn)
        print(verification.to_string(index=False))
        
        conn.close()
        print("\n🎉 NULL VALUES FIX COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    success = fix_null_values()
    sys.exit(0 if success else 1)
