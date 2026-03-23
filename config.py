import os

# Database
DATABASE_PATH = 'db/hostel.db'

# Face Recognition
FACE_MODEL = 'ArcFace'
FACE_DETECTOR = 'opencv'          # opencv (not mtcnn) — avoids keras conflict
SIMILARITY_THRESHOLD = 0.55
RECOGNITION_FPS = 2

# Attendance
DUPLICATE_WINDOW_MINUTES = 30

# SMTP Email
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = os.environ.get('SMTP_USER', 'your_email@gmail.com')
SMTP_PASS = os.environ.get('SMTP_PASS', 'your_app_password')
WARDEN_EMAIL = os.environ.get('WARDEN_EMAIL', 'warden@hostel.com')

# Twilio SMS (optional)
TWILIO_SID = os.environ.get('TWILIO_SID', '')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN', '')
TWILIO_FROM = os.environ.get('TWILIO_FROM', '')
WARDEN_PHONE = os.environ.get('WARDEN_PHONE', '')

# File Paths
KNOWN_FACES_DIR = 'data/known_faces'
UNKNOWN_CAPTURES = 'data/unknown_captures'
ALERT_FRAMES_DIR = 'data/alert_frames'