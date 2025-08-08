import sqlite3

conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Existing tables:", tables)

# If services table doesn't exist, create it
if 'services' not in tables:
    print("Creating services table...")
    cursor.execute("""
        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            technical_unit TEXT,
            project TEXT,
            employee_name TEXT,
            activities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add some sample data
    sample_services = [
        ('Digital Engineering', 'Project Alpha', 'John Smith', 'Software Development'),
        ('Digital Engineering', 'Project Beta', 'Jane Doe', 'System Analysis'),
        ('Process Engineering', 'Project Gamma', 'Bob Johnson', 'Process Design'),
        ('Mechanical Engineering', 'Project Delta', 'Alice Wilson', 'Mechanical Design'),
    ]
    
    cursor.executemany("""
        INSERT INTO services (technical_unit, project, employee_name, activities)
        VALUES (?, ?, ?, ?)
    """, sample_services)
    
    conn.commit()
    print("Services table created and populated with sample data")

conn.close()
print("Database check complete")
