import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Database setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workload.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class StickBuilt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Activities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class TechnicalUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class ProfessionalUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stick_built_id = db.Column(db.Integer, db.ForeignKey('stick_built.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    activities_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'))
    technical_unit_id = db.Column(db.Integer, db.ForeignKey('technical_unit.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    progress_id = db.Column(db.Integer, db.ForeignKey('progress.id'))
    professional_unit_id = db.Column(db.Integer, db.ForeignKey('professional_unit.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    department = db.Column(db.String)
    estimated_internal_hours = db.Column(db.Integer)
    estimated_external_hours = db.Column(db.Integer)
    start_date = db.Column(db.String)
    due_date = db.Column(db.String)
    notes = db.Column(db.String)

# --- Seeding Functions ---
def seed_table(model, values):
    for v in values:
        if v and not model.query.filter_by(name=str(v)).first():
            db.session.add(model(name=str(v)))
    db.session.commit()

def seed_from_excel():
    excel_path = 'FABSI_List of Service HO_Master_R1.xlsx'
    if not os.path.exists(excel_path):
        print(f"Excel file not found: {excel_path}")
        return
    df_template = pd.read_excel(excel_path, sheet_name='TemplateList')
    # Map each table to its correct source column
    table_sources = {
        'StickBuilt': ('Stick built', StickBuilt),  # fallback to Module if not present
        'Module': ('Module', Module),
        'Activities': ('Activities', Activities),
        'Title': ('Title', Title),
        'TechnicalUnit': ('Technical Unit', TechnicalUnit),  # fixed column name
        'Employee': ('Assigned to', Employee),
        'Progress': ('Progress', Progress),
        'ProfessionalUnit': ('Professional Role', ProfessionalUnit),
        'Project': ('Project', Project)
    }
    # StickBuilt: use Stick built if present, else use Module
    stick_built_col = 'Stick built' if 'Stick built' in df_template.columns else 'Module'
    if stick_built_col in df_template.columns:
        values = df_template[stick_built_col].dropna().unique()
        seed_table(StickBuilt, values)
    # Other tables
    for key, (col, model) in table_sources.items():
        if key == 'StickBuilt':
            continue  # already seeded above
        if col in df_template.columns:
            values = df_template[col].dropna().unique()
            seed_table(model, values)
    print('Seeding complete.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_from_excel()
        print('Database created and seeded.')
