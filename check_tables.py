import sqlite3

conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

print("Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  {table[0]}")

print("\nChecking title table:")
try:
    cursor.execute("PRAGMA table_info(title)")
    columns = cursor.fetchall()
    print("title table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except:
    print("title table not found")

print("\nChecking activities table:")
try:
    cursor.execute("PRAGMA table_info(activities)")
    columns = cursor.fetchall()
    print("activities table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except:
    print("activities table not found")

conn.close()
