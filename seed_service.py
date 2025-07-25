import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workload.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models (same as db_setup.py) ---
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

def get_id_by_name(model, name):
    if not name or pd.isna(name):
        return None
    obj = model.query.filter_by(name=str(name)).first()
    return obj.id if obj else None

def seed_services_from_excel():
    excel_path = 'FABSI_List of Service HO_Master_R1.xlsx'
    if not os.path.exists(excel_path):
        print(f"Excel file not found: {excel_path}")
        return
    with pd.ExcelFile(excel_path) as xls:
        for sheet in xls.sheet_names:
            if sheet.lower().startswith('list of service') or sheet.lower() == 'anadarko' or sheet.lower() == 'master' or sheet.lower() == 'list of service':
                print(f"Seeding from sheet: {sheet}")
                df = pd.read_excel(xls, sheet_name=sheet)
                for _, row in df.iterrows():
                    s = Service(
                        stick_built_id=get_id_by_name(StickBuilt, row.get('Stick-Built')),
                        module_id=get_id_by_name(Module, row.get('Module')),
                        activities_id=get_id_by_name(Activities, row.get('Activities')),
                        title_id=get_id_by_name(Title, row.get('Title')),
                        technical_unit_id=get_id_by_name(TechnicalUnit, row.get('Technical Unit')),
                        employee_id=get_id_by_name(Employee, row.get('Assigned to')),
                        progress_id=get_id_by_name(Progress, row.get('Progress')),
                        professional_unit_id=get_id_by_name(ProfessionalUnit, row.get('Professional Role')),
                        project_id=get_id_by_name(Project, sheet),
                        department=row.get('Department'),
                        estimated_internal_hours=row.get('Estimated hours (internal)'),
                        estimated_external_hours=row.get('Estimated hours (external)'),
                        start_date=row.get('Start date'),
                        due_date=row.get('Due date'),
                        notes=row.get('Notes')
                    )
                    db.session.add(s)
                db.session.commit()
    print('Service seeding complete.')

if __name__ == '__main__':
    with app.app_context():
        seed_services_from_excel()
