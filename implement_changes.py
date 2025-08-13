import sqlite3
import logging

def implement_database_changes():
    """
    Implement the requested database changes:
    1. Add hub table with [id, name] and populate with specified data
    2. Add department table with [id, name]
    3. Remove estimated_hours and notes columns from service table and project_bookings if they exist
    """
    
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    
    try:
        # 1. Create hub table
        print("Creating hub table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hub (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL
            )
        ''')
        
        # Check if hub table is empty and populate
        cursor.execute("SELECT COUNT(*) FROM hub")
        if cursor.fetchone()[0] == 0:
            hub_data = [
                ('Saipem SpA Abu Dhabi Branch',),
                ('Saipem SpA Milan',),
                ('Local Agency',)
            ]
            cursor.executemany("INSERT INTO hub (name) VALUES (?)", hub_data)
            print(f"Inserted {len(hub_data)} records into hub table")
        else:
            print("Hub table already contains data")
        
        # 2. Create department table
        print("Creating department table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS department (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL
            )
        ''')
        print("Department table created successfully")
        
        # 3. Check and remove estimated_hours and notes columns from service table
        print("Checking service table structure...")
        cursor.execute("PRAGMA table_info(service)")
        service_columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_remove = []
        if 'estimated_internal_hours' in service_columns:
            columns_to_remove.append('estimated_internal_hours')
        if 'estimated_external_hours' in service_columns:
            columns_to_remove.append('estimated_external_hours')
        if 'notes' in service_columns:
            columns_to_remove.append('notes')
        
        if columns_to_remove:
            print(f"Removing columns from service table: {columns_to_remove}")
            
            # Get all columns except the ones to remove
            remaining_columns = [col for col in service_columns if col not in columns_to_remove]
            
            # Create new table without the unwanted columns
            column_definitions = []
            cursor.execute("PRAGMA table_info(service)")
            for col_info in cursor.fetchall():
                col_name = col_info[1]
                if col_name not in columns_to_remove:
                    col_type = col_info[2]
                    pk = " PRIMARY KEY AUTOINCREMENT" if col_info[5] else ""
                    not_null = " NOT NULL" if col_info[3] else ""
                    column_definitions.append(f"{col_name} {col_type}{pk}{not_null}")
            
            # Create temporary table
            create_sql = f"CREATE TABLE service_temp ({', '.join(column_definitions)})"
            cursor.execute(create_sql)
            
            # Copy data
            columns_str = ', '.join(remaining_columns)
            cursor.execute(f"INSERT INTO service_temp ({columns_str}) SELECT {columns_str} FROM service")
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE service")
            cursor.execute("ALTER TABLE service_temp RENAME TO service")
            
            print("Service table updated successfully")
        else:
            print("No columns to remove from service table")
        
        # 4. Check and remove estimated_hours and notes columns from project_bookings table
        print("Checking project_bookings table structure...")
        cursor.execute("PRAGMA table_info(project_bookings)")
        pb_columns = [col[1] for col in cursor.fetchall()]
        
        pb_columns_to_remove = []
        if 'estimated_hours' in pb_columns:
            pb_columns_to_remove.append('estimated_hours')
        if 'notes' in pb_columns:
            pb_columns_to_remove.append('notes')
        
        if pb_columns_to_remove:
            print(f"Removing columns from project_bookings table: {pb_columns_to_remove}")
            
            # Get all columns except the ones to remove
            remaining_pb_columns = [col for col in pb_columns if col not in pb_columns_to_remove]
            
            # Create new table without the unwanted columns
            pb_column_definitions = []
            cursor.execute("PRAGMA table_info(project_bookings)")
            for col_info in cursor.fetchall():
                col_name = col_info[1]
                if col_name not in pb_columns_to_remove:
                    col_type = col_info[2]
                    pk = " PRIMARY KEY AUTOINCREMENT" if col_info[5] else ""
                    not_null = " NOT NULL" if col_info[3] else ""
                    pb_column_definitions.append(f"{col_name} {col_type}{pk}{not_null}")
            
            # Create temporary table
            create_pb_sql = f"CREATE TABLE project_bookings_temp ({', '.join(pb_column_definitions)})"
            cursor.execute(create_pb_sql)
            
            # Copy data
            pb_columns_str = ', '.join(remaining_pb_columns)
            cursor.execute(f"INSERT INTO project_bookings_temp ({pb_columns_str}) SELECT {pb_columns_str} FROM project_bookings")
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE project_bookings")
            cursor.execute("ALTER TABLE project_bookings_temp RENAME TO project_bookings")
            
            print("Project_bookings table updated successfully")
        else:
            print("No columns to remove from project_bookings table")
        
        conn.commit()
        print("\nAll database changes completed successfully!")
        
        # Show final table structures
        print("\n=== FINAL TABLE STRUCTURES ===")
        
        # Hub table
        print("\nHUB TABLE:")
        cursor.execute("PRAGMA table_info(hub)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        cursor.execute("SELECT * FROM hub")
        print("Data:")
        for row in cursor.fetchall():
            print(f"  {row}")
        
        # Department table
        print("\nDEPARTMENT TABLE:")
        cursor.execute("PRAGMA table_info(department)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        
        # Service table
        print("\nSERVICE TABLE (updated):")
        cursor.execute("PRAGMA table_info(service)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        
        # Project_bookings table
        print("\nPROJECT_BOOKINGS TABLE (updated):")
        cursor.execute("PRAGMA table_info(project_bookings)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    implement_database_changes()
