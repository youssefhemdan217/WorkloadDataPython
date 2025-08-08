import sqlite3

def add_ghrs_id_to_employee():
    """Add ghrs_id column to employee table"""
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    
    try:
        # Check if ghrs_id column already exists
        cursor.execute("PRAGMA table_info(employee)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'ghrs_id' not in columns:
            # Add ghrs_id column to employee table
            cursor.execute("ALTER TABLE employee ADD COLUMN ghrs_id VARCHAR(50)")
            print("Added ghrs_id column to employee table")
        else:
            print("ghrs_id column already exists in employee table")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(employee)")
        print("\nUpdated employee table structure:")
        for row in cursor.fetchall():
            print(f"  {row}")
        
        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_ghrs_id_to_employee()
