import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session
import bcrypt
from db.db_manager import DatabaseManager

auth_bp = Blueprint('auth', __name__)
db = DatabaseManager()

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '').encode('utf-8')
    user = db.fetch_one('SELECT * FROM admins WHERE username=?', (username,))
    role = 'admin'
    if not user:
        user = db.fetch_one('SELECT * FROM wardens WHERE username=?', (username,))
        role = 'warden'
    if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
        session['user_id'] = user['id']
        session['role'] = role
        session['username'] = username
        return jsonify({'message': 'Login successful', 'role': role})
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

@auth_bp.route('/api/auth/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({'user_id': session['user_id'], 'role': session['role'], 'username': session['username']})
