import sqlite3

conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

# Check for I050 specifically
cursor.execute("SELECT id FROM project_bookings WHERE id = 'I050'")
result = cursor.fetchone()
print(f"I050 exists: {result is not None}")

# Get all IDs that start with I
cursor.execute("SELECT id FROM project_bookings WHERE id LIKE 'I%' LIMIT 10")
result = cursor.fetchall()
print(f"IDs starting with I: {result}")

# Check total count
cursor.execute("SELECT COUNT(*) FROM project_bookings")
count = cursor.fetchone()[0]
print(f"Total records: {count}")

conn.close()
