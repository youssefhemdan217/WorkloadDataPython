
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flasgger import Swagger
import pandas as pd
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workload.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
swagger = Swagger(app)

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

# --- CRUD Resources ---
class EntityListResource(Resource):
    def get(self, entity):
        """Get all items for an entity
        ---
        parameters:
          - in: path
            name: entity
            type: string
            required: true
        responses:
          200:
            description: List of items
        """
        model = globals()[entity]
        items = model.query.all()
        return jsonify([{ 'id': i.id, 'name': i.name } for i in items])
    def post(self, entity):
        """Create a new item for an entity
        ---
        parameters:
          - in: path
            name: entity
            type: string
            required: true
          - in: body
            name: body
            schema:
              properties:
                name:
                  type: string
        responses:
          200:
            description: Created item
        """
        model = globals()[entity]
        data = request.json
        item = model(name=data['name'])
        db.session.add(item)
        db.session.commit()
        return jsonify({'id': item.id, 'name': item.name})

class EntityResource(Resource):
    def get(self, entity, id):
        """Get a single item by id
        ---
        parameters:
          - in: path
            name: entity
            type: string
            required: true
          - in: path
            name: id
            type: integer
            required: true
        responses:
          200:
            description: Item
        """
        model = globals()[entity]
        item = model.query.get_or_404(id)
        return jsonify({'id': item.id, 'name': item.name})
    def put(self, entity, id):
        """Update an item by id
        ---
        parameters:
          - in: path
            name: entity
            type: string
            required: true
          - in: path
            name: id
            type: integer
            required: true
          - in: body
            name: body
            schema:
              properties:
                name:
                  type: string
        responses:
          200:
            description: Updated item
        """
        model = globals()[entity]
        item = model.query.get_or_404(id)
        data = request.json
        item.name = data['name']
        db.session.commit()
        return jsonify({'id': item.id, 'name': item.name})
    def delete(self, entity, id):
        """Delete an item by id
        ---
        parameters:
          - in: path
            name: entity
            type: string
            required: true
          - in: path
            name: id
            type: integer
            required: true
        responses:
          204:
            description: Deleted
        """
        model = globals()[entity]
        item = model.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

# --- Service CRUD ---
class ServiceListResource(Resource):
    def get(self):
        """Get all services (optionally filter by project_id)
        ---
        parameters:
          - in: query
            name: project_id
            type: integer
            required: false
        responses:
          200:
            description: List of services
        """
        project_id = request.args.get('project_id')
        q = Service.query
        if project_id:
            q = q.filter_by(project_id=project_id)
        services = q.all()
        def to_dict(s):
            return {
                'id': s.id,
                'stick_built_id': s.stick_built_id,
                'module_id': s.module_id,
                'activities_id': s.activities_id,
                'title_id': s.title_id,
                'technical_unit_id': s.technical_unit_id,
                'employee_id': s.employee_id,
                'progress_id': s.progress_id,
                'professional_unit_id': s.professional_unit_id,
                'project_id': s.project_id,
                'department': s.department,
                'estimated_internal_hours': s.estimated_internal_hours,
                'estimated_external_hours': s.estimated_external_hours,
                'start_date': s.start_date,
                'due_date': s.due_date,
                'notes': s.notes
            }
        return jsonify([to_dict(s) for s in services])
    def post(self):
        """Create a new service
        ---
        parameters:
          - in: body
            name: body
            schema:
              properties:
                stick_built_id: {type: integer}
                module_id: {type: integer}
                activities_id: {type: integer}
                title_id: {type: integer}
                technical_unit_id: {type: integer}
                employee_id: {type: integer}
                progress_id: {type: integer}
                professional_unit_id: {type: integer}
                project_id: {type: integer}
                department: {type: string}
                estimated_internal_hours: {type: integer}
                estimated_external_hours: {type: integer}
                start_date: {type: string}
                due_date: {type: string}
                notes: {type: string}
        responses:
          200:
            description: Created service
        """
        data = request.json
        s = Service(**data)
        db.session.add(s)
        db.session.commit()
        return jsonify({'id': s.id})

class ServiceResource(Resource):
    def get(self, id):
        """Get a service by id
        ---
        parameters:
          - in: path
            name: id
            type: integer
            required: true
        responses:
          200:
            description: Service
        """
        s = Service.query.get_or_404(id)
        return jsonify({
            'id': s.id,
            'stick_built_id': s.stick_built_id,
            'module_id': s.module_id,
            'activities_id': s.activities_id,
            'title_id': s.title_id,
            'technical_unit_id': s.technical_unit_id,
            'employee_id': s.employee_id,
            'progress_id': s.progress_id,
            'professional_unit_id': s.professional_unit_id,
            'project_id': s.project_id,
            'department': s.department,
            'estimated_internal_hours': s.estimated_internal_hours,
            'estimated_external_hours': s.estimated_external_hours,
            'start_date': s.start_date,
            'due_date': s.due_date,
            'notes': s.notes
        })
    def put(self, id):
        """Update a service by id
        ---
        parameters:
          - in: path
            name: id
            type: integer
            required: true
          - in: body
            name: body
            schema:
              properties:
                stick_built_id: {type: integer}
                module_id: {type: integer}
                activities_id: {type: integer}
                title_id: {type: integer}
                technical_unit_id: {type: integer}
                employee_id: {type: integer}
                progress_id: {type: integer}
                professional_unit_id: {type: integer}
                project_id: {type: integer}
                department: {type: string}
                estimated_internal_hours: {type: integer}
                estimated_external_hours: {type: integer}
                start_date: {type: string}
                due_date: {type: string}
                notes: {type: string}
        responses:
          200:
            description: Updated service
        """
        s = Service.query.get_or_404(id)
        data = request.json
        for k, v in data.items():
            setattr(s, k, v)
        db.session.commit()
        return jsonify({'id': s.id})
    def delete(self, id):
        """Delete a service by id
        ---
        parameters:
          - in: path
            name: id
            type: integer
            required: true
        responses:
          204:
            description: Deleted
        """
        s = Service.query.get_or_404(id)
        db.session.delete(s)
        db.session.commit()
        return '', 204

# --- Import from Excel to Service Table ---
@app.route('/import_service', methods=['POST'])
def import_service():
    """Import services from Excel
    ---
    parameters:
      - in: body
        name: body
        schema:
          properties:
            excel_path: {type: string}
            sheet_name: {type: string}
    responses:
      200:
        description: Import status
    """
    excel_path = request.json.get('excel_path', 'FABSI_List of Service HO_Master_R1.xlsx')
    sheet_name = request.json.get('sheet_name', 'List of Service')
    if not os.path.exists(excel_path):
        return jsonify({'error': 'Excel file not found'}), 404
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    for _, row in df.iterrows():
        s = Service(
            stick_built_id=None,  # You can map by name if needed
            module_id=None,
            activities_id=None,
            title_id=None,
            technical_unit_id=None,
            employee_id=None,
            progress_id=None,
            professional_unit_id=None,
            project_id=None,
            department=row.get('Department'),
            estimated_internal_hours=row.get('Estimated hours (internal)'),
            estimated_external_hours=row.get('Estimated hours (external)'),
            start_date=row.get('Start date'),
            due_date=row.get('Due date'),
            notes=row.get('Notes')
        )
        db.session.add(s)
    db.session.commit()
    return jsonify({'status': 'imported'})

# --- API Routes ---
# --- API Routes ---

entities = ['StickBuilt', 'Module', 'Activities', 'Title', 'TechnicalUnit', 'Employee', 'Progress', 'ProfessionalUnit', 'Project']
for entity in entities:
    api.add_resource(EntityListResource, f'/{entity.lower()}s', endpoint=f'{entity.lower()}s', resource_class_kwargs={'entity': entity})
    api.add_resource(EntityResource, f'/{entity.lower()}s/<int:id>', endpoint=f'{entity.lower()}_detail', resource_class_kwargs={'entity': entity})
api.add_resource(ServiceListResource, '/services')
api.add_resource(ServiceResource, '/services/<int:id>')

# --- Swagger root endpoint ---
@app.route('/')
def docs():
    return '''<h2>API is running</h2>
    <p>See <a href="/apidocs">Swagger UI</a> for documentation.</p>'''


if __name__ == '__main__':
    app.run(debug=True, port=5000)
