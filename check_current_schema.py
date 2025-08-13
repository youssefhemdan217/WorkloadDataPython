import sqlite3

def check_database_schema():
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("=== EXISTING TABLES ===")
    for table in tables:
        print(f"Table: {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_database_schema()
