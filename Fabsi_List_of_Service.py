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
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

class ExcelActivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FABSI - List of Service")
        self.root.resizable(True, True)

        self.display_columns = [
            "Stick-Built", "Module", "Document Number", "Activities", "Title", "Department",
            "Technical Unit", "Assigned to", "Progress", "Estimated hours (internal)",
            "Estimated hours (external)", "Start date", "Due date", "Notes", "Professional Role"
        ]
        self.df = pd.DataFrame(columns=self.display_columns)
        self.original_df = self.df.copy()

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

        # Add button to open modal for professional role summary
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=15, pady=(0, 5))
        tk.Button(button_frame, text="Professional Role Summary", command=self.open_role_summary_modal, bg="#1976D2", fg="white").pack(side='left', padx=(0, 10))
        tk.Button(button_frame, text="Agregar Actividad", command=self.add_row, bg="#388E3C", fg="white").pack(side='right')
        tk.Button(button_frame, text="Open File", command=self.open_file, bg="#0288D1", fg="white").pack(side='right', padx=(0, 10))

        # Remove the always-visible small table from the main UI
        # self.role_summary_frame = tk.Frame(summary_right, bd=1, relief='solid')
        # self.role_summary_frame.pack(padx=5, pady=5, anchor='ne')
        # self.role_summary_tree = ...

        # Add a visual separator between form and table
        separator = tk.Frame(self.root, height=2, bd=1, relief='sunken', bg="#BDBDBD")
        separator.pack(fill='x', padx=10, pady=5)

        # Create the main table frame (always present)
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill='both', expand=True, padx=15, pady=(5, 10))

        # --- SUMAS, alineadas a columnas ---
        self.sum_frame = tk.Frame(self.root, height=35)
        self.sum_frame.pack(fill='x', padx=20, pady=(0,5))
        # Ajusta las posiciones para alinear exactamente
        self.total_label_internal = tk.Label(self.sum_frame, text="", anchor='e', font=('Arial', 8, 'bold'))
        self.total_label_internal.place(x=1045, y=2, width=60)
        self.total_label_external = tk.Label(self.sum_frame, text="", anchor='e', font=('Arial', 8, 'bold'))
        self.total_label_external.place(x=1115, y=2, width=60)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10, fill='x')
        tk.Button(bottom_frame, text="Reset Filtros", command=self.reset_filters).pack(side='left', padx=10)
        tk.Button(bottom_frame, text="Eliminar seleccionadas", command=self.delete_selected).pack(side='left', padx=10)
        tk.Button(bottom_frame, text="Save & Print in Excel", command=self.save_to_excel).pack(side='right', padx=10)
        tk.Button(bottom_frame, text="Save & Print in PDF", command=self.save_to_pdf).pack(side='right', padx=10)

        self.render_table()
        self.build_entry_fields()
        self.update_sum_labels()
        self.update_role_summary()
    def open_role_summary_modal(self):
        if hasattr(self, 'role_summary_modal') and self.role_summary_modal and tk.Toplevel.winfo_exists(self.role_summary_modal):
            self.role_summary_modal.lift()
            return
        self.role_summary_modal = tk.Toplevel(self.root)
        self.role_summary_modal.title("Professional Role & Manhours Summary")
        self.role_summary_modal.geometry("350x300")
        self.role_summary_modal.transient(self.root)
        self.role_summary_modal.grab_set()
        frame = tk.Frame(self.role_summary_modal, bd=1, relief='solid')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        tree = ttk.Treeview(
            frame,
            columns=["Professional Role", "Manhours"],
            show='headings', height=10
        )
        tree.heading("Professional Role", text="Professional Role")
        tree.heading("Manhours", text="Manhours")
        tree.column("Professional Role", width=180, anchor='w')
        tree.column("Manhours", width=90, anchor='e')
        tree.pack(fill='both', expand=True)
        # Fill the tree with summary data
        if hasattr(self, 'role_summary_data') and not self.role_summary_data.empty:
            for _, row in self.role_summary_data.iterrows():
                manhours = f"{row['Estimated hours (internal)']:,.0f}" if pd.notnull(row["Estimated hours (internal)"]) else ""
                tree.insert("", "end", values=(row["Professional Role"], manhours))
        close_btn = tk.Button(self.role_summary_modal, text="Close", command=self.role_summary_modal.destroy)
        close_btn.pack(pady=5)

        # (moved to setup_ui)

    def auto_update_totals(self):
        self.update_sum_labels()
        self.update_role_summary()
        self.root.after(400, self.auto_update_totals)

    def update_sum_labels(self):
        if not self.total_label_internal or not self.total_label_external:
            return
        try:
            df = self.df
            col_internal = "Estimated hours (internal)"
            col_external = "Estimated hours (external)"
            total_internal = pd.to_numeric(df[col_internal], errors='coerce').sum() if col_internal in df.columns else 0
            total_external = pd.to_numeric(df[col_external], errors='coerce').sum() if col_external in df.columns else 0
        except Exception:
            total_internal = 0
            total_external = 0
        # Solo los resultados, sin etiquetas
        self.total_label_internal.config(text=f"{total_internal:,.2f}")
        self.total_label_external.config(text=f"{total_external:,.2f}")

    def update_role_summary(self):
        # Only update if the modal/tree exists
        if not hasattr(self, 'role_summary_tree') or self.role_summary_tree is None:
            # Still update the summary data for the modal
            if "Professional Role" in self.df.columns and "Estimated hours (internal)" in self.df.columns:
                summary = (
                    self.df.groupby("Professional Role")["Estimated hours (internal)"]
                    .apply(lambda x: pd.to_numeric(x, errors='coerce').sum())
                    .reset_index()
                )
                summary = summary[summary["Professional Role"].notnull() & (summary["Professional Role"] != "")]
                summary = summary[summary["Estimated hours (internal)"] > 0]
                self.role_summary_data = summary
            return
        for row in self.role_summary_tree.get_children():
            self.role_summary_tree.delete(row)
        if "Professional Role" in self.df.columns and "Estimated hours (internal)" in self.df.columns:
            summary = (
                self.df.groupby("Professional Role")["Estimated hours (internal)"]
                .apply(lambda x: pd.to_numeric(x, errors='coerce').sum())
                .reset_index()
            )
            summary = summary[summary["Professional Role"].notnull() & (summary["Professional Role"] != "")]
            summary = summary[summary["Estimated hours (internal)"] > 0]
            self.role_summary_data = summary  # Guarda el DataFrame actual para editar
            for _, row in summary.iterrows():
                manhours = f"{row['Estimated hours (internal)']:,.0f}" if pd.notnull(row["Estimated hours (internal)"]) else ""
                self.role_summary_tree.insert("", "end", values=(row["Professional Role"], manhours))

    def edit_role_summary_cell(self, event):
        # Permite editar la tabla resumen haciendo doble clic
        item = self.role_summary_tree.identify_row(event.y)
        column = self.role_summary_tree.identify_column(event.x)
        if not item or not column:
            return
        col_idx = int(column.replace('#', '')) - 1
        col_name = ["Professional Role", "Estimated hours (internal)"][col_idx]
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
                    "Estimated hours (internal)": "estimated_internal_hours",
                    "Estimated hours (external)": "estimated_external_hours",
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
                    s.estimated_internal_hours AS "Estimated hours (internal)",
                    s.estimated_external_hours AS "Estimated hours (external)",
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
                # Only keep display columns
                if not df.empty:
                    self.df = df[self.display_columns]
                else:
                    self.df = pd.DataFrame(columns=self.display_columns)
                self.original_df = self.df.copy()
                self.render_table()
            else:
                self.df = pd.DataFrame(columns=self.display_columns)
                self.original_df = self.df.copy()
                self.render_table()
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
            ["Department", "Estimated hours (internal)", "Estimated hours (external)", "Start date"],
            ["Due date", "Notes"]
        ]
        label_opts = {'anchor': 'w', 'bg': '#F7F7F7', 'font': ('Arial', 9)}
        entry_opts = {'font': ('Arial', 10)}
        for row_idx, row in enumerate(fields):
            for col_idx, col in enumerate(row):
                lbl = tk.Label(self.entry_frame, text=col, **label_opts)
                lbl.grid(row=row_idx*2, column=col_idx, sticky='w', padx=10, pady=(10,0))
                if col in self.foreign_key_options:
                    options = self.foreign_key_options[col]
                    widget = ttk.Combobox(self.entry_frame, width=24, state="readonly", font=('Arial', 11))
                    widget['values'] = [o['name'] for o in options]
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, sticky='we', padx=10, pady=(0,10))
                elif col in ["Department", "Estimated hours (internal)", "Estimated hours (external)", "Start date", "Due date"]:
                    widget = tk.Entry(self.entry_frame, width=26, **entry_opts)
                    if col == "Department":
                        widget.insert(0, "FABSI")
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, sticky='we', padx=10, pady=(0,10))
                elif col == "Notes":
                    widget = tk.Entry(self.entry_frame, width=50, **entry_opts)
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, columnspan=2, sticky='we', padx=10, pady=(0,10))
                else:
                    widget = tk.Entry(self.entry_frame, width=26, **entry_opts)
                    self.entries[col] = widget
                    widget.grid(row=row_idx*2+1, column=col_idx, sticky='we', padx=10, pady=(0,10))
        # Make columns expand equally
        for i in range(4):
            self.entry_frame.grid_columnconfigure(i, weight=1)

    def update_activities_filter(self, event):
        text = self.entries["Activities"].get()
        all_activities = self.df["Activities"].dropna().unique().tolist() if "Activities" in self.df.columns else []
        if text:
            matches = [act for act in all_activities if text.lower() in act.lower()]
            self.entries["Activities"]['values'] = matches if matches else all_activities
        else:
            self.entries["Activities"]['values'] = all_activities

    def render_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.create_custom_header_with_filters()
        self.tree = ttk.Treeview(
            self.table_frame,
            columns=list(self.df.columns),
            show='',  # Oculta headings nativos y árbol
            selectmode='extended'
        )
        self.tree.bind("<Double-1>", self.edit_cell)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=23,
            fieldbackground="white",
            bordercolor="#BFBFBF",
            borderwidth=1
        )
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe', 'border': '1'})
        ])
        column_widths = {
            "Stick-Built": 65,
            "Module": 58,
            "Document Number": 70,
            "Activities": 370,
            "Title": 75,
            "Department": 80,
            "Technical Unit": 150,
            "Assigned to": 120,
            "Progress": 75,
            "Estimated hours (internal)": 68,
            "Estimated hours (external)": 68,
            "Start date": 70,
            "Due date": 70,
            "Notes": 230,
            "Professional Role": 250
        }
        for col in self.df.columns:
            anchor = 'w' if col in ["Activities", "Technical Unit", "Assigned to", "Professional Role"] else 'c'
            self.tree.column(col, width=column_widths.get(col, 120), anchor=anchor, stretch=False)
        for i, row in self.df.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end', iid=str(i), values=list(row), tags=(tag,))
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#F7F7F7')
        self.tree.pack(fill='both', expand=True)

    def create_custom_header_with_filters(self):
        for widget in self.table_frame.winfo_children():
            if isinstance(widget, tk.Frame) and getattr(widget, 'is_custom_header', False):
                widget.destroy()
        header_map = {
            "Document Number": "Document\nNumber",
            "Estimated hours (internal)": "Estimated\nhours\n(internal)",
            "Estimated hours (external)": "Estimated\nhours\n(external)",
            "Start date": "Start\ndate",
            "Due date": "Due\ndate"
        }
        column_widths = {
            "Stick-Built": 65,
            "Module": 58,
            "Document Number": 70,
            "Activities": 370,
            "Title": 75,
            "Department": 80,
            "Technical Unit": 150,
            "Assigned to": 120,
            "Progress": 75,
            "Estimated hours (internal)": 68,
            "Estimated hours (external)": 68,
            "Start date": 70,
            "Due date": 70,
            "Notes": 230,
            "Professional Role": 250
        }
        header_height = 52
        header_frame = tk.Frame(self.table_frame, height=header_height, bg="#D9D9D9")
        header_frame.pack(fill='x')
        header_frame.is_custom_header = True
        self.header_labels.clear()
        self.filter_vars.clear()
        x_offset = 0
        for idx, col in enumerate(self.df.columns):
            txt = header_map.get(col, col)
            width = column_widths.get(col, 100)
            cell_frame = tk.Frame(header_frame, width=width, height=header_height, bg="#D9D9D9", highlightthickness=0, bd=0)
            cell_frame.place(x=x_offset, y=0, width=width, height=header_height)
            lbl = tk.Label(
                cell_frame,
                text=txt,
                width=1,
                font=('Arial', 7, 'bold'),
                justify='center',
                anchor='center',
                bg='#D9D9D9',
                relief='groove',
                height=2,
                wraplength=width-4
            )
            lbl.pack(fill='x', padx=0, pady=0)
            filter_var = tk.StringVar()
            filter_var.set("Todos")
            self.filter_vars[col] = filter_var
            values = sorted(self.df[col].dropna().astype(str).unique())
            values = ["Todos"] + values
            cmb = ttk.Combobox(
                cell_frame, textvariable=filter_var, width=max(8, int(width/8)),
                values=values, state="readonly")
            cmb.pack(fill='x', padx=0, pady=0)
            cmb.bind("<<ComboboxSelected>>", self.apply_dropdown_filters)
            self.header_labels.append((lbl, cmb))
            x_offset += width

    def apply_dropdown_filters(self, event=None):
        df_filtered = self.original_df.copy()
        for col, var in self.filter_vars.items():
            val = var.get()
            if val != "Todos":
                df_filtered = df_filtered[df_filtered[col].astype(str) == val]
        self.df = df_filtered
        self.render_table()
        for idx, (col, var) in enumerate(self.filter_vars.items()):
            if idx < len(self.header_labels):
                lbl, cmb = self.header_labels[idx]
                cmb.set(var.get())

    def reset_filters(self):
        for col, var in self.filter_vars.items():
            var.set("Todos")
        self.df = self.original_df.copy()
        self.render_table()

    def edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
        col_idx = int(column.replace('#', '')) - 1
        col_name = self.df.columns[col_idx]
        x, y, width, height = self.tree.bbox(item, column)
        entry = tk.Entry(self.tree, width=20)
        entry.insert(0, self.tree.item(item, 'values')[col_idx])
        entry.place(x=x, y=y + 2, width=width, height=height - 4)
        entry.focus()
        def on_focus_out(event):
            new_value = entry.get()
            self.df.at[int(item), col_name] = new_value
            self.original_df = self.df.copy()
            self.render_table()
        entry.bind("<Return>", lambda e: on_focus_out(e))
        entry.bind("<FocusOut>", on_focus_out)

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
            "Estimated hours (internal)": "estimated_internal_hours",
            "Estimated hours (external)": "estimated_external_hours",
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
            self.on_project_selected(None)
        except Exception as e:
            import traceback
            logging.error(f"Failed to add service: {e}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to add service: {e}")

    def load_services(self):
        # Not used anymore, replaced by on_project_selected
        pass

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one activity to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Do you want to delete the selected activity?"):
            for item in selected_items:
                self.df.drop(int(item), inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            self.original_df = self.df.copy()
            self.render_table()

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
        if self.df.empty:
            messagebox.showerror("Error", "No selected data to save.")
            return
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        data = [list(self.df.columns)] + self.df.values.tolist()
        page_width = landscape(A4)[0]
        col_width = page_width / len(self.df.columns)
        col_widths = [col_width] * len(self.df.columns)
        table = Table(data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.50, colors.black),
        ])
        table.setStyle(style)
        doc = SimpleDocTemplate(path, pagesize=landscape(A4))
        doc.build([table])
        subprocess.Popen(['start', '', path], shell=True)
        messagebox.showinfo("Guardado", f"Archivo PDF guardado:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.resizable(True, True)
    app = ExcelActivityApp(root)
    root.mainloop()

