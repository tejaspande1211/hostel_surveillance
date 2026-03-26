import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session
from db.db_manager import DatabaseManager
from services.face_recognizer import FaceRecognizer
from functools import wraps

blacklist_bp = Blueprint('blacklist', __name__)
db = DatabaseManager()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@blacklist_bp.route('/api/blacklist', methods=['GET'])
@login_required
def get_blacklist():
    persons = db.fetch_all('SELECT * FROM blacklisted_persons ORDER BY created_at DESC')
    return jsonify([dict(p) for p in persons])


@blacklist_bp.route('/api/blacklist', methods=['POST'])
@login_required
def add_blacklisted_person():
    name = request.form.get('name')
    reason = request.form.get('reason')
    image = request.files.get('image')

    if not name or not reason or image is None:
        return jsonify({'error': 'Name, reason and image are required'}), 400

    try:
        added_by = session.get('user_id')
        person_id = db.execute(
            'INSERT INTO blacklisted_persons (name, reason, added_by, image_path) VALUES (?,?,?,?)',
            (name, reason, added_by, '')
        )

        save_dir = os.path.join('data', 'known_faces', 'blacklisted', str(person_id))
        os.makedirs(save_dir, exist_ok=True)
        image_path = os.path.join(save_dir, 'face.jpg')
        image.save(image_path)

        recognizer = FaceRecognizer()
        db.execute('DELETE FROM face_embeddings WHERE person_type=? AND person_id=?', ('blacklisted', person_id))
        recognizer.add_face('blacklisted', person_id, image_path)

        # Update blacklisted_persons row with path once saved
        db.execute('UPDATE blacklisted_persons SET image_path=? WHERE id=?', (image_path, person_id))

        return jsonify({'message': 'Person blacklisted', 'id': person_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@blacklist_bp.route('/api/blacklist/<int:pid>', methods=['DELETE'])
@login_required
def remove_blacklisted_person(pid):
    db.execute('DELETE FROM blacklisted_persons WHERE id=?', (pid,))
    db.execute('DELETE FROM face_embeddings WHERE person_type=? AND person_id=?', ('blacklisted', pid))
    folder = os.path.join('data', 'known_faces', 'blacklisted', str(pid))
    try:
        if os.path.isdir(folder):
            for root, dirs, files in os.walk(folder, topdown=False):
                for f in files:
                    os.remove(os.path.join(root, f))
                for d in dirs:
                    os.rmdir(os.path.join(root, d))
            os.rmdir(folder)
    except Exception:
        pass
    return jsonify({'message': 'Person removed from blacklist'})
