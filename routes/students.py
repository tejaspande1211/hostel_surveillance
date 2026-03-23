import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session
from db.db_manager import DatabaseManager
from services.face_recognizer import FaceRecognizer
from functools import wraps

students_bp = Blueprint('students', __name__)
db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@students_bp.route('/api/students', methods=['GET'])
@login_required
def get_students():
    students = db.fetch_all('SELECT * FROM students WHERE is_active=1')
    return jsonify([dict(s) for s in students])

@students_bp.route('/api/students', methods=['POST'])
@login_required
def add_student():
    data = request.get_json()
    try:
        sid = db.execute(
            'INSERT INTO students (roll_number, name, email, phone, room_number, hostel_block, course, year) VALUES (?,?,?,?,?,?,?,?)',
            (data['roll_number'], data['name'], data.get('email'), data.get('phone'),
             data.get('room_number'), data.get('hostel_block'), data.get('course'), data.get('year'))
        )
        return jsonify({'message': 'Student added', 'id': sid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@students_bp.route('/api/students/<int:sid>', methods=['PUT'])
@login_required
def update_student(sid):
    data = request.get_json()
    db.execute(
        'UPDATE students SET name=?, email=?, phone=?, room_number=?, hostel_block=?, course=?, year=? WHERE id=?',
        (data.get('name'), data.get('email'), data.get('phone'),
         data.get('room_number'), data.get('hostel_block'), data.get('course'), data.get('year'), sid)
    )
    return jsonify({'message': 'Student updated'})

@students_bp.route('/api/students/<int:sid>', methods=['DELETE'])
@login_required
def delete_student(sid):
    db.execute('UPDATE students SET is_active=0 WHERE id=?', (sid,))
    return jsonify({'message': 'Student removed'})

@students_bp.route('/api/students/<int:sid>/face', methods=['POST'])
@login_required
def upload_face(sid):
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    save_dir = f'data/known_faces/students/{sid}'
    os.makedirs(save_dir, exist_ok=True)
    path = f'{save_dir}/face.jpg'
    file.save(path)
    try:
        r = FaceRecognizer()
        db.execute('DELETE FROM face_embeddings WHERE person_type=? AND person_id=?', ('student', sid))
        r.add_face('student', sid, path)
        return jsonify({'message': 'Face registered successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
