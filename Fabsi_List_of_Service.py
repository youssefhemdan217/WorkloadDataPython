import os
import logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'app.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import pandas as pd
import os
import subprocess
import traceback
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

class ExcelActivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FABSI - List of Service")
        self.root.resizable(True, True)

        self.display_columns = [
            "Select", "ID", "Stick-Built", "Module", "Document Number", "Activities", "Title", "Department",
            "Technical Unit", "Assigned to", "Progress", "Estimated internal",
            "Estimated external", "Start date", "Due date", "Notes", "Professional Role"
        ]
        self.df = pd.DataFrame(columns=self.display_columns)
        self.original_df = self.df.copy()
        self.selected_rows = set()  # Track selected rows

        self.file_path = ""
        self.tree = None
        self.entries = {}
        self.foreign_key_fields = [
            ("Stick-Built", "stickbuilts"),
            ("Module", "modules"),
            ("Activities", "activitiess"),
            ("Title", "titles"),
            ("Technical Unit", "technicalunits"),
            ("Assigned to", "employees"),
            ("Progress", "progresss"),
            ("Professional Role", "professionalunits")
        ]
        self.foreign_key_options = {}
        self.load_foreign_key_options_from_db()
        self.setup_ui()
    def load_foreign_key_options_from_db(self):
        # Print all available table names for debugging
        import sqlalchemy
        import re
        db_path = os.path.join(os.path.dirname(__file__), 'Workload.db')
        engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        insp = sqlalchemy.inspect(engine)
        available_tables = insp.get_table_names()
        print("Available tables in database:", available_tables)
        # Try to map expected table names to actual table names
        def normalize(name):
            return re.sub(r'[^a-z0-9]', '', name.lower())
        # List of possible table name variants for each field
        table_name_variants = {
            "stickbuilts": ["stickbuilt", "stickbuilts"],
            "modules": ["module", "modules"],
            "activitiess": ["activities", "activity", "activitiess"],
            "titles": ["title", "titles"],
            "technicalunits": ["technicalunit", "technicalunits"],
            "employees": ["employee", "employees"],
            "progresss": ["progress", "progresss"],
            "professionalunits": ["professionalunit", "professionalunits"],
            "projects": ["project", "projects"]
        }
        # Build a mapping from endpoint to actual table name in DB
        endpoint_to_table = {}
        for endpoint, variants in table_name_variants.items():
            found = None
            for t in available_tables:
                t_norm = normalize(t)
                for v in variants:
                    if t_norm == normalize(v):
                        found = t
                        break
                if found:
                    break
            if found:
                endpoint_to_table[endpoint] = found
            else:
                endpoint_to_table[endpoint] = None
        print("Endpoint to DB table mapping:", endpoint_to_table)
        # Fetch dropdown options directly from SQLite using SQLAlchemy models
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.automap import automap_base
        import traceback
        if not os.path.exists(db_path):
            from tkinter import messagebox
            messagebox.showerror("DB Error", f"Database file not found: {db_path}")
            print(f"Database file not found: {db_path}")
            return
        engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        Base = automap_base()
        try:
            Base.prepare(autoload_with=engine)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("DB Error", f"Could not reflect database tables.\n{e}")
            print("Could not reflect database tables:", e)
            traceback.print_exc()
            return
        Session = sessionmaker(bind=engine)
        session = Session()
        for field, endpoint in self.foreign_key_fields:
            try:
                table_name = endpoint_to_table.get(endpoint)
                if not table_name:
                    self.foreign_key_options[field] = []
                    print(f"No table mapping for endpoint: {endpoint}")
                    continue
                if not hasattr(Base.classes, table_name):
                    self.foreign_key_options[field] = []
                    print(f"Table '{table_name}' not found in database.")
                    from tkinter import messagebox
                    messagebox.showwarning("DB Table Missing", f"Table '{table_name}' not found in database.")
                    continue
                Model = getattr(Base.classes, table_name)
                options = session.query(Model).all()
                if not options:
                    print(f"No data found in table '{table_name}'.")
                    from tkinter import messagebox
                    messagebox.showwarning("DB Table Empty", f"No data found in table '{table_name}'.")
                self.foreign_key_options[field] = [
                    {"id": getattr(opt, "id", None), "name": getattr(opt, "name", str(opt))} for opt in options
                ]
            except Exception as e:
                self.foreign_key_options[field] = []
                print(f"Error loading options for {field} ({endpoint}): {e}")
                traceback.print_exc()
        session.close()
        self.project_combobox = None
        self.current_project = None
        self.tree_edit_widgets = {}
        self.header_labels = []
        self.filter_vars = {}

        self.header_frame = None
        self.sum_frame = None
        self.total_label_internal = None
        self.total_label_external = None
        self.role_summary_frame = None
        self.role_summary_tree = None
        self.role_summary_data = pd.DataFrame()
        self.edit_popup = None

    def setup_ui(self):
        # Create header frame - reduced height
        header_frame = tk.Frame(self.root, bg='white', height=60)  # Reduced from 100 to 60
        header_frame.pack(fill='x', padx=10, pady=(2, 5))  # Reduced padding
        header_frame.pack_propagate(False)

        # Left logo placeholder - smaller size
        left_logo_frame = tk.Frame(header_frame, width=70, height=50, bg='white')  # Reduced size
        left_logo_frame.pack(side='left', padx=10)  # Reduced padding
        left_logo_label = tk.Label(left_logo_frame, text="Logo 1", bg='white', font=("Arial", 8))
        left_logo_label.pack(expand=True)

        # Title in center - smaller font
        title_frame = tk.Frame(header_frame, bg='white')
        title_frame.pack(side='left', expand=True)
        title_label = tk.Label(
            title_frame, 
            text="FABSI - List of Service",
            font=("Arial", 18, "bold"),  # Reduced font size from 24 to 18
            bg='white',
            fg='#1976D2'
        )
        title_label.pack(expand=True)

        # Right logo placeholder - smaller size
        right_logo_frame = tk.Frame(header_frame, width=70, height=50, bg='white')  # Reduced size
        right_logo_frame.pack(side='right', padx=10)  # Reduced padding
        right_logo_label = tk.Label(right_logo_frame, text="Logo 2", bg='white', font=("Arial", 8))
        right_logo_label.pack(expand=True)

        # Add a separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=(0, 5))

        # Main content area
        main_top = tk.Frame(self.root)
        main_top.pack(fill='x', padx=10, pady=2)

        # Project selection dropdown
        project_label = tk.Label(main_top, text="Select Project:", font=("Arial", 10, "bold"))
        project_label.pack(side='left', padx=(0, 5))
        # Always reload project list from DB to avoid stale cache
        import sqlalchemy
        db_path = os.path.join(os.path.dirname(__file__), 'Workload.db')
        engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text('SELECT name FROM project')).fetchall()
            project_names = [row[0] for row in result]
        self.project_combobox = ttk.Combobox(main_top, values=project_names, state="readonly", width=30)
        self.project_combobox.pack(side='left', padx=(0, 20))
        self.project_combobox.bind("<<ComboboxSelected>>", self.on_project_selected)

        # Professional, compact form frame with max width
        self.entry_frame = tk.Frame(main_top, height=260, width=1300, bd=2, relief='groove', bg='#F7F7F7')
        self.entry_frame.pack_propagate(False)
        self.entry_frame.pack(side='left', padx=10, pady=5, anchor='nw')

        # Button frame with all options
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=15, pady=(5, 5))
        
        # Left side buttons
        tk.Button(button_frame, text="Professional Role Summary", 
                 command=self.open_role_summary_modal, 
                 bg="#1976D2", fg="white").pack(side='left', padx=(0, 10))
        tk.Button(button_frame, text="🔄 Clear All Filters", 
                 command=self.reset_filters, 
                 bg="#FF9800", fg="white").pack(side='left', padx=(0, 10))
        tk.Button(button_frame, text="🗑️ Delete Selected", 
                 command=self.delete_selected, 
                 bg="#F44336", fg="white").pack(side='left', padx=(0, 10))
        tk.Button(button_frame, text="✅ Select All", 
                 command=self.select_all_rows, 
                 bg="#9C27B0", fg="white").pack(side='left', padx=(0, 10))
        tk.Button(button_frame, text="❌ Deselect All", 
                 command=self.deselect_all_rows, 
                 bg="#607D8B", fg="white").pack(side='left', padx=(0, 10))
        
        # Export buttons
        export_frame = tk.Frame(button_frame, bg='#E3F2FD', bd=1, relief='groove')
        export_frame.pack(side='left', padx=10)
        
        tk.Label(export_frame, text="Export Data:", 
                bg='#E3F2FD', fg='#1976D2', 
                font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
        tk.Button(export_frame, text="📊 Excel", 
                 command=self.save_to_excel,
                 bg="#217346", fg="white",  # Excel green color
                 width=8).pack(side='left', padx=5, pady=2)
        
        tk.Button(export_frame, text="📄 PDF",
                 command=self.save_to_pdf,
                 bg="#DB4437", fg="white",  # PDF red color
                 width=8).pack(side='left', padx=5, pady=2)
        
        # Right side buttons
        tk.Button(button_frame, text="Agregar Actividad", 
                 command=self.add_row, 
                 bg="#388E3C", fg="white").pack(side='right')
        tk.Button(button_frame, text="Open File", 
                 command=self.open_file, 
                 bg="#0288D1", fg="white").pack(side='right', padx=(0, 10))

        # Remove the always-visible small table from the main UI
        # self.role_summary_frame = tk.Frame(summary_right, bd=1, relief='solid')
        # self.role_summary_frame.pack(padx=5, pady=5, anchor='ne')
        # self.role_summary_tree = ...

        # Add a visual separator between form and table
        separator = tk.Frame(self.root, height=2, bd=1, relief='sunken', bg="#BDBDBD")
        separator.pack(fill='x', padx=10, pady=5)

        # Create the main table frame (always present)
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill='both', expand=True, padx=15, pady=(5, 0))

        self.render_table()
        self.build_entry_fields()
        
        self.update_sum_labels()
        self.update_role_summary()

        # Start auto-updating totals every 400ms
        self.auto_update_totals()

        # Bottom frame with buttons (outside of scrollable area)
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10, fill='x')
        tk.Button(bottom_frame, text="Reset Filtros", command=self.reset_filters).pack(side='left', padx=10)
        tk.Button(bottom_frame, text="Save & Print in Excel", command=self.save_to_excel).pack(side='right', padx=10)
        tk.Button(bottom_frame, text="Save & Print in PDF", command=self.save_to_pdf).pack(side='right', padx=10)

    def on_checkbox_click(self, event):
        """Handle checkbox column clicks for row selection"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column:
            col_idx = int(column.replace('#', '')) - 1
            if col_idx == 0 and 'Select' in self.df.columns:  # First column is Select
                row_idx = int(item)
                if row_idx in self.selected_rows:
                    self.selected_rows.remove(row_idx)
                else:
                    self.selected_rows.add(row_idx)
                self.render_table()

    def select_all_rows(self):
        """Select all visible rows"""
        self.selected_rows.clear()  # Clear first to ensure clean state
        # Get the actual number of rows in the current DataFrame
        total_rows = len(self.df)
        print(f"DataFrame has {total_rows} rows")  # Debug
        
        # Add all current row indices to selected_rows (from 0 to total_rows-1)
        for i in range(total_rows):
            self.selected_rows.add(i)
        
        print(f"Selected {len(self.selected_rows)} rows out of {total_rows}: {sorted(self.selected_rows)}")  # Debug
        self.render_table()  # Re-render to show checkmarks

    def deselect_all_rows(self):
        """Deselect all rows"""
        self.selected_rows.clear()
        self.render_table()
    def open_role_summary_modal(self):
        """Open a modal window showing the Professional Role summary table"""
        if hasattr(self, 'role_summary_modal') and self.role_summary_modal and tk.Toplevel.winfo_exists(self.role_summary_modal):
            self.role_summary_modal.lift()
            return

        # Create new modal window
        self.role_summary_modal = tk.Toplevel(self.root)
        self.role_summary_modal.title("Professional Role & Hours Summary")
        self.role_summary_modal.geometry("400x400")
        self.role_summary_modal.transient(self.root)
        self.role_summary_modal.grab_set()

        # Add title label
        title_label = tk.Label(
            self.role_summary_modal,
            text="Total Hours per Professional Role",
            font=("Arial", 12, "bold"),
            fg="#1976D2",
            pady=10
        )
        title_label.pack()

        # Create main frame
        frame = tk.Frame(self.role_summary_modal, bd=1, relief='solid')
        frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Create treeview with fixed column widths
        self.role_summary_tree = ttk.Treeview(
            frame,
            columns=["Professional Role", "Manhours"],
            show='headings',
            height=15,
            style="Summary.Treeview"
        )

        # Configure treeview style
        style = ttk.Style()
        style.configure("Summary.Treeview",
                       background="white",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="white")
        style.configure("Summary.Treeview.Heading",
                       font=('Arial', 9, 'bold'),
                       background="#E3F2FD")

        # Configure headers
        self.role_summary_tree.heading("Professional Role", text="Professional Role",
                                     command=lambda: self.sort_summary("Professional Role"))
        self.role_summary_tree.heading("Manhours", text="Internal Hours",
                                     command=lambda: self.sort_summary("Manhours"))

        # Configure columns
        self.role_summary_tree.column("Professional Role", width=250, anchor='w')
        self.role_summary_tree.column("Manhours", width=120, anchor='e')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.role_summary_tree.yview)
        self.role_summary_tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.role_summary_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Update the summary data
        self.update_role_summary()

        # Add close button
        close_btn = tk.Button(
            self.role_summary_modal,
            text="Close",
            command=self.role_summary_modal.destroy,
            bg="#1976D2",
            fg="white",
            padx=20,
            font=("Arial", 10)
        )
        close_btn.pack(pady=10)

    def sort_column(self, column, ascending=True):
        """Sort the data by column"""
        if self.filter_popup:
            self.filter_popup.destroy()
        
        if column in self.df.columns:
            self.df = self.df.sort_values(by=column, ascending=ascending, na_position='last')
            self.render_table()
    
    def apply_column_filter(self, column, selected_indices):
        """Apply filter to the column based on selected values"""
        if not selected_indices:  # If nothing selected, show all
            self.clear_column_filter(column)
            return
            
        # Get selected values from listbox
        values = []
        for idx in selected_indices:
            values.append(self.current_filter_values[idx])
        
        # Apply filter to DataFrame
        self.df = self.df[self.df[column].astype(str).isin(values)]
        
        # Close popup and update display
        if self.filter_popup:
            self.filter_popup.destroy()
        self.render_table()
        self.update_sum_labels()
        self.update_role_summary()
    
    def clear_column_filter(self, column):
        """Clear filter for the column and show all values"""
        # Reset to original data
        display_cols_without_select_id = [col for col in self.display_columns if col not in ['Select', 'ID']]
        available_cols = [col for col in display_cols_without_select_id if col in self.original_df.columns]
        
        # Create a new DataFrame from original data
        self.df = self.original_df[available_cols].copy()
        
        # Add Select and ID columns
        self.df.insert(0, 'Select', False)
        self.df.insert(1, 'ID', range(1, len(self.df) + 1))
        
        # Close popup and update display
        if self.filter_popup:
            self.filter_popup.destroy()
        self.render_table()
        self.update_sum_labels()
        self.update_role_summary()

    def sort_summary(self, column):
        """Sort the role summary table by clicking on headers"""
        if not hasattr(self, 'role_summary_tree') or not self.role_summary_tree:
            return

        # Get all items except the total row
        items = [(self.role_summary_tree.set(item, column), item)
                for item in self.role_summary_tree.get_children('')]
        
        if not items:
            return

        # Remove the total row if it exists (last row)
        if items[-1][0] == "TOTAL":
            total_values = self.role_summary_tree.item(items[-1][1])['values']
            items.pop()
        else:
            total_values = None

        # Sort items
        items.sort(reverse=hasattr(self, '_summary_sort_reverse') and not self._summary_sort_reverse)
        self._summary_sort_reverse = not getattr(self, '_summary_sort_reverse', False)

        # Move items in the tree
        for idx, (_, item) in enumerate(items):
            self.role_summary_tree.move(item, '', idx)

        # Re-add total row at the bottom if it existed
        if total_values:
            self.role_summary_tree.insert("", "end", values=total_values, tags=('total',))

        # (moved to setup_ui)

    def auto_update_totals(self):
        self.update_sum_labels()
        self.update_role_summary()
        self.root.after(400, self.auto_update_totals)

    def update_sum_labels(self):
        # No longer need the separate labels since we're using table row
        # But keep the calculation for debugging and potential future use
        
        try:
            df = self.df
            col_internal = "Estimated internal"
            col_external = "Estimated external"
            
            # Calculate internal total - only numeric values
            total_internal = 0
            if col_internal in df.columns and len(df) > 0:
                internal_series = pd.to_numeric(df[col_internal], errors='coerce')
                total_internal = internal_series.dropna().sum()
            
            # Calculate external total - only numeric values
            total_external = 0
            if col_external in df.columns and len(df) > 0:
                external_series = pd.to_numeric(df[col_external], errors='coerce')
                total_external = external_series.dropna().sum()
                
        except Exception as e:
            print(f"Error calculating sums: {e}")
            total_internal = 0
            total_external = 0
        
        # Update the summation row in the table if it exists
        self.update_summation_row_in_table(total_internal, total_external)
        
        print(f"Updated totals: Internal={total_internal:.2f}, External={total_external:.2f}")  # Debug

    def update_summation_row_in_table(self, total_internal, total_external):
        """Update the summation row values in the table"""
        if not hasattr(self, 'tree') or not self.tree:
            return
            
        try:
            # Check if the summation row exists
            if self.tree.exists('TOTALS_ROW'):
                # Update the existing summation row
                row_values = []
                for col in self.df.columns:
                    if col == "Select":
                        row_values.append("📊")
                    elif col == "ID":
                        row_values.append("TOTAL")
                    elif col == "Activities":
                        row_values.append("📈 TOTAL PROJECT HOURS")
                    elif col == "Estimated internal":
                        row_values.append(f"{total_internal:,.2f}")
                    elif col == "Estimated external":
                        row_values.append(f"{total_external:,.2f}")
                    elif col in ["Department"]:
                        row_values.append("ALL")
                    else:
                        row_values.append("")
                
                # Update the row values
                self.tree.item('TOTALS_ROW', values=row_values)
        except Exception as e:
            print(f"Error updating summation row: {e}")

    def update_role_summary(self):
        """Update the role summary based on the currently displayed/filtered data"""
        if not hasattr(self, 'role_summary_tree') or not self.role_summary_tree:
            return
        
        # Clear existing items
        for row in self.role_summary_tree.get_children():
            self.role_summary_tree.delete(row)
        
        # Calculate summary from current filtered data
        if "Professional Role" in self.df.columns and "Estimated internal" in self.df.columns:
            try:
                # Create summary from current filtered data
                summary = (
                    self.df.groupby("Professional Role")["Estimated internal"]
                    .apply(lambda x: pd.to_numeric(x, errors='coerce').sum())
                    .reset_index()
                )
                
                # Clean up the summary data
                summary = summary[summary["Professional Role"].notnull() & (summary["Professional Role"] != "")]
                summary = summary[summary["Estimated internal"] > 0]  # Only show roles with hours
                summary = summary.sort_values("Estimated internal", ascending=False)  # Sort by hours descending
                self.role_summary_data = summary
                
                # Add rows to the tree
                total_hours = 0
                for _, row in summary.iterrows():
                    hours = row["Estimated internal"] if pd.notnull(row["Estimated internal"]) else 0
                    total_hours += hours
                    manhours = f"{hours:,.0f}" if hours > 0 else "0"
                    self.role_summary_tree.insert("", "end", values=(row["Professional Role"], manhours))
                
                # Add total row if there are entries
                if len(summary) > 0:
                    self.role_summary_tree.insert("", "end", values=("TOTAL", f"{total_hours:,.0f}"),
                                                tags=('total',))
                    self.role_summary_tree.tag_configure('total', background='#E3F2FD',
                                                       font=('Arial', 9, 'bold'))
            except Exception as e:
                print(f"Error updating role summary: {e}")
                traceback.print_exc()

    def edit_role_summary_cell(self, event):
        # Permite editar la tabla resumen haciendo doble clic
        item = self.role_summary_tree.identify_row(event.y)
        column = self.role_summary_tree.identify_column(event.x)
        if not item or not column:
            return
        col_idx = int(column.replace('#', '')) - 1
        col_name = ["Professional Role", "Estimated internal"][col_idx]
        x, y, width, height = self.role_summary_tree.bbox(item, column)
        value = self.role_summary_tree.item(item, "values")[col_idx]
        # Evita más de una edición a la vez
        if self.edit_popup:
            self.edit_popup.destroy()
        self.edit_popup = tk.Entry(self.role_summary_tree, width=20)
        self.edit_popup.insert(0, value)
        self.edit_popup.place(x=x, y=y, width=width, height=height)
        self.edit_popup.focus()
        def on_focus_out(event):
            new_value = self.edit_popup.get()
            values = list(self.role_summary_tree.item(item, "values"))
            values[col_idx] = new_value
            self.role_summary_tree.item(item, values=values)
            self.edit_popup.destroy()
            self.edit_popup = None
        self.edit_popup.bind("<Return>", on_focus_out)
        self.edit_popup.bind("<FocusOut>", on_focus_out)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.file_path = path
            if not self.current_project:
                messagebox.showinfo("Select Project", "Please select a project first.")
                return
            import sqlalchemy
            import pandas as pd
            db_path = os.path.join(os.path.dirname(__file__), 'Workload.db')
            engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
            # Get project_id
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text('SELECT id FROM project WHERE name = :name'), {'name': self.current_project}).fetchone()
                project_id = result[0] if result else None
            if not project_id:
                messagebox.showerror("Error", "Project not found in database.")
                return
            try:
                # Try to load the sheet with the same name as the project, else fallback to first sheet
                try:
                    df = pd.read_excel(path, sheet_name=self.current_project)
                except Exception:
                    df = pd.read_excel(path)
                # Map Excel columns to DB columns
                field_to_db = {
                    "Stick-Built": "stick_built_id",
                    "Module": "module_id",
                    "Activities": "activities_id",
                    "Title": "title_id",
                    "Technical Unit": "technical_unit_id",
                    "Assigned to": "employee_id",
                    "Progress": "progress_id",
                    "Professional Role": "professional_unit_id",
                    "Department": "department",
                    "Estimated internal": "estimated_internal_hours",
                    "Estimated external": "estimated_external_hours",
                    "Start date": "start_date",
                    "Due date": "due_date",
                    "Notes": "notes"
                }
                # Build foreign key name->id maps for all dropdowns
                fk_maps = {}
                for col, options in self.foreign_key_options.items():
                    fk_maps[col] = {o['name']: o['id'] for o in options if o['id'] is not None}
                # Prepare rows for insert
                rows = []
                for _, row in df.iterrows():
                    data = {'project_id': project_id}
                    for col, db_col in field_to_db.items():
                        if db_col.endswith('_id'):
                            val = row.get(col, None)
                            data[db_col] = fk_maps.get(col, {}).get(val, None) if pd.notnull(val) else None
                        else:
                            data[db_col] = row.get(col, None)
                    rows.append(data)
                # Insert all rows in a transaction
                with engine.begin() as conn:
                    for data in rows:
                        columns = ', '.join(data.keys())
                        placeholders = ', '.join([f':{k}' for k in data.keys()])
                        insert_sql = f"INSERT INTO service ({columns}) VALUES ({placeholders})"
                        conn.execute(sqlalchemy.text(insert_sql), data)
                logging.info(f"Imported {len(rows)} rows from Excel to service table for project {self.current_project}")
                messagebox.showinfo("Import", f"Imported {len(rows)} rows successfully.")
                self.on_project_selected(None)
            except Exception as e:
                import traceback
                logging.error(f"Failed to import from Excel: {e}")
                logging.error(traceback.format_exc())
                messagebox.showerror("Import Error", f"Failed to import: {e}")

    def load_project_data(self, sheet_name):
        if not self.file_path:
            return
        try:
            df_loaded = pd.read_excel(self.file_path, sheet_name=sheet_name)
            cols_present = [c for c in self.display_columns if c in df_loaded.columns]
            extra_cols = [c for c in df_loaded.columns if c not in cols_present]
            df_loaded = df_loaded[cols_present + extra_cols]
            self.df = df_loaded
            self.original_df = self.df.copy()
            self.render_table()
            self.build_entry_fields()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la hoja '{sheet_name}':\n{e}")

    def on_project_selected(self, event):
        project_name = self.project_combobox.get()
        self.current_project = project_name
        # Fetch project ID directly from DB
        import sqlalchemy
        db_path = os.path.join(os.path.dirname(__file__), 'Workload.db')
        engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text('SELECT id FROM project WHERE name = :name'), {'name': project_name}).fetchone()
            project_id = result[0] if result else None
        # Load services for this project directly from DB
        import pandas as pd
        try:
            if project_id:
                # Join foreign key tables to get display names
                query = '''
                SELECT
                    s.id,
                    sb.name AS "Stick-Built",
                    m.name AS "Module",
                    s.id AS "Document Number",
                    a.name AS "Activities",
                    t.name AS "Title",
                    s.department AS "Department",
                    tu.name AS "Technical Unit",
                    e.name AS "Assigned to",
                    p.name AS "Progress",
                    s.estimated_internal_hours AS "Estimated internal",
                    s.estimated_external_hours AS "Estimated external",
                    s.start_date AS "Start date",
                    s.due_date AS "Due date",
                    s.notes AS "Notes",
                    pu.name AS "Professional Role"
                FROM service s
                LEFT JOIN stick_built sb ON s.stick_built_id = sb.id
                LEFT JOIN module m ON s.module_id = m.id
                LEFT JOIN activities a ON s.activities_id = a.id
                LEFT JOIN title t ON s.title_id = t.id
                LEFT JOIN technical_unit tu ON s.technical_unit_id = tu.id
                LEFT JOIN employee e ON s.employee_id = e.id
                LEFT JOIN progress p ON s.progress_id = p.id
                LEFT JOIN professional_unit pu ON s.professional_unit_id = pu.id
                WHERE s.project_id = :project_id
                '''
                with engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text(query), {'project_id': project_id})
                    rows = result.fetchall()
                    columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                # Store original data WITHOUT Select and ID columns for filtering
                if not df.empty:
                    # Store clean original data
                    display_cols_without_select_id = [col for col in self.display_columns if col not in ['Select', 'ID']]
                    available_cols = [col for col in display_cols_without_select_id if col in df.columns]
                    self.original_df = df[available_cols].copy()
                    
                    # Add the Select column (checkbox) and ID counter for display
                    df.insert(0, 'Select', False)
                    df.insert(1, 'ID', range(1, len(df) + 1))
                    # Reorder to match display_columns
                    final_cols = ['Select', 'ID'] + available_cols
                    self.df = df[final_cols]
                else:
                    self.original_df = pd.DataFrame(columns=[col for col in self.display_columns if col not in ['Select', 'ID']])
                    self.df = pd.DataFrame(columns=self.display_columns)
                
                self.render_table()
                self.update_sum_labels()  # Update totals after loading data
            else:
                self.df = pd.DataFrame(columns=self.display_columns)
                self.original_df = pd.DataFrame(columns=[col for col in self.display_columns if col not in ['Select', 'ID']])
                self.render_table()
                self.update_sum_labels()  # Update totals even when empty
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load services for project: {e}")

    def build_entry_fields(self):
        for widget in self.entry_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        # Define the order and grouping of fields for a compact grid
        fields = [
            ["Stick-Built", "Module", "Activities", "Title"],
            ["Technical Unit", "Assigned to", "Progress", "Professional Role"],
            ["Department", "Estimated internal", "Estimated external", "Start date"],
            ["Due date", "Notes"]
        ]
        label_opts = {'anchor': 'w', 'bg': '#F7F7F7', 'font': ('Arial', 9)}
        entry_opts = {'font': ('Arial', 10)}
        
        # Set column weights for better distribution
        self.entry_frame.grid_columnconfigure(0, weight=2)  # Stick-Built
        self.entry_frame.grid_columnconfigure(1, weight=2)  # Module
        self.entry_frame.grid_columnconfigure(2, weight=4)  # Activities (double width)
        self.entry_frame.grid_columnconfigure(3, weight=2)  # Title
        
        # Define field widths
        field_widths = {
            "Stick-Built": 30,
            "Module": 30,
            "Activities": 60,  # Much wider for Activities
            "Title": 35,
            "Technical Unit": 35,
            "Assigned to": 35,
            "Progress": 25,
            "Professional Role": 35,
            "Department": 25,
            "Estimated internal": 25,
            "Estimated external": 25,
            "Start date": 25,
            "Due date": 25,
            "Notes": 70  # Wider for Notes
        }
        
        for row_idx, row in enumerate(fields):
            for col_idx, col in enumerate(row):
                # Create label
                lbl = tk.Label(self.entry_frame, text=col, **label_opts)
                lbl.grid(row=row_idx*2, column=col_idx, sticky='w', padx=10, pady=(10,0))
                
                # Create field
                width = field_widths.get(col, 30)  # Default width if not specified
                
                if col in self.foreign_key_options:
                    options = self.foreign_key_options[col]
                    widget = ttk.Combobox(self.entry_frame, width=width, state="readonly", font=('Arial', 11))
                    widget['values'] = [o['name'] for o in options]
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, sticky='we', padx=10, pady=(0,10))
                elif col in ["Department", "Estimated internal", "Estimated external", "Start date", "Due date"]:
                    widget = tk.Entry(self.entry_frame, width=width, **entry_opts)
                    if col == "Department":
                        widget.insert(0, "FABSI")
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, sticky='we', padx=10, pady=(0,10))
                elif col == "Notes":
                    widget = tk.Entry(self.entry_frame, width=width, **entry_opts)
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, columnspan=2, sticky='we', padx=10, pady=(0,10))
                else:
                    widget = tk.Entry(self.entry_frame, width=width, **entry_opts)
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, sticky='we', padx=10, pady=(0,10))

    def update_activities_filter(self, event):
        text = self.entries["Activities"].get()
        all_activities = self.df["Activities"].dropna().unique().tolist() if "Activities" in self.df.columns else []
        if text:
            matches = [act for act in all_activities if text.lower() in act.lower()]
            self.entries["Activities"]['values'] = matches if matches else all_activities
        else:
            self.entries["Activities"]['values'] = all_activities

    def render_table(self):
        """Render the main table with data"""
        # Clear existing widgets
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Create main container
        main_container = ttk.Frame(self.table_frame)
        main_container.pack(fill='both', expand=True)
        
        # Create the container for our data table
        self.scrollable_frame = ttk.Frame(main_container)
        self.scrollable_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create and configure treeview with scrollbars
        tree_frame = ttk.Frame(self.scrollable_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        self.tree = ttk.Treeview(tree_frame, columns=list(self.df.columns), show='headings', height=15)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configure headers and columns with increased widths
        column_widths = {
            "Select": 45,               # Increased for better checkbox visibility
            "ID": 50,                  # Increased for larger numbers
            "Stick-Built": 100,        # Increased for longer names
            "Module": 100,             # Increased for longer module names
            "Activities": 400,          # Significantly increased for full activity descriptions
            "Title": 150,              # Increased for full titles
            "Department": 100,         # Increased for department names
            "Technical Unit": 150,     # Increased for longer unit names
            "Assigned to": 150,        # Increased for full names
            "Progress": 100,           # Increased for progress status
            "Estimated internal": 100,  # Increased for larger numbers
            "Estimated external": 100,  # Increased for larger numbers
            "Start date": 100,         # Increased for full date format
            "Due date": 100,           # Increased for full date format
            "Notes": 300,              # Significantly increased for full notes
            "Professional Role": 200    # Increased for full role names
        }
        
        header_map = {
            "Select": "☑", "ID": "ID", "Stick-Built": "Stick-Built",
            "Module": "Module", "Activities": "Activities",
            "Title": "Title", "Department": "Department",
            "Technical Unit": "Tech. Unit", "Assigned to": "Assigned To",
            "Progress": "Progress", "Notes": "Notes",
            "Professional Role": "Professional Role",
            "Estimated internal": "Est. Internal",
            "Estimated external": "Est. External",
            "Start date": "Start Date", "Due date": "Due Date"
        }
        
        # Configure columns with improved readability and Excel-like filtering
        for col in self.df.columns:
            # Add filter arrow only for non-Select and non-ID columns
            if col not in ["Select", "ID"]:
                header_text = f"{header_map.get(col, col)} ▼"
                # Use functools.partial to avoid lambda closure issues
                from functools import partial
                self.tree.heading(col, text=header_text, command=partial(self.show_filter_menu, col))
            else:
                header_text = header_map.get(col, col)
                self.tree.heading(col, text=header_text)
            
            width = column_widths.get(col, 100)
            anchor = 'w' if col in ["Activities", "Title", "Notes", "Technical Unit", 
                                  "Assigned to", "Professional Role", "Department"] else 'center'
            self.tree.column(col, width=width, minwidth=50, stretch=True, anchor=anchor)
        
        # Style the treeview with increased row height for better readability
        style = ttk.Style()
        style.configure("Treeview",
                       background="white",
                       foreground="black",
                       rowheight=40,  # Increased row height
                       fieldbackground="white",
                       font=('Arial', 10))  # Slightly larger font
        
        style.configure("Treeview.Heading",
                       background="#D9D9D9",
                       font=('Arial', 9, 'bold'))
        
        # Insert data
        for i, row in self.df.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            row_values = list(row)
            if len(row_values) > 0 and 'Select' in self.df.columns:
                checkbox_idx = self.df.columns.get_loc('Select')
                row_values[checkbox_idx] = '☑' if i in self.selected_rows else '☐'
            self.tree.insert('', 'end', iid=str(i), values=row_values, tags=(tag,))
        
        # ADD SUMMATION ROW as the last row of the table
        self.add_summation_row_to_table()
        
        # Configure row colors
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#F8F8F8')
        # Configure summation row with bright colors
        self.tree.tag_configure('total_row', background='#FFD700', foreground='#000000', font=('Arial', 12, 'bold'))
        
        # Bind events
        self.tree.bind("<Double-1>", self.edit_cell)
        self.tree.bind("<Button-1>", self.on_checkbox_click)
        
        # Update the totals after rendering the table
        self.update_sum_labels()

    def add_summation_row_to_table(self):
        """Add a summation row as the last row of the table"""
        # Calculate totals
        total_internal = 0
        total_external = 0
        
        try:
            if "Estimated internal" in self.df.columns and len(self.df) > 0:
                internal_series = pd.to_numeric(self.df["Estimated internal"], errors='coerce')
                total_internal = internal_series.dropna().sum()
            
            if "Estimated external" in self.df.columns and len(self.df) > 0:
                external_series = pd.to_numeric(self.df["Estimated external"], errors='coerce')
                total_external = external_series.dropna().sum()
        except Exception as e:
            print(f"Error calculating totals for summation row: {e}")
        
        # Create summation row values
        row_values = []
        for col in self.df.columns:
            if col == "Select":
                row_values.append("📊")  # Special icon for totals row
            elif col == "ID":
                row_values.append("TOTAL")
            elif col == "Activities":
                row_values.append("📈 TOTAL PROJECT HOURS")
            elif col == "Estimated internal":
                row_values.append(f"{total_internal:,.2f}")
            elif col == "Estimated external":
                row_values.append(f"{total_external:,.2f}")
            elif col in ["Department"]:
                row_values.append("ALL")
            else:
                row_values.append("")  # Empty for other columns
        
        # Insert the summation row with special styling
        self.tree.insert('', 'end', iid='TOTALS_ROW', values=row_values, tags=('total_row',))

    def get_visible_columns(self):
        """Get list of columns to display (excluding Document Number)"""
        columns = [col for col in self.df.columns if col != "Document Number"]
        return columns

    def create_unified_header(self):
        """Create header with filters that scrolls with data"""
        # Reset any existing filter menus
        self.filter_menus = {}
        
        header_map = {
            "Select": "☑",
            "ID": "ID",
            "Estimated internal": "Est. Internal",
            "Estimated external": "Est. External", 
            "Start date": "Start Date",
            "Due date": "Due Date",
            "Stick-Built": "Stick-Built",
            "Module": "Module",
            "Activities": "Activities",
            "Title": "Title",
            "Department": "Department",
            "Technical Unit": "Tech. Unit",
            "Assigned to": "Assigned To",
            "Progress": "Progress",
            "Notes": "Notes",
            "Professional Role": "Professional Role"
        }
        
        column_widths = {
            "Select": 35,
            "ID": 35,
            "Stick-Built": 100,
            "Module": 100,
            "Activities": 500,    # Significantly increased for better readability
            "Title": 150,
            "Department": 100,
            "Technical Unit": 180,
            "Assigned to": 150,
            "Progress": 80,
            "Estimated internal": 100,
            "Estimated external": 100,
            "Start date": 80,
            "Due date": 80,
            "Notes": 250,
            "Professional Role": 180
        }
        
        header_height = 35  # Further reduced height
        header_frame = tk.Frame(self.scrollable_frame, height=header_height, bg="#D9D9D9", relief='groove', bd=1)
        header_frame.pack(fill='x', pady=(0,2))
        header_frame.pack_propagate(False)
        
        self.header_labels = []
        self.filter_vars = {}
        self.filter_menus = {}  # Store filter menu buttons
        x_offset = 0
        
        for idx, col in enumerate(self.df.columns):
            txt = header_map.get(col, col)
            width = column_widths.get(col, 100)
            
            cell_frame = tk.Frame(header_frame, width=width, height=header_height, bg="#D9D9D9", 
                                relief='groove', bd=1)
            cell_frame.place(x=x_offset, y=0, width=width, height=header_height)
            cell_frame.pack_propagate(False)
            
            # Header container with text and filter button
            header_container = tk.Frame(cell_frame, bg="#D9D9D9")
            header_container.pack(fill='x', expand=True, pady=(2,0))
            
            # Header text label
            header_label = tk.Label(header_container, text=txt, bg="#D9D9D9", 
                                  font=('Arial', 8, 'bold'), anchor='w')
            header_label.pack(side='left', padx=(2,0))
            
            # Filter button - only add for non-Select and non-ID columns
            if col not in ["Select", "ID"]:
                filter_btn = tk.Button(header_container, text="↓", font=('Arial', 7),
                                     width=2, height=1, relief='flat', bg="#D9D9D9",
                                     command=lambda c=col: self.show_column_filter(c))
                filter_btn.pack(side='right', padx=(0,1))
                self.filter_menus[col] = filter_btn
            
            x_offset += width
            
    def show_column_filter(self, column):
        """Show Excel-like filter popup for the column"""
        # Close existing popup if any
        if hasattr(self, 'filter_popup') and self.filter_popup:
            self.filter_popup.destroy()
        
        # Get button widget and position
        filter_btn = self.filter_menus[column]
        x = filter_btn.winfo_rootx()
        y = filter_btn.winfo_rooty() + filter_btn.winfo_height()
        
        # Create popup window
        self.filter_popup = tk.Toplevel(self.root)
        self.filter_popup.wm_overrideredirect(True)
        self.filter_popup.geometry(f"200x350+{x}+{y}")  # Made taller to fit all elements
        self.filter_popup.configure(bg='white', bd=1, relief='solid')
        
        # Main container frame
        main_frame = tk.Frame(self.filter_popup, bg='white')
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Store current filter values for search
        self.current_filter_values = []
        if column in self.df.columns:
            self.current_filter_values = sorted(self.df[column].unique().tolist())
            self.current_filter_values = [str(val) for val in self.current_filter_values if pd.notnull(val)]
        
        # Frame for sort options at the top
        sort_frame = tk.Frame(main_frame, bg='white')
        sort_frame.pack(fill='x', pady=(0, 2))
        
        # Sort buttons
        tk.Button(sort_frame, text="Sort A → Z", 
                 command=lambda: self.sort_column(column, ascending=True),
                 relief='flat', bg='white', anchor='w').pack(fill='x')
        tk.Button(sort_frame, text="Sort Z → A",
                 command=lambda: self.sort_column(column, ascending=False),
                 relief='flat', bg='white', anchor='w').pack(fill='x')
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=2)
        
        # Filter options frame
        filter_frame = tk.Frame(self.filter_popup, bg='white')
        filter_frame.pack(fill='both', expand=True, padx=2)
        
        # Search entry
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=search_var, 
                              font=('Arial', 9))
        search_entry.pack(fill='x', pady=2)
        
        # Checkboxes container with scrollbar
        checkbox_container = tk.Frame(filter_frame)
        checkbox_container.pack(fill='both', expand=True)
        
        # Create canvas for scrolling checkboxes
        canvas = tk.Canvas(checkbox_container, bg='white')
        scrollbar = ttk.Scrollbar(checkbox_container, orient="vertical", command=canvas.yview)
        
        # Frame to hold checkboxes
        checkbox_frame = tk.Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=checkbox_frame, anchor='nw')
        
        # Dictionary to store checkbox variables
        self.filter_vars = {}
        
        # Add checkboxes
        for val in self.current_filter_values:
            var = tk.BooleanVar()
            self.filter_vars[val] = var
            cb = ttk.Checkbutton(checkbox_frame, text=str(val), variable=var)
            cb.pack(anchor='w', padx=5, pady=1)
        
        # Configure scrolling
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        checkbox_frame.bind('<Configure>', on_frame_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Update filter options based on search
        def update_search(*args):
            search_text = search_var.get().lower()
            for widget in checkbox_frame.winfo_children():
                if isinstance(widget, ttk.Checkbutton):
                    if search_text in widget.cget('text').lower():
                        widget.pack(anchor='w', padx=5, pady=1)
                    else:
                        widget.pack_forget()
        
        search_var.trace('w', update_search)
        
        # Buttons frame at the bottom
        btn_frame = tk.Frame(self.filter_popup, bg='white')
        btn_frame.pack(side='bottom', fill='x', padx=2, pady=4)
        
        # Button styles
        button_style = {'font': ('Arial', 8), 'width': 8, 'pady': 2}
        
        # Pack buttons with equal spacing
        tk.Button(btn_frame, text="Apply", 
                 command=lambda: self.apply_column_filter(column),
                 bg='#1976D2', fg='white', **button_style).pack(side='left', expand=True, padx=2)
        tk.Button(btn_frame, text="Clear",
                 command=lambda: self.clear_column_filter(column),
                 bg='#FF9800', fg='white', **button_style).pack(side='left', expand=True, padx=2)
        tk.Button(btn_frame, text="Cancel",
                 command=self.filter_popup.destroy,
                 bg='#F44336', fg='white', **button_style).pack(side='left', expand=True, padx=2)
        
        # Handle click outside popup
        def on_click_outside(event):
            if event.widget == self.filter_popup:
                self.filter_popup.destroy()
        
        self.filter_popup.bind('<Button-1>', on_click_outside)
        
        # Set focus to search entry
        search_entry.focus()

    def update_filter_list(self, search_text, listbox):
        """Update the filter listbox based on search text"""
        listbox.delete(0, tk.END)
        items = [item for item in self.current_filter_values 
                if str(search_text).lower() in str(item).lower()]
        for item in sorted(items):
            listbox.insert(tk.END, str(item))

    def sort_column(self, column, ascending=True):
        """Sort the data by column"""
        if self.filter_popup:
            self.filter_popup.destroy()
        
        if column in self.df.columns:
            self.df = self.df.sort_values(by=column, ascending=ascending, na_position='last')
            self.render_table()

    def apply_column_filter(self, column, *args):
        """Apply filter to the column based on selected checkboxes"""
        # Get selected values from checkboxes
        selected_values = [val for val, var in self.filter_vars.items() if var.get()]
        
        if not selected_values:  # If nothing selected, show all
            self.clear_column_filter(column)
            return
        
        # Apply filter
        mask = self.df[column].astype(str).isin([str(v) for v in selected_values])
        self.df = self.df[mask]
        
        if self.filter_popup:
            self.filter_popup.destroy()
            
        self.render_table()
        self.update_sum_labels()
        self.update_role_summary()

    def clear_column_filter(self, column):
        """Clear filter for the column"""
        # Reset to original data for this column
        self.df = self.original_df.copy()
        if self.filter_popup:
            self.filter_popup.destroy()
        self.render_table()
        self.update_sum_labels()
        self.update_role_summary()

    def create_data_rows(self):
        """Create the data rows section"""
        # Enhanced treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white",
            bordercolor="#BFBFBF",
            borderwidth=1,
            font=('Arial', 9)
        )
        
        # Create treeview for data
        self.tree = ttk.Treeview(
            self.scrollable_frame,
            columns=list(self.df.columns),
            show='',  # Hide native headers
            selectmode='extended',
            height=15  # Limit height so summation is visible
        )
        self.tree.pack(fill='x', pady=(0,2))
        
        self.tree.bind("<Double-1>", self.edit_cell)
        self.tree.bind("<Button-1>", self.on_checkbox_click)
        
        # Column widths (updated to match header)
        column_widths = {
            "Select": 35, "ID": 35, "Stick-Built": 70, "Module": 65, "Document Number": 65,
            "Activities": 280, "Title": 85, "Department": 75, "Technical Unit": 120,
            "Assigned to": 100, "Progress": 70, "Estimated internal": 75,
            "Estimated external": 75, "Start date": 70, "Due date": 70,
            "Notes": 180, "Professional Role": 130
        }
        
        for col in self.df.columns:
            anchor = 'w' if col in ["Activities", "Technical Unit", "Assigned to", "Professional Role"] else 'c'
            self.tree.column(col, width=column_widths.get(col, 120), anchor=anchor, stretch=False)
        
        # Add data rows
        for i, row in self.df.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            row_values = list(row)
            if len(row_values) > 0 and 'Select' in self.df.columns:
                checkbox_idx = self.df.columns.get_loc('Select')
                row_values[checkbox_idx] = '☑' if i in self.selected_rows else '☐'
            self.tree.insert('', 'end', iid=str(i), values=row_values, tags=(tag,))
        
        # Row styling
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#F8F8F8')

    def show_filter_menu(self, column):
        """Show Excel-like filter menu for the selected column"""
        print(f"Opening filter for column: {column}")  # Debug
        
        # Close any existing filter window
        if hasattr(self, 'filter_window') and self.filter_window:
            try:
                self.filter_window.destroy()
            except:
                pass
        
        # Create new filter window with proper layout
        self.filter_window = tk.Toplevel(self.root)
        self.filter_window.title(f"Filter - {column}")
        self.filter_window.geometry("350x550")  # Increased size for better visibility
        self.filter_window.resizable(False, False)
        self.filter_window.transient(self.root)
        self.filter_window.grab_set()
        
        # Position the window near the mouse cursor
        try:
            x = self.root.winfo_pointerx() - 175
            y = self.root.winfo_pointery() - 50
            self.filter_window.geometry(f"350x550+{x}+{y}")
        except:
            pass
        
        # Main container with fixed structure
        main_frame = tk.Frame(self.filter_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text=f"Filter: {column}", 
                              font=('Arial', 12, 'bold'), bg='white')
        title_label.pack(pady=(0, 10))
        
        # Sort section
        sort_frame = tk.LabelFrame(main_frame, text="Sort Options", bg='white', font=('Arial', 9, 'bold'))
        sort_frame.pack(fill='x', pady=(0, 10))
        
        # Sort buttons
        sort_btn_frame = tk.Frame(sort_frame, bg='white')
        sort_btn_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Button(sort_btn_frame, text="↑ Sort A to Z", 
                 command=lambda: self.apply_sort(column, True),
                 bg='#E8F4FD', relief='flat', font=('Arial', 9),
                 width=15, pady=5).pack(side='left', padx=(0, 5))
        
        tk.Button(sort_btn_frame, text="↓ Sort Z to A",
                 command=lambda: self.apply_sort(column, False), 
                 bg='#E8F4FD', relief='flat', font=('Arial', 9),
                 width=15, pady=5).pack(side='left')
        
        # Filter section with FIXED height to ensure buttons show
        filter_frame = tk.LabelFrame(main_frame, text="Filter Values", bg='white', 
                                   font=('Arial', 9, 'bold'), height=320)
        filter_frame.pack(fill='x', pady=(0, 10))
        filter_frame.pack_propagate(False)  # Prevent expansion
        
        # Search box
        search_frame = tk.Frame(filter_frame, bg='white')
        search_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(search_frame, text="Search:", bg='white', font=('Arial', 9)).pack(anchor='w')
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 9))
        search_entry.pack(fill='x', pady=2)
        
        # Select All checkbox
        select_all_frame = tk.Frame(filter_frame, bg='white')
        select_all_frame.pack(fill='x', padx=5, pady=2)
        
        self.select_all_var = tk.BooleanVar(value=True)
        select_all_cb = tk.Checkbutton(select_all_frame, text="Select All", 
                                      variable=self.select_all_var, bg='white',
                                      font=('Arial', 9, 'bold'),
                                      command=self.toggle_all_checkboxes)
        select_all_cb.pack(anchor='w')
        
        # Values list with scrollbar - FIXED HEIGHT for proper scrolling
        list_frame = tk.Frame(filter_frame, bg='white', height=220)
        list_frame.pack(fill='x', padx=5, pady=5)
        list_frame.pack_propagate(False)  # Prevent expansion
        
        # Create scrollable frame for checkboxes
        canvas = tk.Canvas(list_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Get distinct values for the column
        if hasattr(self, 'original_df') and column in self.original_df.columns:
            # Use original data to get all possible values
            all_values = self.original_df[column].dropna().astype(str).unique().tolist()
        elif column in self.df.columns:
            # Fallback to current data
            all_values = self.df[column].dropna().astype(str).unique().tolist()
        else:
            all_values = []
        
        # Sort values naturally
        def natural_sort_key(val):
            try:
                return (0, float(val))  # Numbers first
            except (ValueError, TypeError):
                return (1, str(val).lower())  # Then text
        
        all_values = sorted(all_values, key=natural_sort_key)
        self.filter_values = all_values
        
        # Store checkbox variables
        self.filter_checkboxes = {}
        self.current_filter_column = column
        
        # Create checkboxes for each value
        for value in all_values:
            var = tk.BooleanVar(value=True)
            self.filter_checkboxes[value] = var
            
            cb = tk.Checkbutton(scrollable_frame, text=f" {value}", 
                              variable=var, bg='white', anchor='w',
                              font=('Arial', 9))
            cb.pack(fill='x', anchor='w', pady=1)
        
        # Pack canvas and scrollbar properly
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Search functionality
        def update_search(*args):
            search_text = self.search_var.get().lower()
            for widget in scrollable_frame.winfo_children():
                if isinstance(widget, tk.Checkbutton):
                    text = widget.cget('text').lower()
                    if search_text in text:
                        widget.pack(fill='x', anchor='w', pady=1)
                    else:
                        widget.pack_forget()
            # Update scrollregion after search
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.search_var.trace('w', update_search)
        
        # BUTTONS SECTION - Always visible at the bottom of main_frame
        separator = tk.Frame(main_frame, height=2, bg='#CCCCCC')
        separator.pack(fill='x', pady=(10, 5))
        
        # Button frame - FIXED at bottom
        btn_frame = tk.Frame(main_frame, bg='#F0F0F0', relief='raised', bd=2, height=80)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)  # Prevent resizing
        
        # Button container for centered layout
        btn_container = tk.Frame(btn_frame, bg='#F0F0F0')
        btn_container.pack(expand=True, pady=15)
        
        # Buttons with improved styling and clear visibility
        apply_btn = tk.Button(btn_container, text="✅ Apply Filter", 
                             command=self.apply_filter,
                             bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                             width=15, height=2, relief='raised', bd=3,
                             activebackground='#45A049')
        apply_btn.pack(side='left', padx=8)
        
        clear_btn = tk.Button(btn_container, text="🔄 Clear Filter",
                             command=lambda: self.clear_filter(column),
                             bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                             width=15, height=2, relief='raised', bd=3,
                             activebackground='#F57C00')
        clear_btn.pack(side='left', padx=8)
        
        # cancel_btn = tk.Button(btn_container, text="❌ Cancel",
        #                       command=self.filter_window.destroy,
        #                       bg='#F44336', fg='white', font=('Arial', 10, 'bold'),
        #                       width=12, height=2, relief='raised', bd=3,
        #                       activebackground='#D32F2F')
        # cancel_btn.pack(side='left', padx=8)
        
        # Add mouse wheel scrolling support
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mousewheel to canvas and window
        canvas.bind("<MouseWheel>", on_mousewheel)
        self.filter_window.bind("<MouseWheel>", on_mousewheel)
        
        # Focus on search entry for immediate typing
        search_entry.focus()
    
    def toggle_all_checkboxes(self):
        """Toggle all filter checkboxes based on Select All state"""
        if hasattr(self, 'filter_checkboxes'):
            select_all = self.select_all_var.get()
            for var in self.filter_checkboxes.values():
                var.set(select_all)
    
    def apply_sort(self, column, ascending):
        """Apply sorting to the column"""
        try:
            if column in self.df.columns:
                # Convert to appropriate type for sorting
                if self.df[column].dtype == 'object':
                    # Try to convert to numeric if possible, otherwise sort as string
                    try:
                        sorted_df = self.df.iloc[self.df[column].astype(float).argsort()]
                        if not ascending:
                            sorted_df = sorted_df.iloc[::-1]
                    except:
                        sorted_df = self.df.sort_values(by=column, ascending=ascending, 
                                                       key=lambda x: x.astype(str).str.lower())
                else:
                    sorted_df = self.df.sort_values(by=column, ascending=ascending)
                
                self.df = sorted_df.reset_index(drop=True)
                # Update ID column after sorting
                if 'ID' in self.df.columns:
                    self.df['ID'] = range(1, len(self.df) + 1)
                
                self.render_table()
                self.update_sum_labels()
                self.update_role_summary()
                
                # Close filter window
                if hasattr(self, 'filter_window') and self.filter_window:
                    self.filter_window.destroy()
                    
                print(f"Sorted by {column}, ascending={ascending}")
        except Exception as e:
            print(f"Error sorting: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_filter(self):
        """Apply the selected filter values"""
        try:
            if not hasattr(self, 'filter_checkboxes') or not hasattr(self, 'current_filter_column'):
                return
            
            column = self.current_filter_column
            
            # Get selected values
            selected_values = []
            for value, var in self.filter_checkboxes.items():
                if var.get():
                    selected_values.append(value)
            
            if not selected_values:
                # If nothing selected, show empty dataframe
                self.df = pd.DataFrame(columns=self.df.columns)
            else:
                # Filter the original data
                if hasattr(self, 'original_df') and column in self.original_df.columns:
                    # Start with original data (without Select and ID columns)
                    filtered_df = self.original_df[self.original_df[column].astype(str).isin(selected_values)].copy()
                    
                    # Add Select and ID columns
                    if not filtered_df.empty:
                        filtered_df.insert(0, 'Select', False)
                        filtered_df.insert(1, 'ID', range(1, len(filtered_df) + 1))
                    else:
                        # Create empty dataframe with all columns
                        filtered_df = pd.DataFrame(columns=self.df.columns)
                    
                    self.df = filtered_df
                else:
                    # Fallback to current dataframe
                    self.df = self.df[self.df[column].astype(str).isin(selected_values)].copy()
                    if 'ID' in self.df.columns and not self.df.empty:
                        self.df['ID'] = range(1, len(self.df) + 1)
            
            # Clear selections since row indices have changed
            self.selected_rows.clear()
            
            # Update display
            self.render_table()
            self.update_sum_labels()
            self.update_role_summary()
            
            # Close filter window
            if hasattr(self, 'filter_window') and self.filter_window:
                self.filter_window.destroy()
                
            print(f"Applied filter to {column}: {len(selected_values)} values selected")
            
        except Exception as e:
            print(f"Error applying filter: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_filter(self, column):
        """Clear filter and restore original data"""
        try:
            # Restore original data
            if hasattr(self, 'original_df'):
                # Recreate the full dataframe with Select and ID columns
                display_cols_without_select_id = [col for col in self.df.columns if col not in ['Select', 'ID']]
                available_cols = [col for col in display_cols_without_select_id if col in self.original_df.columns]
                
                restored_df = self.original_df[available_cols].copy()
                
                # Add Select and ID columns
                if not restored_df.empty:
                    restored_df.insert(0, 'Select', False)
                    restored_df.insert(1, 'ID', range(1, len(restored_df) + 1))
                else:
                    restored_df = pd.DataFrame(columns=self.df.columns)
                
                self.df = restored_df
            
            # Clear selections
            self.selected_rows.clear()
            
            # Update display
            self.render_table()
            self.update_sum_labels()
            self.update_role_summary()
            
            # Close filter window
            if hasattr(self, 'filter_window') and self.filter_window:
                self.filter_window.destroy()
                
            print(f"Cleared filter for {column}")
            
        except Exception as e:
            print(f"Error clearing filter: {e}")
            import traceback
            traceback.print_exc()

    def create_summation_row(self):
        """Create a fixed summary row below the table in dedicated frame"""
        # Clear any existing widgets in the totals frame
        for widget in self.totals_display_frame.winfo_children():
            widget.destroy()
        
        # Create a HUGE IMPOSSIBLE TO MISS title
        title_label = tk.Label(self.totals_display_frame, 
                              text="� ATTENTION: TOTAL HOURS SUMMARY 🚨", 
                              font=('Arial', 20, 'bold'),
                              bg='#FF0000',
                              fg='white')
        title_label.pack(pady=(15, 20))
        
        # Create styled containers for totals with MAXIMUM visibility
        totals_container = tk.Frame(self.totals_display_frame, bg='#FF0000')
        totals_container.pack(expand=True, fill='both', padx=30)
        
        # Internal total box - GIGANTIC and impossible to miss
        internal_frame = tk.Frame(totals_container, bg='#00FF00', relief='raised', bd=10, height=80)
        internal_frame.pack(side='left', padx=30, pady=15, expand=True, fill='both')
        
        internal_label = tk.Label(internal_frame, 
                                text="💼 TOTAL INTERNAL HOURS:", 
                                font=('Arial', 16, 'bold'),
                                bg='#00FF00',
                                fg='black')
        internal_label.pack(side='left', padx=25, pady=20)
        
        self.total_label_internal = tk.Label(internal_frame,
                                           text="0.00",
                                           font=('Arial', 24, 'bold'),
                                           bg='#00FF00',
                                           fg='red')
        self.total_label_internal.pack(side='left', padx=(15, 25), pady=20)
        
        # External total box - GIGANTIC and impossible to miss
        external_frame = tk.Frame(totals_container, bg='#0000FF', relief='raised', bd=10, height=80)
        external_frame.pack(side='left', padx=30, pady=15, expand=True, fill='both')
        
        external_label = tk.Label(external_frame,
                                text="🏢 TOTAL EXTERNAL HOURS:",
                                font=('Arial', 16, 'bold'),
                                bg='#0000FF',
                                fg='white')
        external_label.pack(side='left', padx=25, pady=20)
        
        self.total_label_external = tk.Label(external_frame,
                                           text="0.00", 
                                           font=('Arial', 24, 'bold'),
                                           bg='#0000FF',
                                           fg='yellow')
        self.total_label_external.pack(side='left', padx=(15, 25), pady=20)

    def on_checkbox_click(self, event):
        """Handle checkbox column clicks for row selection"""
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)
        
        if not item or not column.startswith('#'):
            return
            
        col_idx = int(column.replace('#', '')) - 1
        col_name = self.df.columns[col_idx]
        
        if col_name == 'Select':
            row_idx = int(item)
            values = list(self.tree.item(item)['values'])
            
            # Toggle selection
            if row_idx in self.selected_rows:
                self.selected_rows.remove(row_idx)
                values[0] = '☐'
            else:
                self.selected_rows.add(row_idx)
                values[0] = '☑'
                
            # Update tree display without full refresh
            self.tree.item(item, values=values)
            print(f"Selected rows: {len(self.selected_rows)}")

    def apply_dropdown_filters(self, event=None):
        # Start with original data without Select and ID columns
        df_original_clean = self.original_df.copy()
        
        # Remove Select and ID columns if they exist in original_df
        if 'Select' in df_original_clean.columns:
            df_original_clean = df_original_clean.drop('Select', axis=1)
        if 'ID' in df_original_clean.columns:
            df_original_clean = df_original_clean.drop('ID', axis=1)
        
        df_filtered = df_original_clean.copy()
        
        # Apply filters
        active_filters = {}
        for col, var in self.filter_vars.items():
            val = var.get()
            if val != "Todos" and col not in ["Select", "ID"] and col in df_filtered.columns:
                df_filtered = df_filtered[df_filtered[col].astype(str) == val]
                active_filters[col] = val
        
        print(f"Applied filters: {active_filters}")  # Debug
        print(f"Filtered data shape: {df_filtered.shape}")  # Debug
        
        # Re-add Select and ID columns
        if not df_filtered.empty:
            df_filtered.insert(0, 'Select', False)
            df_filtered.insert(1, 'ID', range(1, len(df_filtered) + 1))
        else:
            df_filtered = pd.DataFrame(columns=self.display_columns)
            
        self.df = df_filtered
        self.render_table()
        self.update_sum_labels()  # Update totals after filtering
        self.update_role_summary()  # Update role summary with filtered data

    def reset_filters(self):
        """Reset all filters and restore original project data"""
        # Clear all filter selections
        for col, var in self.filter_vars.items():
            var.set("Todos")
        
        # Clear row selections
        self.selected_rows.clear()
        
        # Reload the full project data from database
        if self.current_project:
            self.on_project_selected(None)  # This will reload all data for the current project
        else:
            # If no project selected, just clear everything
            self.df = pd.DataFrame(columns=self.display_columns)
            self.original_df = pd.DataFrame(columns=[col for col in self.display_columns if col not in ['Select', 'ID']])
            self.render_table()
            self.update_sum_labels()

    def update_filter_dropdowns(self):
        """Update filter dropdown values based on current data"""
        for idx, (col, var) in enumerate(self.filter_vars.items()):
            if col not in ["Select", "ID"] and idx < len(self.header_labels):
                for lbl, cmb in self.header_labels:
                    if hasattr(cmb, 'get'):
                        try:
                            # Update dropdown values with current data
                            if col in self.df.columns:
                                values = sorted(self.df[col].dropna().astype(str).unique())
                            else:
                                values = []
                            values = ["Todos"] + values
                            cmb['values'] = values
                            if var.get() not in values:
                                var.set("Todos")
                        except:
                            pass

    def sort_column(self, column, ascending=True):
        """Sort the dataframe by the specified column"""
        if column in self.df.columns and column not in ["Select", "ID"]:
            try:
                # Try to sort numerically first, fallback to string sort
                if column in ["Estimated internal", "Estimated external"]:
                    # For numeric columns, convert to numeric for proper sorting
                    self.df[column] = pd.to_numeric(self.df[column], errors='coerce')
                    self.df = self.df.sort_values(by=column, ascending=ascending, na_position='last')
                else:
                    # For text columns, sort as strings
                    self.df = self.df.sort_values(by=column, ascending=ascending, na_position='last')
                
                # Update ID counter after sorting
                if 'ID' in self.df.columns:
                    self.df['ID'] = range(1, len(self.df) + 1)
                
                self.render_table()
                self.update_sum_labels()
            except Exception as e:
                print(f"Error sorting column {column}: {e}")

    def edit_cell(self, event):
        """Handle cell editing on double-click"""
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)
        
        if not item or not column or not column.startswith('#'):
            return
            
        # Get column name from index
        col_idx = int(column.replace('#', '')) - 1
        col_name = self.df.columns[col_idx]
        
        # Don't edit checkbox column
        if col_name == 'Select':
            return
            
        # Create and position the edit entry
        x, y, width, height = self.tree.bbox(item, column)
        entry = tk.Entry(self.tree, width=20)
        entry.insert(0, self.tree.item(item)['values'][col_idx])
        entry.select_range(0, tk.END)
        
        def on_edit_done(event=None):
            """Complete the edit and update data"""
            new_value = entry.get()
            row_idx = int(item)  # Get numerical index
            
            # Update DataFrame
            self.df.at[row_idx, col_name] = new_value
            
            # Update tree
            values = list(self.tree.item(item)['values'])
            values[col_idx] = new_value
            self.tree.item(item, values=values)
            
            entry.destroy()
            
            # Update summaries if needed
            if col_name in ["Estimated internal", "Estimated external"]:
                self.update_sum_labels()
                self.update_role_summary()
                
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        
        # Bind events
        entry.bind("<Return>", on_edit_done)
        entry.bind("<Escape>", lambda e: entry.destroy())
        entry.bind("<FocusOut>", on_edit_done)

    def add_row(self):
        required_fields = ["Stick-Built", "Module", "Department", "Activities"]
        missing_fields = [col for col in required_fields if not self.entries[col].get().strip()]
        if not self.current_project:
            messagebox.showerror("Error", "Please select a project first.")
            return
        if missing_fields:
            messagebox.showerror("Error", f"Por favor llena los campos requeridos:\n{', '.join(missing_fields)}")
            return
        # Prepare data for DB insert
        import sqlalchemy
        db_path = os.path.join(os.path.dirname(__file__), 'Workload.db')
        logging.debug(f"Using DB file for insert: {os.path.abspath(db_path)}")
        engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        # Get project_id
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text('SELECT id FROM project WHERE name = :name'), {'name': self.current_project}).fetchone()
            project_id = result[0] if result else None
        if not project_id:
            messagebox.showerror("Error", "Project not found in database.")
            return
        # Build insert dict
        data = { 'project_id': project_id }
        # Map form fields to DB columns (assume DB columns match form fields, adjust if needed)
        # You may need to adjust these mappings if your DB uses different column names
        # Mapping from form field to DB column
        field_to_db = {
            "Stick-Built": "stick_built_id",
            "Module": "module_id",
            "Activities": "activities_id",
            "Title": "title_id",
            "Technical Unit": "technical_unit_id",
            "Assigned to": "employee_id",
            "Progress": "progress_id",
            "Professional Role": "professional_unit_id",
            "Department": "department",
            "Estimated internal": "estimated_internal_hours",
            "Estimated external": "estimated_external_hours",
            "Start date": "start_date",
            "Due date": "due_date",
            "Notes": "notes"
        }
        for col in self.entries:
            val = self.entries[col].get()
            db_col = field_to_db.get(col)
            if db_col is None:
                continue  # Skip fields not mapped
            # Foreign key fields (those ending with _id)
            if db_col.endswith('_id'):
                options = self.foreign_key_options.get(col, [])
                match = next((o for o in options if o['name'] == val), None)
                data[db_col] = match['id'] if match else None
            else:
                data[db_col] = val
        # Insert into DB
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f':{k}' for k in data.keys()])
            insert_sql = f"INSERT INTO service ({columns}) VALUES ({placeholders})"
            with engine.begin() as conn:
                result = conn.execute(sqlalchemy.text(insert_sql), data)
                logging.info(f"Insert result rowcount: {result.rowcount}, data: {data}")
            messagebox.showinfo("Success", "Service added successfully.")
            
            # Store current filter state BEFORE reloading data
            current_filters = {col: var.get() for col, var in self.filter_vars.items() if hasattr(var, 'get')}
            print(f"Saving current filters: {current_filters}")  # Debug
            
            # Clear form fields after successful insert
            for col, entry in self.entries.items():
                if hasattr(entry, 'set') and col != "Department":  # Keep Department as "FABSI"
                    entry.set("")
                elif hasattr(entry, 'delete') and col != "Department":
                    entry.delete(0, 'end')
                    if col == "Department":
                        entry.insert(0, "FABSI")
            
            # Reload ALL project data first (this updates self.original_df)
            self.on_project_selected(None)
            
            # Restore filters and apply them
            for col, value in current_filters.items():
                if col in self.filter_vars and value != "Todos":
                    self.filter_vars[col].set(value)
                    print(f"Restored filter {col}: {value}")  # Debug
            
            # Apply the filters to show only matching records
            if any(v != "Todos" for v in current_filters.values()):
                self.apply_dropdown_filters()
                print("Applied filters after adding record")  # Debug
            else:
                print("No active filters to restore")  # Debug
        except Exception as e:
            import traceback
            logging.error(f"Failed to add service: {e}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to add service: {e}")

    def load_services(self):
        # Not used anymore, replaced by on_project_selected
        pass

    def delete_selected(self):
        if not self.selected_rows:
            messagebox.showwarning("Warning", "Please select at least one activity to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Do you want to delete {len(self.selected_rows)} selected activities?"):
            # Get the actual database IDs from the Document Number column
            ids_to_delete = []
            for row_idx in self.selected_rows:
                if row_idx < len(self.df) and 'Document Number' in self.df.columns:
                    db_id = self.df.iloc[row_idx]['Document Number']
                    if pd.notnull(db_id):  # Only add valid IDs
                        ids_to_delete.append(int(db_id))
            
            # Delete from database
            if ids_to_delete:
                try:
                    import sqlalchemy
                    db_path = os.path.join(os.path.dirname(__file__), 'Workload.db')
                    engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
                    
                    deleted_count = 0
                    with engine.begin() as conn:
                        for db_id in ids_to_delete:
                            result = conn.execute(sqlalchemy.text("DELETE FROM service WHERE id = :id"), {'id': db_id})
                            if result.rowcount > 0:
                                deleted_count += 1
                            logging.info(f"Deleted service ID {db_id}, rows affected: {result.rowcount}")
                    
                    # Clear selection
                    self.selected_rows.clear()
                    
                    # Store current filter state
                    current_filters = {col: var.get() for col, var in self.filter_vars.items() if hasattr(var, 'get')}
                    print(f"Saving current filters before delete: {current_filters}")  # Debug
                    
                    # Reload data
                    self.on_project_selected(None)
                    
                    # Restore filters
                    for col, value in current_filters.items():
                        if col in self.filter_vars and value != "Todos":
                            self.filter_vars[col].set(value)
                    
                    # Apply filters if any were active
                    if any(v != "Todos" for v in current_filters.values()):
                        self.apply_dropdown_filters()
                        print("Applied filters after delete")  # Debug
                    
                    messagebox.showinfo("Success", f"Deleted {deleted_count} activities successfully from database.")
                    logging.info(f"Successfully deleted {deleted_count} services from database")
                except Exception as e:
                    logging.error(f"Failed to delete services: {e}")
                    messagebox.showerror("Error", f"Failed to delete activities: {e}")
            else:
                messagebox.showwarning("Warning", "No valid activities found to delete.")

    def save_to_excel(self):
        if self.df.empty:
            messagebox.showerror("Error", "No selected data to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            self.df.to_excel(writer, index=False, sheet_name='List of Service')
            ws = writer.sheets['List of Service']
            border = Border(left=Side(style='thin'), right=Side(style='thin'),
                            top=Side(style='thin'), bottom=Side(style='thin'))
            header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
            for cell in ws[1]:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                cell.fill = header_fill
                cell.border = border
                cell.font = Font(bold=True)
            for col in ws.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=10)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = min(max_length + 2, 25)
                for cell in col:
                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                    cell.border = border
            ws.auto_filter.ref = ws.dimensions
            ws.row_dimensions[1].height = 48
        subprocess.Popen(['start', '', path], shell=True)
        messagebox.showinfo("Guardado", f"Archivo guardado:\n{path}")

    def save_to_pdf(self):
        """Export table data to a well-formatted PDF file"""
        if self.df.empty:
            messagebox.showerror("Error", "No selected data to save.")
            return

        try:
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.pagesizes import A3, landscape
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Ask for save location
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )
            if not path:
                return
                
            # Configure document
            doc = SimpleDocTemplate(
                path,
                pagesize=landscape(A3),  # Using A3 for more space
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            # Prepare data
            # Filter out unwanted columns and rename them
            export_columns = [col for col in self.df.columns if col not in ['Select', 'Document Number']]
            df_export = self.df[export_columns].copy()
            
            # Convert DataFrame to list of lists for the table
            header = [col for col in df_export.columns]  # Use column names directly
            data = [header]
            
            # Convert DataFrame values to strings and handle None/NaN
            for _, row in df_export.iterrows():
                row_data = []
                for value in row:
                    if pd.isna(value):
                        row_data.append("")
                    else:
                        row_data.append(str(value))
                data.append(row_data)
            
            # Calculate column widths based on content
            col_widths = []
            for idx in range(len(header)):
                max_width = max(
                    len(str(row[idx])) for row in data
                ) * 6  # 6 points per character
                col_widths.append(min(max_width, 150))  # Cap at 150 points for better fit
                
            # Create table
            table = Table(data, colWidths=col_widths, repeatRows=1)
            
            # Table style
            table_style = TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D9D9D9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Cell style
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                
                # Text alignment
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            # Alternate row colors
            for row in range(1, len(data)):
                if row % 2 == 0:
                    table_style.add('BACKGROUND', (0, row), (-1, row), colors.HexColor('#F8F8F8'))
                else:
                    table_style.add('BACKGROUND', (0, row), (-1, row), colors.white)
            
            table.setStyle(table_style)
            
            # Build document
            elements = []
            
            # Add title
            title = Paragraph(f"FABSI - List of Service: {self.current_project}", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))  # Add some space after title
            
            # Add table
            elements.append(table)
            
            # Generate PDF
            doc.build(elements)
            
            # Open the generated PDF
            subprocess.Popen(['start', '', path], shell=True)
            messagebox.showinfo("Success", f"PDF file saved successfully:\n{path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")
            logging.error(f"PDF creation error: {str(e)}")
            logging.error(traceback.format_exc())

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.resizable(True, True)
    app = ExcelActivityApp(root)
    root.mainloop()

