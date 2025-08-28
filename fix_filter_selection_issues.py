#!/usr/bin/env python3
"""
Fix for filtering and selection issues in project_booking_app.py

This patch fixes:
1. Select all after applying filter will clear filter then applied to all data
2. When applying filter and start to select by hand, after selecting first 5 then continue to sixth one, the filter will be cleared and all data will be shown without selected items
"""

import sqlite3
import pandas as pd

def patch_selection_and_filtering():
    """
    This function contains the fixed methods that should replace the problematic ones
    in project_booking_app.py
    """
    
    # Fixed select_all_rows method
    def select_all_rows_fixed(self):
        """Select all rows in the CURRENT FILTERED VIEW (not all data)"""
        try:
            # Clear current selection set
            self.selected_rows.clear()
            
            # Iterate through ONLY THE VISIBLE ITEMS in the tree (filtered data)
            for item in self.employee_tree.get_children():
                current_values = list(self.employee_tree.item(item, 'values'))
                if current_values:
                    # Set checkbox to selected
                    current_values[0] = "☑"
                    self.employee_tree.item(item, values=current_values)
                    # Add to selected rows set
                    self.selected_rows.add(item)
            
            # DO NOT call apply_all_filters() here - this was causing the issue!
            print(f"Selected {len(self.selected_rows)} rows from current filtered view")
                    
        except Exception as e:
            print(f"Select all rows error: {e}")
    
    # Fixed apply_all_filters method
    def apply_all_filters_fixed(self):
        """Apply all active filters to the DataFrame - PRESERVE SELECTIONS"""
        try:
            # Store current selections BEFORE reloading data
            current_selections = {}
            for item in self.employee_tree.get_children():
                values = self.employee_tree.item(item, 'values')
                if values and len(values) > 1:
                    row_id = values[1]  # ID is in second column
                    is_selected = values[0] == "☑"
                    if is_selected:
                        current_selections[str(row_id)] = True
            
            # Start with full dataset - reload from database
            self.load_employee_data_grid_for_filter()
            
            # Apply each active filter
            for column, values in self.active_column_filters.items():
                if column in self.df.columns:
                    # Convert values to string for comparison
                    values_str = [str(v) for v in values]
                    self.df = self.df[self.df[column].astype(str).isin(values_str)]
            
            # Refresh the display AND restore selections
            self.refresh_display_with_selections(current_selections)
            
        except Exception as e:
            print(f"Apply all filters error: {e}")
            import traceback
            traceback.print_exc()
    
    # New method to refresh display while preserving selections
    def refresh_display_with_selections(self, preserved_selections):
        """Refresh the tree display with current DataFrame data and restore selections"""
        try:
            # Clear existing items
            for item in self.employee_tree.get_children():
                self.employee_tree.delete(item)
            
            # Clear and rebuild selected_rows set
            self.selected_rows.clear()
            
            # Populate with filtered data
            for _, row in self.df.iterrows():
                values = []
                columns = list(self.employee_tree['columns'])
                
                for col in columns:
                    if col in row:
                        value = row[col]
                        if col == "Select":
                            # Check if this row was previously selected
                            row_id = str(row.get('id', ''))
                            if row_id in preserved_selections:
                                values.append("☑")
                            else:
                                values.append("☐")
                        else:
                            # Handle None values
                            if pd.isna(value):
                                values.append("")
                            else:
                                values.append(str(value))
                    else:
                        values.append("")
                
                # Insert the row
                item = self.employee_tree.insert("", "end", values=values)
                
                # Add to selected_rows if it was selected
                row_id = str(row.get('id', ''))
                if row_id in preserved_selections:
                    self.selected_rows.add(item)
                    
        except Exception as e:
            print(f"Refresh display with selections error: {e}")
            import traceback
            traceback.print_exc()
    
    # Fixed toggle_row_selection to not trigger filter reload
    def toggle_row_selection_fixed(self, event):
        """Toggle row selection without clearing filters"""
        try:
            # Get the clicked item
            item = self.employee_tree.selection()[0] if self.employee_tree.selection() else None
            if not item:
                return
            
            # Get current values
            current_values = list(self.employee_tree.item(item, 'values'))
            if not current_values:
                return
            
            # Toggle checkbox in first column
            if current_values[0] == "☐":
                current_values[0] = "☑"
                self.selected_rows.add(item)
            else:
                current_values[0] = "☐"
                self.selected_rows.discard(item)
            
            # Update the item display
            self.employee_tree.item(item, values=current_values)
            
            # DO NOT call any filter refresh methods here!
            print(f"Toggled selection. Total selected: {len(self.selected_rows)}")
                        
        except Exception as e:
            print(f"Row selection toggle error: {e}")

# Instructions for applying the patch
patch_instructions = """
INSTRUCTIONS TO APPLY THE FIX:

Replace the following methods in project_booking_app.py:

1. Replace select_all_rows() method (around line 2647) with select_all_rows_fixed()
2. Replace apply_all_filters() method (around line 1514) with apply_all_filters_fixed() 
3. Replace toggle_row_selection() method (around line 2618) with toggle_row_selection_fixed()
4. Add the new method refresh_display_with_selections() after refresh_display() method

Key changes:
- select_all_rows() now only selects visible (filtered) rows, doesn't reload all data
- apply_all_filters() preserves current selections when applying filters
- toggle_row_selection() doesn't trigger filter reloads
- New refresh_display_with_selections() method maintains selections across filter operations
"""

if __name__ == "__main__":
    print("Filter and Selection Fix for Project Booking App")
    print("=" * 50)
    print(patch_instructions)
