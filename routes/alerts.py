import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session
from db.db_manager import DatabaseManager
from functools import wraps

alerts_bp = Blueprint('alerts', __name__)
db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@alerts_bp.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    alerts = db.fetch_all('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 50')
    return jsonify([dict(a) for a in alerts])

@alerts_bp.route('/api/alerts/<int:aid>/ack', methods=['POST'])
@login_required
def acknowledge_alert(aid):
    db.execute('UPDATE alerts SET acknowledged=1 WHERE id=?', (aid,))
    return jsonify({'message': 'Alert acknowledged'})
