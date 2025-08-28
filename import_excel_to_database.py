import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime
import sys
import os

# Import our booking period parser
sys.path.append(os.path.dirname(__file__))
from booking_period_parser import parse_booking_period

def create_column_mapping():
    """
    Create mapping between Excel column names and database column names
    """
    column_mapping = {
        # Excel Column Name -> Database Column Name
        'Cost Center': 'cost_center',
        'Employee': 'employee_name',
        # 'HUB': handled separately with lookup to hub_id
        'Technical Unit': 'technical_unit_name',
        'Work Location': 'work_location',
        'Tipo Description': 'tipo_description',
        'SAABU Rate (EUR)': 'saabu_rate_eur',
        'SAABU Rate (USD)': 'saabu_rate_usd',
        'Local Agency Rate (USD': 'local_agency_rate_usd',  # Note: column name is truncated
        'Unit Rate (USD)': 'unit_rate_usd',
        'Monthly Hours': 'monthly_hours',
        'Annual Hours': 'annual_hours',
        'Workload\n2025_Planned': 'workload_2025_planned',
        'Workload\n2025_Actual': 'workload_2025_actual',
        'Remark': 'remark',
        'Project': 'project_name',
        'Activities': 'activities_name',
        'Booking Hours': 'booking_hours',
        'Booking Cost (Forecast)': 'booking_cost_forecast',
        'Booking Period': 'booking_period',
        'Booking hours (Accepted by Project)': 'booking_hours_accepted',
        'Booking Period (Accepted by Project)': 'booking_period_accepted',
        'Booking hours (Extra)': 'booking_hours_extra'
    }
    
    return column_mapping

def get_lookup_ids(conn):
    """Get lookup dictionaries for foreign key relationships"""
    cursor = conn.cursor()
    
    # Get hub lookup
    cursor.execute('SELECT id, name FROM hub')
    hub_lookup = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Get department lookup  
    cursor.execute('SELECT id, name FROM department')
    dept_lookup = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Get technical unit lookup
    cursor.execute('SELECT id, name FROM technical_unit')
    tech_unit_lookup = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Get project lookup
    cursor.execute('SELECT id, name FROM project')
    project_lookup = {row[1]: row[0] for row in cursor.fetchall()}
    
    return hub_lookup, dept_lookup, tech_unit_lookup, project_lookup

def clean_and_import_excel_data():
    """
    Clean Excel data and import it into the project_bookings table
    """
    
    try:
        # Read the Excel file
        print("📊 Reading Excel data...")
        df = pd.read_excel('test.xlsm', sheet_name='BookingManHours')
        
        print(f"Original data shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        # Get column mapping
        column_mapping = create_column_mapping()
        
        # Connect to database
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Get lookup dictionaries
        hub_lookup, dept_lookup, tech_unit_lookup, project_lookup = get_lookup_ids(conn)
        
        print(f"\n📋 Available lookups:")
        print(f"Hubs: {list(hub_lookup.keys())}")
        print(f"Departments: {list(dept_lookup.keys())}")
        print(f"Technical Units: {len(tech_unit_lookup)} items")
        print(f"Projects: {len(project_lookup)} items")
        
        # Clear existing project booking data
        print("\n🗑️ Clearing existing project booking data...")
        cursor.execute('DELETE FROM project_bookings')
        conn.commit()
        
        print("✅ Existing data cleared")
        
        # Process each row
        print("\n📥 Processing Excel data...")
        imported_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                # Skip rows with no employee name
                if pd.isna(row.get('Employee', '')) or row.get('Employee', '').strip() == '':
                    skipped_count += 1
                    continue
                
                # Prepare the data for insertion
                insert_data = {}
                
                # Map basic columns
                for excel_col, db_col in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        if pd.isna(value):
                            insert_data[db_col] = None
                        elif isinstance(value, str):
                            insert_data[db_col] = value.strip()
                        else:
                            insert_data[db_col] = value
                
                # Handle foreign key lookups
                # Hub lookup (case-insensitive)
                hub_name = row.get('HUB', '')
                if pd.notna(hub_name) and hub_name.strip():
                    hub_name_clean = hub_name.strip()
                    hub_id = None
                    
                    # Try exact match first
                    if hub_name_clean in hub_lookup:
                        hub_id = hub_lookup[hub_name_clean]
                    else:
                        # Try case-insensitive match
                        for hub_key, hub_val in hub_lookup.items():
                            if hub_key.lower() == hub_name_clean.lower():
                                hub_id = hub_val
                                break
                    
                    if hub_id:
                        insert_data['hub_id'] = hub_id
                    else:
                        print(f"⚠️ Hub '{hub_name_clean}' not found in lookup")
                        # Print available hubs for debugging
                        print(f"   Available hubs: {list(hub_lookup.keys())}")
                
                # Technical Unit lookup
                tech_unit_name = row.get('Technical Unit', '')
                if pd.notna(tech_unit_name) and tech_unit_name.strip():
                    tech_unit_id = tech_unit_lookup.get(tech_unit_name.strip())
                    if tech_unit_id:
                        insert_data['technical_unit_id'] = tech_unit_id
                
                # Project lookup
                project_name = row.get('Project', '')
                if pd.notna(project_name) and project_name.strip():
                    project_id = project_lookup.get(project_name.strip())
                    if project_id:
                        insert_data['project_id'] = project_id
                
                # Parse booking period to get from/to dates
                booking_period = row.get('Booking Period', '')
                if pd.notna(booking_period) and booking_period.strip():
                    from_date, to_date = parse_booking_period(booking_period.strip())
                    if from_date and to_date:
                        insert_data['booking_period_from'] = from_date
                        insert_data['booking_period_to'] = to_date
                
                # Set default values for required fields
                insert_data['created_at'] = datetime.now()
                insert_data['updated_at'] = datetime.now()
                insert_data['booking_status'] = 'Active'
                
                # Build the SQL insert statement
                columns = list(insert_data.keys())
                placeholders = ['?' for _ in columns]
                values = [insert_data[col] for col in columns]
                
                sql = f"""
                INSERT INTO project_bookings ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """
                
                cursor.execute(sql, values)
                imported_count += 1
                
            except Exception as e:
                print(f"❌ Error processing row {index}: {e}")
                skipped_count += 1
                continue
        
        # Commit all changes
        conn.commit()
        
        print(f"\n✅ Import completed!")
        print(f"   Imported: {imported_count} records")
        print(f"   Skipped: {skipped_count} records")
        print(f"   Total processed: {imported_count + skipped_count}")
        
        # Verify the import
        cursor.execute('SELECT COUNT(*) FROM project_bookings')
        final_count = cursor.fetchone()[0]
        print(f"   Final database count: {final_count}")
        
        # Show sample of imported data
        cursor.execute('''
            SELECT 
                id, employee_name, project_name, booking_hours, 
                booking_period, booking_period_from, booking_period_to
            FROM project_bookings 
            LIMIT 5
        ''')
        
        sample_data = cursor.fetchall()
        if sample_data:
            print(f"\n📊 Sample imported data:")
            print("ID | Employee | Project | Hours | Period | From | To")
            print("-" * 80)
            for row in sample_data:
                print(f"{row[0]:2} | {str(row[1])[:15]:15} | {str(row[2])[:10]:10} | {str(row[3]):5} | {str(row[4])[:8]:8} | {str(row[5])} | {str(row[6])}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def analyze_column_differences():
    """
    Analyze the differences between Excel and database columns
    and suggest what to remove from database
    """
    
    print("\n🔍 ANALYZING COLUMN DIFFERENCES")
    print("=" * 50)
    
    # Excel columns (based on the analysis)
    excel_display_columns = [
        'Cost Center', 'Employee', 'HUB', 'Technical Unit', 'Work Location',
        'Tipo Description', 'SAABU Rate (EUR)', 'SAABU Rate (USD)', 
        'Local Agency Rate (USD)', 'Unit Rate (USD)', 'Monthly Hours', 
        'Annual Hours', 'Workload 2025_Planned', 'Workload 2025_Actual',
        'Remark', 'Project', 'Activities', 'Booking Hours', 
        'Booking Cost (Forecast)', 'Booking Period', 
        'Booking hours (Accepted by Project)', 'Booking Period (Accepted by Project)',
        'Booking hours (Extra)'
    ]
    
    # Get current database columns
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(project_bookings)')
    db_columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    
    # Core essential columns (should not be removed)
    core_columns = [
        'id', 'employee_id', 'technical_unit_id', 'project_id', 'service_id',
        'hub_id', 'department_id', 'booking_period_from', 'booking_period_to',
        'created_at', 'updated_at', 'booking_status'
    ]
    
    # Mapped columns from Excel
    column_mapping = create_column_mapping()
    excel_mapped_columns = list(column_mapping.values())
    
    # Find columns to potentially remove (in DB but not essential and not from Excel)
    columns_to_consider_removing = []
    for col in db_columns:
        if (col not in core_columns and 
            col not in excel_mapped_columns and
            col not in ['hub_id', 'department_id', 'booking_period_from', 'booking_period_to']):
            columns_to_consider_removing.append(col)
    
    print("📋 COLUMNS ANALYSIS:")
    print(f"Excel display columns: {len(excel_display_columns)}")
    print(f"Database columns: {len(db_columns)}")
    print(f"Core essential columns: {len(core_columns)}")
    print(f"Excel mapped columns: {len(excel_mapped_columns)}")
    
    print(f"\n🔴 COLUMNS TO CONSIDER REMOVING FROM DATABASE:")
    print("(These are in DB but not in Excel and not essential)")
    for col in columns_to_consider_removing:
        print(f"  • {col}")
    
    print(f"\n🟢 COLUMNS TO KEEP:")
    columns_to_keep = [col for col in db_columns if col not in columns_to_consider_removing]
    for col in columns_to_keep:
        print(f"  • {col}")
    
    return columns_to_consider_removing, columns_to_keep

if __name__ == "__main__":
    print("🔧 EXCEL TO DATABASE IMPORT PROCESS")
    print("=" * 50)
    
    # First analyze column differences
    columns_to_remove, columns_to_keep = analyze_column_differences()
    
    # Ask user if they want to proceed with import
    print(f"\n❓ Ready to import Excel data?")
    print("This will:")
    print("1. Clear all existing project booking data")
    print("2. Import data from test.xlsm BookingManHours sheet")
    print("3. Map Excel columns to database columns")
    print("4. Parse booking periods to from/to dates")
    
    proceed = input("\nProceed with import? (y/n): ").lower().strip()
    
    if proceed == 'y':
        clean_and_import_excel_data()
    else:
        print("❌ Import cancelled by user")
        print("💾 Column analysis saved above for review")
