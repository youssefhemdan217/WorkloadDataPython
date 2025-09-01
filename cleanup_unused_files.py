#!/usr/bin/env python3
"""
Cleanup script to remove unused files from the workspace
IMPORTANT: Always backup your data before running this script!
"""

import os
import shutil
from pathlib import Path

def cleanup_unused_files():
    """Remove unused files identified by the analysis"""
    
    workspace_dir = Path(__file__).parent
    
    # Files to remove (based on analysis)
    python_files_to_remove = [
        'analyze_excel_file.py',
        'analyze_insert.py', 
        'analyze_unused_files.py',  # The analysis script itself
        'analyze_vba_code.py',
        'api.py',
        'auto_populate_booking_periods.py',
        'booking_period_parser.py',  # Not imported by main apps
        'comprehensive_test.py',
        'db_setup.py',
        'debug_data.py',
        'excel_edit_guide.py',
        'fix_filter_selection_issues.py',
        'fix_null_values.py',
        'implement_changes.py',
        'import_excel_to_database.py',
        'populate_bookings.py',
        'populate_final.py',
        'quick_populate.py',
        'test_fixes.py',
        'test_urgent_fix.py',
        'update_app.py',
        'verify_filter_fixes.py',
        'verify.py',
    ]
    
    markdown_files_to_remove = [
        'BOOKING_PERIOD_AUTO_POPULATION_SUMMARY.md',
        'EXCEL_INTEGRATION_SUMMARY.md',
        'FILTER_SELECTION_FIX_SUMMARY.md',
        'FILTER_SELECTION_GUIDE.md',
        'PRESENTATION_READY_SUMMARY.md',
        'URGENT_ISSUE_RESOLVED.md',
        'VBA_ANALYSIS_REPORT.md',
    ]
    
    text_files_to_remove = [
        'URGENT_FIX_SUMMARY.txt',
    ]
    
    all_files_to_remove = python_files_to_remove + markdown_files_to_remove + text_files_to_remove
    
    print("🧹 CLEANING UP UNUSED FILES")
    print("=" * 50)
    
    removed_count = 0
    skipped_count = 0
    
    for filename in all_files_to_remove:
        file_path = workspace_dir / filename
        
        if file_path.exists():
            try:
                if file_path.is_file():
                    file_path.unlink()  # Remove file
                    print(f"✅ Removed: {filename}")
                    removed_count += 1
                else:
                    print(f"⚠️  Skipped (not a file): {filename}")
                    skipped_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filename}: {e}")
                skipped_count += 1
        else:
            print(f"ℹ️  Not found: {filename}")
            skipped_count += 1
    
    # Also check and remove the archive_unused directory if it exists
    archive_dir = workspace_dir / 'archive_unused'
    if archive_dir.exists():
        try:
            shutil.rmtree(archive_dir)
            print(f"✅ Removed archive directory: archive_unused/")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove archive_unused/: {e}")
            skipped_count += 1
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"  Files/directories removed: {removed_count}")
    print(f"  Files skipped/not found: {skipped_count}")
    
    print(f"\n✅ REMAINING ESSENTIAL FILES:")
    print("  • Fabsi_List_of_Service.py")
    print("  • project_booking_app.py")
    print("  • workload.db")
    print("  • requirements.txt")
    print("  • SERVICE_TABLE_FIX_SUMMARY.md")
    print("  • fix_service_table.py")
    print("  • *.bat files")
    print("  • *.xlsx, *.xlsm files")
    print("  • *.log files")
    print("  • photos/ directory")
    print("  • __pycache__/ directory")
    print("  • instance/ directory")
    print("  • notes directory")
    
    return removed_count

def main():
    print("⚠️  WARNING: This will permanently delete unused files!")
    print("Make sure you have a backup before proceeding.")
    
    response = input("\nDo you want to proceed with cleanup? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        removed = cleanup_unused_files()
        if removed > 0:
            print(f"\n🎉 Cleanup completed! Removed {removed} files/directories.")
        else:
            print(f"\n✨ Workspace is already clean!")
    else:
        print("\n🚫 Cleanup cancelled.")

if __name__ == '__main__':
    main()
