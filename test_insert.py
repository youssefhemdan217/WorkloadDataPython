import sqlite3

# Quick insert of test data
conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

# Insert a simple test record
cursor.execute("""
    INSERT INTO project_bookings 
    (employee_name, project_name, booking_hours, monthly_hours, annual_hours, 
     workload_2025_planned, workload_2025_actual, booking_period, 
     booking_hours_accepted, booking_period_accepted, booking_hours_extra,
     hourly_rate, total_cost, booking_status, created_at)
    VALUES ('Test Employee', 'Test Project', 100, 160, 1920, 80.0, 75.0, 
            'Q1-2025', 90, 'Q1-2025', 10, 50.0, 5000.0, 'Active', CURRENT_TIMESTAMP)
""")

conn.commit()

# Check if it's there
cursor.execute('SELECT COUNT(*), employee_name, booking_hours FROM project_bookings')
result = cursor.fetchone()
print(f'Records: {result[0]}, Employee: {result[1]}, Hours: {result[2]}')

conn.close()
