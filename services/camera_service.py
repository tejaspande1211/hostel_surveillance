import cv2
import threading
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.face_recognizer import FaceRecognizer
from db.db_manager import DatabaseManager
from services.alert_service import AlertService
from services.attendance_service import AttendanceService


class CameraService:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()

        self.recognizer = FaceRecognizer()
        self.db = DatabaseManager()
        self.alert_svc = AlertService()
        self.attendance_svc = AttendanceService()

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # ✅ Optimization variables
        self.last_process_time = 0
        self.process_interval = 1.0   # process every 1 second
        self.frame_count = 0

        print('[CameraService] Initialized.')

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)

        # ✅ Reduce resolution → faster performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            print('[CameraService] ERROR: Cannot open camera.')
            return False

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

        print('[CameraService] Camera started.')
        return True

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        print('[CameraService] Camera stopped.')

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def get_annotated_frame(self):
        frame = self.get_frame()
        if frame is None:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        return frame

    def reload_embeddings(self):
        self.recognizer.load_embeddings_from_db()
        print('[CameraService] Embeddings reloaded')

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                print('[CameraService] Frame read failed.')
                time.sleep(0.1)
                continue

            # Store frame safely
            with self.lock:
                self.frame = frame

            # ✅ Skip frames (process only every 3rd frame)
            self.frame_count += 1
            if self.frame_count % 3 != 0:
                continue

            # ✅ Process every 1 second
            now = time.time()
            if now - self.last_process_time >= self.process_interval:
                threading.Thread(
                    target=self._process_frame,
                    args=(frame.copy(),),
                    daemon=True
                ).start()

                self.last_process_time = now

    def _process_frame(self, frame):
        try:
            # ✅ Resize frame → faster recognition
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=6,
                minSize=(60, 60)
            )

            if len(faces) == 0:
                return

            # ✅ Recognize face
            result = self.recognizer.recognize(small_frame)

            self._handle_recognition(result, frame)

        except Exception as e:
            print(f'[CameraService] Processing error: {e}')

    def _handle_recognition(self, result, original_frame):
        ptype = result['person_type']
        pid = result['person_id']
        conf = result['confidence']

        # ✅ Ignore low confidence (prevents false alerts)
        if conf < 0.4:
            print('[Recognition] Low confidence, ignored')
            return

        # Log every event
        self.db.execute(
            'INSERT INTO recognition_logs (person_type, person_id, confidence) VALUES (?,?,?)',
            (ptype, pid, conf)
        )

        print(f'[Recognition] type={ptype} id={pid} confidence={conf}')

        # =========================
        # ROUTING LOGIC (UNCHANGED)
        # =========================
        if ptype == 'student':
            student = self.db.fetch_one(
                'SELECT * FROM students WHERE id=? AND is_active=1',
                (pid,)
            )
            if student:
                self.attendance_svc.mark_attendance(pid)

        elif ptype == 'blacklisted':
            person = self.db.fetch_one(
                'SELECT * FROM blacklisted_persons WHERE id=?',
                (pid,)
            )
            if person:
                self.alert_svc.send_blacklist_alert(pid, original_frame)

        elif ptype == 'unknown':
            self.alert_svc.log_unknown(original_frame)