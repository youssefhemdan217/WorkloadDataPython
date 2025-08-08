import sqlite3

conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

print("Employee table schema:")
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="employee"')
result = cursor.fetchone()
if result:
    print(result[0])

print("\nEmployee table columns:")
cursor.execute('PRAGMA table_info(employee)')
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\nSample employee data:")
cursor.execute('SELECT * FROM employee LIMIT 3')
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
