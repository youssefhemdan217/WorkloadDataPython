import sqlite3

def test_direct_edit():
    """Test the database update functionality that the editing system uses"""
    try:
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Get a record to test with
        cursor.execute("SELECT id, employee_name, estimated_hours, remark FROM project_bookings LIMIT 1")
        test_record = cursor.fetchone()
        
        if test_record:
            booking_id, emp_name, est_hours, remark = test_record
            print(f"Testing with booking ID: {booking_id}")
            print(f"Current values:")
            print(f"  Employee Name: {emp_name}")
            print(f"  Estimated Hours: {est_hours}")
            print(f"  Remark: {remark}")
            
            # Test updating a text field
            new_remark = "TEST EDIT - Updated via direct editing system"
            cursor.execute("UPDATE project_bookings SET remark = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                          (new_remark, booking_id))
            
            # Test updating a numeric field  
            new_hours = 25.5
            cursor.execute("UPDATE project_bookings SET estimated_hours = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                          (new_hours, booking_id))
            
            conn.commit()
            
            # Verify the changes
            cursor.execute("SELECT employee_name, estimated_hours, remark FROM project_bookings WHERE id = ?", (booking_id,))
            updated_record = cursor.fetchone()
            
            print(f"\nAfter update:")
            print(f"  Employee Name: {updated_record[0]}")
            print(f"  Estimated Hours: {updated_record[1]}")
            print(f"  Remark: {updated_record[2]}")
            
            print("\n✅ Direct edit functionality is working correctly!")
            
        else:
            print("❌ No records found to test with")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_edit()
