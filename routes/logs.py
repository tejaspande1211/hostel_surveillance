import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session
from db.db_manager import DatabaseManager
from functools import wraps

logs_bp = Blueprint('logs', __name__)
db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@logs_bp.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    limit = request.args.get('limit', 50)
    logs = db.fetch_all('''
        SELECT rl.*, s.name AS student_name, b.name AS blacklist_name
        FROM recognition_logs rl
        LEFT JOIN students s ON rl.person_type='student' AND rl.person_id=s.id
        LEFT JOIN blacklisted_persons b ON rl.person_type='blacklisted' AND rl.person_id=b.id
        ORDER BY rl.timestamp DESC LIMIT ?
    ''', (limit,))
    return jsonify([dict(l) for l in logs])
