import sqlite3

def check_project_bookings_table():
    try:
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute('PRAGMA table_info(project_bookings)')
        columns = cursor.fetchall()
        
        print(f"project_bookings table has {len(columns)} columns:")
        print("-" * 50)
        
        for i, col in enumerate(columns):
            print(f"{i+1:2d}. {col[1]:<30} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_project_bookings_table()
