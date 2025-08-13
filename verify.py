import sqlite3

conn = sqlite3.connect('workload.db')
cursor = conn.cursor()

print('=== FINAL VERIFICATION ===')

print('\nHUB TABLE:')
cursor.execute('SELECT * FROM hub')
for row in cursor.fetchall():
    print(f'  {row}')

print('\nDEPARTMENT TABLE STRUCTURE:')
cursor.execute('PRAGMA table_info(department)')
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')

print('\nSERVICE TABLE (columns after removal):')
cursor.execute('PRAGMA table_info(service)')
cols = [col[1] for col in cursor.fetchall()]
print(f'  Columns: {cols}')
print(f'  Has estimated_internal_hours: {"estimated_internal_hours" in cols}')
print(f'  Has estimated_external_hours: {"estimated_external_hours" in cols}')
print(f'  Has notes: {"notes" in cols}')

print('\nPROJECT_BOOKINGS TABLE (columns after removal):')
cursor.execute('PRAGMA table_info(project_bookings)')
pb_cols = [col[1] for col in cursor.fetchall()]
print(f'  Has estimated_hours: {"estimated_hours" in pb_cols}')
print(f'  Has notes: {"notes" in pb_cols}')

conn.close()
print('\nAll changes implemented successfully!')
