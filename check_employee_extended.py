import sqlite3

def check_employee_extended_table():
    try:
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('PRAGMA table_info(employee_extended)')
            columns = cursor.fetchall()
            
            if columns:
                print(f"employee_extended table has {len(columns)} columns:")
                print("-" * 50)
                
                for i, col in enumerate(columns):
                    print(f"{i+1:2d}. {col[1]:<30} ({col[2]})")
            else:
                print("employee_extended table has no columns or does not exist")
                
        except Exception as e:
            print(f"employee_extended table does not exist: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_employee_extended_table()
