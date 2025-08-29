#!/usr/bin/env python3
"""
Script to fix the service table by adding missing columns
"""

import sqlite3
import sys
import os

def fix_service_table():
    """Add missing columns to the service table"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'workload.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist first
        cursor.execute('PRAGMA table_info(service)')
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Current columns in service table: {existing_columns}")
        
        # Add missing columns to service table
        print('Adding missing columns to service table...')
        
        # Add estimated_internal_hours column if it doesn't exist
        if 'estimated_internal_hours' not in existing_columns:
            cursor.execute('ALTER TABLE service ADD COLUMN estimated_internal_hours REAL DEFAULT 0.0')
            print('Added estimated_internal_hours column')
        else:
            print('estimated_internal_hours column already exists')
        
        # Add estimated_external_hours column if it doesn't exist
        if 'estimated_external_hours' not in existing_columns:
            cursor.execute('ALTER TABLE service ADD COLUMN estimated_external_hours REAL DEFAULT 0.0')
            print('Added estimated_external_hours column')
        else:
            print('estimated_external_hours column already exists')
        
        # Add notes column if it doesn't exist
        if 'notes' not in existing_columns:
            cursor.execute('ALTER TABLE service ADD COLUMN notes TEXT DEFAULT ""')
            print('Added notes column')
        else:
            print('notes column already exists')
        
        # Commit changes
        conn.commit()
        print('Successfully processed all columns!')
        
        # Verify the changes
        cursor.execute('PRAGMA table_info(service)')
        columns = cursor.fetchall()
        print('\nUpdated service table structure:')
        for col in columns:
            print(f'  {col[1]} ({col[2]})')
            
        # Check if there are any existing service records
        cursor.execute('SELECT COUNT(*) FROM service')
        count = cursor.fetchone()[0]
        print(f'\nTotal service records: {count}')
        
        if count > 0:
            # Update existing records with some reasonable default values
            print('Updating existing records with reasonable default values...')
            
            # Set estimated_internal_hours to 8.0 for existing records (1 day of work)
            cursor.execute('UPDATE service SET estimated_internal_hours = 8.0 WHERE estimated_internal_hours = 0.0')
            
            # Set estimated_external_hours to 0.0 for existing records (no external work by default)
            cursor.execute('UPDATE service SET estimated_external_hours = 0.0 WHERE estimated_external_hours IS NULL')
            
            # Set empty notes for existing records
            cursor.execute('UPDATE service SET notes = "" WHERE notes IS NULL')
            
            conn.commit()
            print('Updated existing records with default values')
        
        return True
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = fix_service_table()
    if success:
        print('\n✅ Service table fixed successfully!')
        sys.exit(0)
    else:
        print('\n❌ Failed to fix service table!')
        sys.exit(1)
