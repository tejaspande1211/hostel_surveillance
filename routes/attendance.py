import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session
from db.db_manager import DatabaseManager
from functools import wraps

attendance_bp = Blueprint('attendance', __name__)
db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@attendance_bp.route('/api/attendance', methods=['GET'])
@login_required
def get_attendance():
    date = request.args.get('date')
    if date:
        records = db.fetch_all(
            'SELECT a.*, s.name, s.roll_number FROM attendance_records a JOIN students s ON a.student_id=s.id WHERE a.date=? ORDER BY a.time_in DESC',
            (date,)
        )
    else:
        records = db.fetch_all(
            'SELECT a.*, s.name, s.roll_number FROM attendance_records a JOIN students s ON a.student_id=s.id ORDER BY a.date DESC, a.time_in DESC LIMIT 100'
        )
    return jsonify([dict(r) for r in records])
