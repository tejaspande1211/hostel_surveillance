import os
from dotenv import load_dotenv

# =========================
# Load Environment Variables
# =========================
load_dotenv()

# =========================
# Database
# =========================
DATABASE_PATH = 'db/hostel.db'

# =========================
# Face Recognition
# =========================
FACE_MODEL = 'ArcFace'
FACE_DETECTOR = 'opencv'   # avoids keras/mtcnn conflict
SIMILARITY_THRESHOLD = 0.50   # tune between 0.45–0.55
RECOGNITION_FPS = 2

# =========================
# Attendance
# =========================
DUPLICATE_WINDOW_MINUTES = 30

# =========================
# SMTP Email (Gmail)
# =========================
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587

SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')

WARDEN_EMAIL = os.environ.get('WARDEN_EMAIL', 'email add')

# =========================
# Twilio SMS (Optional)
# =========================
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_FROM = os.environ.get('TWILIO_FROM')

# Must include country code (+91)
WARDEN_PHONE = os.environ.get('WARDEN_PHONE', '# mobile number add')

SMS_GATEWAY_DOMAIN = os.environ.get('SMS_GATEWAY_DOMAIN')

# =========================
# File Paths
# =========================
KNOWN_FACES_DIR = 'data/known_faces'
UNKNOWN_CAPTURES = 'data/unknown_captures'
ALERT_FRAMES_DIR = 'data/alert_frames'

# =========================
# Create Required Folders
# =========================
REQUIRED_DIRS = [
    'db',
    KNOWN_FACES_DIR,
    UNKNOWN_CAPTURES,
    ALERT_FRAMES_DIR
]

for path in REQUIRED_DIRS:
    os.makedirs(path, exist_ok=True)

# =========================
# Twilio Enabled Check
# =========================
TWILIO_ENABLED = all([
    TWILIO_SID,
    TWILIO_TOKEN,
    TWILIO_FROM,
    WARDEN_PHONE
])

# =========================
# Validation
# =========================
def validate_config():
    # SMTP validation
    if not SMTP_USER or not SMTP_PASS:
        raise ValueError("❌ SMTP credentials missing in .env")

    if '@' not in SMTP_USER:
        raise ValueError("❌ Invalid SMTP email")

    # Phone validation
    if not WARDEN_PHONE.startswith('+'):
        raise ValueError("❌ Phone must include country code (+91...)")

validate_config()