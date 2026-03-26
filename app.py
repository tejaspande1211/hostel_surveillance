import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from flask import Flask, render_template, redirect
from services.camera_service import CameraService
import routes.camera as camera_route
from routes.auth import auth_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.alerts import alerts_bp
from routes.dashboard import dashboard_bp
from routes.camera import camera_bp
from routes.logs import logs_bp
from routes.blacklist import blacklist_bp

app = Flask(__name__)
app.secret_key = 'hostel_surveillance_secret_change_in_production'

camera = CameraService()
camera.start()
camera_route.camera_service = camera

app.register_blueprint(auth_bp)
app.register_blueprint(students_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(camera_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(blacklist_bp)

@app.route('/')
def index(): return redirect('/login')

@app.route('/login')
def login_page(): return render_template('login.html')

@app.route('/dashboard')
def dashboard_page(): return render_template('base.html')

@app.route('/students')
def students_page(): return render_template('base.html')

@app.route('/camera')
def camera_page(): return render_template('base.html')

@app.route('/alerts')
def alerts_page(): return render_template('base.html')

@app.route('/attendance')
def attendance_page(): return render_template('base.html')

@app.route('/logs')
def logs_page(): return render_template('base.html')

@app.route('/blacklist')
def blacklist_page(): return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)
