"""
Booking Period Parser Utility

This module provides functionality to automatically parse booking period text
and convert it to from/to date ranges for the project booking system.

Usage:
- Can be imported into the main application
- Supports various formats: Q1 2025, 2025-Q2, Jan to Dec 2025, 1/2025 to 12/2025, etc.
"""

import re
from datetime import datetime, date

class BookingPeriodParser:
    """Parser for converting booking period text to date ranges"""
    
    def __init__(self):
        # Month name mappings
        self.month_names = {
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
        self.quarter_months = {
            'q1': (1, 3),   # Q1: Jan-Mar
            'q2': (4, 6),   # Q2: Apr-Jun
            'q3': (7, 9),   # Q3: Jul-Sep
            'q4': (10, 12)  # Q4: Oct-Dec
        }
    
    def get_last_day_of_month(self, year, month):
        """Get the last day of a given month/year"""
        if month == 12:
            return 31
        elif month == 2:
            # February - handle leap years
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            else:
                return 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31
    
    def parse(self, booking_period):
        """
        Parse booking period text and return (from_date, to_date) tuple
        
        Supported formats:
        - "Jan to Dec 2025" -> (2025-01-01, 2025-12-31)
        - "Q1 2025" -> (2025-01-01, 2025-03-31)
        - "2025-Q1" -> (2025-01-01, 2025-03-31)
        - "Q1-2025" -> (2025-01-01, 2025-03-31)
        - "Q1, Q2 2025" -> (2025-01-01, 2025-06-30)
        - "1/2025" -> (2025-01-01, 2025-01-31)
        - "1/2025 to 12/2025" -> (2025-01-01, 2025-12-31)
        """
        
        if not booking_period or booking_period.strip() == '':
            return None, None
        
        period = booking_period.strip().lower()
        
        try:
            # Pattern 1: "Jan to Dec 2025" or "January to December 2025"
            month_range_pattern = r'(\w+)\s+to\s+(\w+)\s+(\d{4})'
            match = re.search(month_range_pattern, period)
            if match:
                start_month_name = match.group(1)
                end_month_name = match.group(2)
                year = int(match.group(3))
                
                start_month = self.month_names.get(start_month_name)
                end_month = self.month_names.get(end_month_name)
                
                if start_month and end_month:
                    from_date = date(year, start_month, 1)
                    last_day = self.get_last_day_of_month(year, end_month)
                    to_date = date(year, end_month, last_day)
                    return from_date, to_date
            
            # Pattern 2: "1/2025 to 12/2025" or "01/2025 to 12/2025"
            numeric_range_pattern = r'(\d{1,2})/(\d{4})\s+to\s+(\d{1,2})/(\d{4})'
            match = re.search(numeric_range_pattern, period)
            if match:
                start_month = int(match.group(1))
                start_year = int(match.group(2))
                end_month = int(match.group(3))
                end_year = int(match.group(4))
                
                from_date = date(start_year, start_month, 1)
                last_day = self.get_last_day_of_month(end_year, end_month)
                to_date = date(end_year, end_month, last_day)
                return from_date, to_date
            
            # Pattern 3: Single quarter "Q1 2025" or "2025-Q1" or "Q1-2025"
            single_quarter_pattern = r'(?:q(\d)\s+(\d{4})|(\d{4})-q(\d)|q(\d)-(\d{4}))'
            match = re.search(single_quarter_pattern, period)
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
                
                if quarter_key in self.quarter_months:
                    start_month, end_month = self.quarter_months[quarter_key]
                    from_date = date(year, start_month, 1)
                    last_day = self.get_last_day_of_month(year, end_month)
                    to_date = date(year, end_month, last_day)
                    return from_date, to_date
            
            # Pattern 4: Multiple quarters "Q1, Q2 2025" 
            multi_quarter_pattern = r'q(\d)(?:\s*,\s*q(\d))?(?:\s*,\s*q(\d))?(?:\s*,\s*q(\d))?\s+(\d{4})'
            match = re.search(multi_quarter_pattern, period)
            if match:
                quarters = [int(q) for q in match.groups()[:-1] if q is not None]
                year = int(match.groups()[-1])
                
                if quarters:
                    min_quarter = min(quarters)
                    max_quarter = max(quarters)
                    
                    start_month = self.quarter_months[f'q{min_quarter}'][0]
                    end_month = self.quarter_months[f'q{max_quarter}'][1]
                    
                    from_date = date(year, start_month, 1)
                    last_day = self.get_last_day_of_month(year, end_month)
                    to_date = date(year, end_month, last_day)
                    return from_date, to_date
            
            # Pattern 5: Single month "1/2025" or "01/2025"
            single_month_pattern = r'^(\d{1,2})/(\d{4})$'
            match = re.search(single_month_pattern, period)
            if match:
                month = int(match.group(1))
                year = int(match.group(2))
                
                from_date = date(year, month, 1)
                last_day = self.get_last_day_of_month(year, month)
                to_date = date(year, month, last_day)
                return from_date, to_date
            
            # Pattern 6: Single month name "January 2025"
            single_month_name_pattern = r'^(\w+)\s+(\d{4})$'
            match = re.search(single_month_name_pattern, period)
            if match:
                month_name = match.group(1)
                year = int(match.group(2))
                
                month = self.month_names.get(month_name)
                if month:
                    from_date = date(year, month, 1)
                    last_day = self.get_last_day_of_month(year, month)
                    to_date = date(year, month, last_day)
                    return from_date, to_date
            
        except Exception as e:
            print(f"Error parsing booking period '{booking_period}': {e}")
            return None, None
        
        return None, None
    
    def format_period_display(self, from_date, to_date):
        """Format date range for display"""
        if not from_date or not to_date:
            return "N/A"
        
        if from_date.year == to_date.year:
            if from_date.month == to_date.month:
                return f"{from_date.strftime('%b %Y')}"
            else:
                return f"{from_date.strftime('%b')} to {to_date.strftime('%b %Y')}"
        else:
            return f"{from_date.strftime('%b %Y')} to {to_date.strftime('%b %Y')}"

# Global instance for easy use
booking_period_parser = BookingPeriodParser()

def parse_booking_period(period_text):
    """
    Convenience function to parse booking period text
    Returns (from_date, to_date) tuple
    """
    return booking_period_parser.parse(period_text)

def format_booking_period_display(from_date, to_date):
    """
    Convenience function to format booking period for display
    """
    return booking_period_parser.format_period_display(from_date, to_date)

# Example usage and tests
if __name__ == "__main__":
    parser = BookingPeriodParser()
    
    test_cases = [
        "Q1 2025",
        "2025-Q2", 
        "Q1-2025",
        "Q1, Q2 2025",
        "Jan to Dec 2025",
        "1/2025 to 12/2025",
        "March 2025",
        "6/2025",
        "Invalid format"
    ]
    
    print("Booking Period Parser Test Results:")
    print("=" * 50)
    
    for test_case in test_cases:
        from_date, to_date = parser.parse(test_case)
        if from_date and to_date:
            display = parser.format_period_display(from_date, to_date)
            print(f"'{test_case}' -> {from_date} to {to_date} ({display})")
        else:
            print(f"'{test_case}' -> Could not parse")
