import sqlite3

conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

print("=== CHECKING FOR ACTUAL DATA ===")

# Check employee_extended table which has 8 records
cursor.execute('SELECT id, ghrs_id, last_name, first_name, project_assigned FROM employee_extended LIMIT 5')
print('employee_extended sample data:')
for row in cursor.fetchall():
    print(f'  ID: {row[0]}, GHRS: {row[1]}, Name: {row[2]} {row[3]}, Project: {row[4]}')

# Check if we need to populate project_bookings from employee_extended
cursor.execute('SELECT COUNT(*) FROM employee_extended WHERE project_assigned IS NOT NULL')
has_projects = cursor.fetchone()[0]
print(f'\nRecords in employee_extended with projects: {has_projects}')

# Check service table as well
cursor.execute('SELECT COUNT(*) FROM service')
service_count = cursor.fetchone()[0]
print(f'Records in service table: {service_count}')

if service_count > 0:
    cursor.execute('SELECT id, employee_id, project_id, department LIMIT 5')
    print('\nservice table sample:')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, Employee: {row[1]}, Project: {row[2]}, Dept: {row[3]}')

conn.close()
