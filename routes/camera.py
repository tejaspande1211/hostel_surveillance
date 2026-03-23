import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, Response, jsonify, session
from functools import wraps
import cv2

camera_bp = Blueprint('camera', __name__)
camera_service = None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def generate_frames():
    while True:
        if camera_service is None:
            break
        frame = camera_service.get_annotated_frame()
        if frame is None:
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

@camera_bp.route('/api/camera/stream')
@login_required
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/api/camera/status')
@login_required
def status():
    running = camera_service is not None and camera_service.running
    return jsonify({'running': running})
