import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, jsonify, session
from db.db_manager import DatabaseManager
from datetime import date
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)
db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_stats():
    today = date.today()
    total_students = db.fetch_one('SELECT COUNT(*) as c FROM students WHERE is_active=1')['c']
    present_today  = db.fetch_one('SELECT COUNT(*) as c FROM attendance_records WHERE date=?', (today,))['c']
    total_alerts   = db.fetch_one('SELECT COUNT(*) as c FROM alerts WHERE acknowledged=0')['c']
    total_logs     = db.fetch_one('SELECT COUNT(*) as c FROM recognition_logs')['c']
    return jsonify({
        'total_students': total_students,
        'present_today': present_today,
        'unacked_alerts': total_alerts,
        'total_logs': total_logs
    })
