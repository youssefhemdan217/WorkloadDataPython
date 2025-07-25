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
        self.project_combobox = None
        self.current_project = ""
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

        self.setup_ui()
        self.auto_update_totals()

    def setup_ui(self):
        main_top = tk.Frame(self.root)
        main_top.pack(fill='x', padx=10, pady=2)

        self.entry_frame = tk.Frame(main_top, height=180)
        self.entry_frame.pack_propagate(False)
        self.entry_frame.pack(side='left', fill='x', expand=True)

        # Tabla resumen (derecha)
        summary_right = tk.Frame(main_top)
        summary_right.pack(side='right', padx=(0,10), pady=(10,0), anchor='ne')
        self.role_summary_frame = tk.Frame(summary_right, bd=1, relief='solid')
        self.role_summary_frame.pack(padx=5, pady=5, anchor='ne')
        self.role_summary_tree = ttk.Treeview(
            self.role_summary_frame,
            columns=["Professional Role", "Manhours"],
            show='headings', height=6
        )
        self.role_summary_tree.heading("Professional Role", text="Professional Role")
        self.role_summary_tree.heading("Manhours", text="Manhours")
        self.role_summary_tree.column("Professional Role", width=200, anchor='w')
        self.role_summary_tree.column("Manhours", width=90, anchor='e')
        self.role_summary_tree.pack()
        self.role_summary_tree.bind("<Double-1>", self.edit_role_summary_cell)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        style.configure("Treeview", font=('Arial', 9), rowheight=22)

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=15)
        tk.Button(button_frame, text="Agregar Actividad", command=self.add_row).pack(side='right')
        tk.Button(button_frame, text="Open File", command=self.open_file).pack(side='right', padx=(0, 10))

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

    def auto_update_totals(self):
        self.update_sum_labels()
        self.update_role_summary()
        self.root.after(400, self.auto_update_totals)

    def update_sum_labels(self):
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
            self.load_project_data("List of Service")

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
        if project_name:
            try:
                excel = pd.ExcelFile(self.file_path)
                if project_name == 'Master':
                    if 'List of Service' in excel.sheet_names:
                        self.load_project_data('List of Service')
                    else:
                        messagebox.showerror("Error", "No existe hoja 'List of Service' en el archivo de Excel.")
                elif project_name in excel.sheet_names:
                    self.load_project_data(project_name)
                else:
                    messagebox.showerror("Error", f"No existe hoja '{project_name}' en el archivo de Excel.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la hoja '{project_name}':\n{e}")

    def build_entry_fields(self):
        for widget in self.entry_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        project_list = []
        try:
            template_df = pd.read_excel(self.file_path, sheet_name='TemplateList')
            if 'Project' in template_df.columns:
                project_list = template_df['Project'].dropna().astype(str).unique().tolist()
            if 'Master' not in project_list:
                project_list.insert(0, 'Master')
            template_lists = {
                col: template_df[col].dropna().astype(str).unique().tolist()
                for col in template_df.columns
            }
        except Exception:
            template_lists = {}
            project_list = ['Master']
        field_layout = {
            "Project Template":             (30, 20, 20, 20),
            "Stick-Built":                  (210, 20, 15, 20),
            "Module":                       (390, 20, 15, 20),
            "Document Number":              (570, 20, 15, 25),
            "Title":                        (760, 20, 15, 23),
            "Department":                   (950, 20, 15, 25),
            "Technical Unit":               (30, 70, 15, 20),
            "Assigned to":                  (210, 70, 15, 20),
            "Progress":                     (390, 70, 15, 20),
            "Estimated hours (internal)":   (570, 70, 20, 25),
            "Estimated hours (external)":   (760, 70, 20, 25),
            "Start date":                   (950, 70, 15, 25),
            "Due date":                     (1150, 70, 15, 25),
            "Activities":                   (30, 120, 30, 80),
            "Notes":                        (570, 120, 30, 88)
        }
        for col, (x, y, label_width, entry_width) in field_layout.items():
            lbl = tk.Label(self.entry_frame, text=col, width=label_width, anchor='w')
            lbl.place(x=x, y=y)
            if col == "Project Template":
                self.project_combobox = ttk.Combobox(
                    self.entry_frame,
                    width=entry_width,
                    state="readonly",
                    values=project_list
                )
                self.project_combobox.place(x=x, y=y + 22)
                self.project_combobox.bind("<<ComboboxSelected>>", self.on_project_selected)
                self.entries[col] = self.project_combobox
            elif col == "Activities":
                all_activities = self.df["Activities"].dropna().unique().tolist() if "Activities" in self.df.columns else []
                widget = ttk.Combobox(self.entry_frame, width=entry_width, values=all_activities)
                widget.bind("<KeyRelease>", self.update_activities_filter)
                self.entries[col] = widget
                widget.place(x=x, y=y + 22)
            else:
                if col in template_lists:
                    widget = ttk.Combobox(self.entry_frame, values=template_lists[col], width=entry_width)
                    widget.set("")
                else:
                    widget = tk.Entry(self.entry_frame, width=entry_width)
                    if col == "Department":
                        widget.insert(0, "FABSI")
                widget.place(x=x, y=y + 22)
                self.entries[col] = widget

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
        required_fields = ["Stick-Built", "Module", "Document Number", "Department", "Activities"]
        missing_fields = [col for col in required_fields if not self.entries[col].get().strip()]
        if missing_fields:
            messagebox.showerror("Error", f"Por favor llena los campos requeridos:\n{', '.join(missing_fields)}")
            return
        new_data = {col: self.entries[col].get() for col in self.entries}
        self.df = pd.concat([self.df, pd.DataFrame([new_data])], ignore_index=True)
        self.original_df = self.df.copy()
        self.render_table()

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

