import sqlite3

def quick_populate():
    conn = sqlite3.connect('workload.db')
    cursor = conn.cursor()
    
    # Get sample data from employee_extended
    cursor.execute("""
        SELECT ghrs_id, last_name, first_name, project_assigned, booking_hours, unit_rate_usd
        FROM employee_extended 
        WHERE project_assigned IS NOT NULL 
        LIMIT 3
    """)
    
    employees = cursor.fetchall()
    
    # Insert simple records
    for i, emp in enumerate(employees, 1):
        ghrs_id, last_name, first_name, project, hours, rate = emp
        name = f"{last_name} {first_name}".strip()
        
        cursor.execute("""
            INSERT INTO project_bookings 
            (employee_name, project_name, booking_hours, hourly_rate, total_cost, 
             booking_status, created_at, ghrs_id)
            VALUES (?, ?, ?, ?, ?, 'Active', CURRENT_TIMESTAMP, ?)
        """, (name, project, hours or 0, rate or 0, (hours or 0) * (rate or 0), ghrs_id))
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM project_bookings')
    count = cursor.fetchone()[0]
    print(f'Inserted records. Total count: {count}')
    
    conn.close()

if __name__ == "__main__":
    quick_populate()
