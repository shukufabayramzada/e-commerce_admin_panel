from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Company, User, Problem
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['JWT_SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route('/approve_company/<int:company_id>', methods=['POST'])
@jwt_required()
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approved = True
    db.session.commit()
    return jsonify({'message': 'Company approved successfully'}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'], is_admin=data.get('is_admin', False))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200

@app.route('/submit_problem', methods=['POST'])
@jwt_required()
def submit_problem():
    data = request.get_json()
    current_user = get_jwt_identity()
    new_problem = Problem(description=data['description'], user_id=current_user)
    db.session.add(new_problem)
    db.session.commit()
    return jsonify({'message': 'Problem submitted successfully'}), 201

@app.route('/view_problems', methods=['GET'])
@jwt_required()
def view_problems():
    problems = Problem.query.all()
    result = []
    for problem in problems:
        problem_data = {
            'id': problem.id,
            'description': problem.description,
            'status': problem.status
        }
        result.append(problem_data)
    return jsonify(result), 200

@app.route('/resolve_problem/<int:problem_id>', methods=['POST'])
@jwt_required()
def resolve_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    problem.status = 'resolved'
    db.session.commit()
    return jsonify({'message': 'Problem resolved successfully'}), 200

@app.route('/create_admin', methods=['POST'])
@jwt_required()
def create_admin():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    data = request.get_json()
    new_admin = User(username=data['username'], password=data['password'], is_admin=True)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': 'Admin user created successfully'}), 201

@app.route('/list_admins', methods=['GET'])
@jwt_required()
def list_admins():
    admins = User.query.filter_by(is_admin=True).all()
    result = []
    for admin in admins:
        admin_data = {
            'id': admin.id,
            'username': admin.username
        }
        result.append(admin_data)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
