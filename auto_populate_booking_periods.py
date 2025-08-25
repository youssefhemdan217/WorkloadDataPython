import sqlite3
import re
from datetime import datetime, date

def parse_booking_period_to_dates(booking_period):
    """
    Parse booking period text and return (from_date, to_date) tuple
    
    Examples:
    - "Jan to Dec 2025" -> (2025-01-01, 2025-12-31)
    - "Q1 2025" -> (2025-01-01, 2025-03-31)
    - "Q1, Q2 2025" -> (2025-01-01, 2025-06-30)
    - "1/2025" -> (2025-01-01, 2025-01-31)
    - "1/2025 to 12/2025" -> (2025-01-01, 2025-12-31)
    """
    
    if not booking_period or booking_period.strip() == '':
        return None, None
    
    period = booking_period.strip()
    
    # Month name mappings
    month_names = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    # Quarter mappings
    quarter_months = {
        'q1': (1, 3),
        'q2': (4, 6),
        'q3': (7, 9),
        'q4': (10, 12)
    }
    
    try:
        period_lower = period.lower()
        
        # Pattern 1: "Jan to Dec 2025" or "January to December 2025"
        month_range_pattern = r'(\w+)\s+to\s+(\w+)\s+(\d{4})'
        match = re.search(month_range_pattern, period_lower)
        if match:
            start_month_name = match.group(1)
            end_month_name = match.group(2)
            year = int(match.group(3))
            
            start_month = month_names.get(start_month_name)
            end_month = month_names.get(end_month_name)
            
            if start_month and end_month:
                from_date = date(year, start_month, 1)
                # Last day of end month
                if end_month == 12:
                    to_date = date(year, 12, 31)
                else:
                    to_date = date(year, end_month + 1, 1)
                    to_date = date(to_date.year, to_date.month - 1, 31)
                    # Adjust for months with different numbers of days
                    while True:
                        try:
                            to_date = date(year, end_month, to_date.day)
                            break
                        except ValueError:
                            to_date = date(to_date.year, to_date.month, to_date.day - 1)
                
                return from_date, to_date
        
        # Pattern 2: "1/2025 to 12/2025" or "01/2025 to 12/2025"
        numeric_range_pattern = r'(\d{1,2})/(\d{4})\s+to\s+(\d{1,2})/(\d{4})'
        match = re.search(numeric_range_pattern, period_lower)
        if match:
            start_month = int(match.group(1))
            start_year = int(match.group(2))
            end_month = int(match.group(3))
            end_year = int(match.group(4))
            
            from_date = date(start_year, start_month, 1)
            # Last day of end month
            if end_month == 12:
                to_date = date(end_year, 12, 31)
            else:
                to_date = date(end_year, end_month + 1, 1)
                to_date = date(to_date.year, to_date.month - 1, 31)
                # Adjust for months with different numbers of days
                while True:
                    try:
                        to_date = date(end_year, end_month, to_date.day)
                        break
                    except ValueError:
                        to_date = date(to_date.year, to_date.month, to_date.day - 1)
            
            return from_date, to_date
        
        # Pattern 3: Single quarter "Q1 2025" or "2025-Q1" or "Q1-2025"
        single_quarter_pattern = r'(?:q(\d)\s+(\d{4})|(\d{4})-q(\d)|q(\d)-(\d{4}))'
        match = re.search(single_quarter_pattern, period_lower)
        if match:
            if match.group(1) and match.group(2):  # Q1 2025
                quarter_num = int(match.group(1))
                year = int(match.group(2))
            elif match.group(3) and match.group(4):  # 2025-Q1
                year = int(match.group(3))
                quarter_num = int(match.group(4))
            elif match.group(5) and match.group(6):  # Q1-2025
                quarter_num = int(match.group(5))
                year = int(match.group(6))
            else:
                return None, None
            
            quarter_key = f'q{quarter_num}'
            
            if quarter_key in quarter_months:
                start_month, end_month = quarter_months[quarter_key]
                from_date = date(year, start_month, 1)
                # Last day of quarter
                if end_month == 12:
                    to_date = date(year, 12, 31)
                elif end_month == 2:
                    # February - handle leap years
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                        to_date = date(year, 2, 29)
                    else:
                        to_date = date(year, 2, 28)
                elif end_month in [4, 6, 9, 11]:
                    to_date = date(year, end_month, 30)
                else:
                    to_date = date(year, end_month, 31)
                
                return from_date, to_date
        
        # Pattern 4: Multiple quarters "Q1, Q2 2025" or "Q1,Q2 2025" or "2025-Q1,Q2"
        multi_quarter_pattern = r'(?:q(\d)(?:\s*,\s*q(\d))?(?:\s*,\s*q(\d))?(?:\s*,\s*q(\d))?\s+(\d{4})|(\d{4})-q(\d)(?:\s*,\s*q(\d))?(?:\s*,\s*q(\d))?(?:\s*,\s*q(\d))?)'
        match = re.search(multi_quarter_pattern, period_lower)
        if match:
            quarters = []
            year = None
            
            if match.group(5):  # Standard format Q1, Q2 2025
                quarters = [int(q) for q in match.groups()[:4] if q is not None and q.isdigit()]
                year = int(match.group(5))
            elif match.group(6):  # 2025-Q1,Q2 format
                year = int(match.group(6))
                quarters = [int(q) for q in match.groups()[6:] if q is not None and q.isdigit()]
            
            if quarters and year:
                min_quarter = min(quarters)
                max_quarter = max(quarters)
                
                start_month = quarter_months[f'q{min_quarter}'][0]
                end_month = quarter_months[f'q{max_quarter}'][1]
                
                from_date = date(year, start_month, 1)
                # Last day of last quarter
                if end_month == 12:
                    to_date = date(year, 12, 31)
                elif end_month == 2:
                    # February - handle leap years
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                        to_date = date(year, 2, 29)
                    else:
                        to_date = date(year, 2, 28)
                elif end_month in [4, 6, 9, 11]:
                    to_date = date(year, end_month, 30)
                else:
                    to_date = date(year, end_month, 31)
                
                return from_date, to_date
        
        # Pattern 5: Single month "1/2025" or "01/2025"
        single_month_pattern = r'(\d{1,2})/(\d{4})'
        match = re.search(single_month_pattern, period_lower)
        if match:
            month = int(match.group(1))
            year = int(match.group(2))
            
            from_date = date(year, month, 1)
            # Last day of month
            if month == 12:
                to_date = date(year, 12, 31)
            else:
                to_date = date(year, month + 1, 1)
                to_date = date(to_date.year, to_date.month - 1, 31)
                while True:
                    try:
                        to_date = date(year, month, to_date.day)
                        break
                    except ValueError:
                        to_date = date(to_date.year, to_date.month, to_date.day - 1)
            
            return from_date, to_date
        
        # Pattern 6: Single month name "January 2025"
        single_month_name_pattern = r'(\w+)\s+(\d{4})'
        match = re.search(single_month_name_pattern, period_lower)
        if match:
            month_name = match.group(1)
            year = int(match.group(2))
            
            month = month_names.get(month_name)
            if month:
                from_date = date(year, month, 1)
                # Last day of month
                if month == 12:
                    to_date = date(year, 12, 31)
                else:
                    to_date = date(year, month + 1, 1)
                    to_date = date(to_date.year, to_date.month - 1, 31)
                    while True:
                        try:
                            to_date = date(year, month, to_date.day)
                            break
                        except ValueError:
                            to_date = date(to_date.year, to_date.month, to_date.day - 1)
                
                return from_date, to_date
        
    except Exception as e:
        print(f"Error parsing booking period '{booking_period}': {e}")
        return None, None
    
    print(f"Could not parse booking period: '{booking_period}'")
    return None, None

def update_booking_period_dates():
    """
    Update booking_period_from and booking_period_to based on existing booking_period values
    """
    
    try:
        conn = sqlite3.connect('workload.db')
        cursor = conn.cursor()
        
        # Get all records with booking_period values
        cursor.execute('''
            SELECT id, booking_period, booking_period_from, booking_period_to
            FROM project_bookings 
            WHERE booking_period IS NOT NULL AND booking_period != ''
        ''')
        
        records = cursor.fetchall()
        print(f"Found {len(records)} records with booking_period values")
        
        updated_count = 0
        test_cases = []
        
        for record_id, booking_period, current_from, current_to in records:
            from_date, to_date = parse_booking_period_to_dates(booking_period)
            
            if from_date and to_date:
                # Update the record
                cursor.execute('''
                    UPDATE project_bookings 
                    SET booking_period_from = ?, booking_period_to = ?
                    WHERE id = ?
                ''', (from_date, to_date, record_id))
                
                updated_count += 1
                test_cases.append({
                    'id': record_id,
                    'original': booking_period,
                    'from_date': from_date,
                    'to_date': to_date
                })
                
                print(f"✓ Updated ID {record_id}: '{booking_period}' -> {from_date} to {to_date}")
            else:
                print(f"❌ Could not parse ID {record_id}: '{booking_period}'")
        
        conn.commit()
        
        print(f"\n✅ Successfully updated {updated_count} records")
        
        # Show sample of updated data
        if test_cases:
            print("\nSample updated records:")
            print("ID | Original Period | From Date  | To Date")
            print("-" * 50)
            for case in test_cases[:10]:  # Show first 10
                print(f"{case['id']:2} | {case['original'][:20]:20} | {case['from_date']} | {case['to_date']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating booking period dates: {e}")
        if conn:
            conn.rollback()
            conn.close()

def test_parsing_logic():
    """Test the parsing logic with various formats"""
    
    test_cases = [
        "Jan to Dec 2025",
        "January to December 2025", 
        "Q1 2025",
        "2025-Q1",  # Format found in data
        "Q1-2025",  # Format found in data
        "2025-Q2",  # Format found in data
        "Q1, Q2 2025",
        "Q1,Q2,Q3 2025",
        "1/2025",
        "01/2025",
        "1/2025 to 12/2025",
        "01/2025 to 12/2025",
        "March 2025",
        "Q4 2024",
        "Q2, Q3 2025"
    ]
    
    print("🧪 Testing parsing logic:")
    print("=" * 60)
    
    for test_case in test_cases:
        from_date, to_date = parse_booking_period_to_dates(test_case)
        result = f"{from_date} to {to_date}" if from_date and to_date else "Could not parse"
        print(f"'{test_case}' -> {result}")

if __name__ == "__main__":
    print("🔧 Auto-populating booking period dates from booking_period column...")
    print("=" * 70)
    
    # First test the parsing logic
    test_parsing_logic()
    
    print("\n" + "=" * 70)
    print("📅 Updating database records...")
    
    # Then update the actual data
    update_booking_period_dates()
