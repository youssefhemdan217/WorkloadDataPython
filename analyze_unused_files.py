#!/usr/bin/env python3
"""
Script to analyze and identify unused files in the workspace
"""

import os
import re
import sqlite3
from pathlib import Path

def analyze_unused_files():
    """Analyze files to identify which ones are unused"""
    
    workspace_dir = Path(__file__).parent
    
    # Core application files (definitely needed)
    core_files = {
        'Fabsi_List_of_Service.py',  # Main List of Services app
        'project_booking_app.py',    # Main Project Booking app
        'workload.db',               # Database
        'requirements.txt',          # Dependencies
        'fix_service_table.py',      # Recent fix we created
    }
    
    # Essential support files
    essential_files = {
        'app.log',                   # Log file for List of Services
        'project_booking_app.log',   # Log file for Project Booking
        'excel_booking_data_for_import.csv',  # Data file
        'import_excel_booking_data.sql',      # SQL import script
        'FABSI_List of Service HO_Master_R1.xlsx',  # Excel template
        'test.xlsm',                 # Excel file
    }
    
    # Batch/executable files (needed for deployment)
    batch_files = {
        'build_deployment.bat',
        'install_fabsi.bat', 
        'run_project_booking.bat',
    }
    
    # Images/assets
    asset_files = set()
    photos_dir = workspace_dir / 'photos'
    if photos_dir.exists():
        asset_files.update(f'photos/{f.name}' for f in photos_dir.iterdir() if f.is_file())
    
    # Get all Python files
    python_files = list(workspace_dir.glob('*.py'))
    markdown_files = list(workspace_dir.glob('*.md'))
    txt_files = list(workspace_dir.glob('*.txt'))
    
    # Files that are likely unused
    likely_unused = []
    
    # Analyze Python files
    for py_file in python_files:
        filename = py_file.name
        
        # Skip core files
        if filename in core_files:
            continue
            
        # Check if it's a test, debug, or analysis file
        if any(pattern in filename.lower() for pattern in [
            'test_', 'debug_', 'analyze_', 'fix_', 'populate_', 
            'verify_', 'comprehensive_', 'quick_', 'import_excel',
            'update_app', 'api', 'db_setup', 'excel_edit_guide',
            'auto_populate', 'implement_changes'
        ]):
            # Check if it's imported by main apps
            is_imported = check_if_imported(filename, workspace_dir)
            if not is_imported:
                likely_unused.append({
                    'file': filename,
                    'type': 'python',
                    'reason': 'Utility/test script not imported by main apps'
                })
    
    # Analyze markdown files (documentation)
    for md_file in markdown_files:
        filename = md_file.name
        # Most markdown files are documentation and can be considered for cleanup
        # Keep only the most recent fix summary
        if filename != 'SERVICE_TABLE_FIX_SUMMARY.md':
            likely_unused.append({
                'file': filename,
                'type': 'documentation', 
                'reason': 'Old documentation/summary file'
            })
    
    # Analyze txt files
    for txt_file in txt_files:
        filename = txt_file.name
        if filename not in {'requirements.txt'}:
            likely_unused.append({
                'file': filename,
                'type': 'text',
                'reason': 'Summary/documentation file'
            })
    
    return likely_unused

def check_if_imported(filename, workspace_dir):
    """Check if a Python file is imported by the main applications"""
    
    module_name = filename.replace('.py', '')
    main_apps = ['Fabsi_List_of_Service.py', 'project_booking_app.py']
    
    for app_file in main_apps:
        app_path = workspace_dir / app_file
        if app_path.exists():
            try:
                with open(app_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for import statements
                    if re.search(rf'\b(import|from)\s+{re.escape(module_name)}\b', content):
                        return True
            except Exception:
                pass
    
    return False

def main():
    unused_files = analyze_unused_files()
    
    print("🧹 UNUSED FILES ANALYSIS")
    print("=" * 50)
    
    if not unused_files:
        print("✅ No unused files detected!")
        return
    
    # Group by type
    by_type = {}
    for file_info in unused_files:
        file_type = file_info['type']
        if file_type not in by_type:
            by_type[file_type] = []
        by_type[file_type].append(file_info)
    
    for file_type, files in by_type.items():
        print(f"\n📁 {file_type.upper()} FILES:")
        print("-" * 30)
        for file_info in files:
            print(f"  🗑️  {file_info['file']}")
            print(f"      Reason: {file_info['reason']}")
    
    print(f"\n📊 SUMMARY:")
    print(f"Total files that can be removed: {len(unused_files)}")
    
    # Show which files to keep
    print(f"\n✅ ESSENTIAL FILES TO KEEP:")
    print("  • Fabsi_List_of_Service.py (Main List of Services app)")
    print("  • project_booking_app.py (Main Project Booking app)")
    print("  • workload.db (Database)")
    print("  • requirements.txt (Dependencies)")
    print("  • SERVICE_TABLE_FIX_SUMMARY.md (Recent fix documentation)")
    print("  • fix_service_table.py (Recent fix script)")
    print("  • *.bat files (Deployment scripts)")
    print("  • *.xlsx, *.xlsm files (Excel templates)")
    print("  • *.log files (Application logs)")
    print("  • photos/ directory (Assets)")
    print("  • __pycache__/ directory (Python cache)")
    print("  • instance/ directory (App instance data)")

if __name__ == '__main__':
    main()
