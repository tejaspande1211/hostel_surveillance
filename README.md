# Smart Hostel Surveillance & Face Recognition System

Final Year B.E. Project | AI / ML / Computer Vision / Flask

## Tech Stack
- Python 3.10, Flask, OpenCV, DeepFace (ArcFace), SQLite

## Features
- Real-time face recognition using ArcFace deep CNN (~80% confidence)
- Automatic attendance marking with duplicate prevention
- Unknown person threshold-based alerting (email notification)
- Blacklist detection with instant warden alert
- Role-based dashboard (Admin / Warden)
- Live MJPEG camera stream in browser

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/hostel_surveillance.git
cd hostel_surveillance
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install tensorflow==2.12.0
pip install deepface==0.0.75
pip install flask==3.0.0 flask-session opencv-python scipy bcrypt pillow python-dotenv
```

### 4. Initialize database
```bash
python db/init_db.py
```

### 5. Create admin user
```bash
python -c "
import bcrypt, sys
sys.path.insert(0, '.')
from db.db_manager import DatabaseManager
db = DatabaseManager()
pw = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
db.execute('INSERT OR IGNORE INTO admins (username,password,email) VALUES (?,?,?)', ('admin',pw,'admin@hostel.com'))
print('Admin created.')
"
```

### 6. Run
```bash
python app.py
```

Open browser: http://localhost:5000
Login: admin / admin123

## Important Notes
- Use `tensorflow==2.12.0` + `deepface==0.0.75` — newer versions break on Windows
- Do NOT install `mtcnn` — conflicts with TF 2.12
- Register student faces using webcam photos, not high-res studio photos

## Project Structure
```
hostel_surveillance/
├── app.py              # Flask entry point
├── config.py           # All configuration
├── db/                 # Database schema + manager
├── services/           # Camera, face recognition, alerts, attendance
├── routes/             # Flask API blueprints
├── templates/          # HTML templates
├── static/             # CSS + JS
└── data/               # Face images (gitignored)
```
Admin =  admin   and   admin123
Warden = warden1   and NewWardenPass123