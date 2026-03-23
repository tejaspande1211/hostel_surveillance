import smtplib
import os
import cv2
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from db.db_manager import DatabaseManager
from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS,
    WARDEN_EMAIL, ALERT_FRAMES_DIR, UNKNOWN_CAPTURES
)

class AlertService:
    def __init__(self):
        self.db = DatabaseManager()
        os.makedirs(ALERT_FRAMES_DIR, exist_ok=True)
        os.makedirs(UNKNOWN_CAPTURES, exist_ok=True)

    def send_blacklist_alert(self, person_id, frame):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        img_path = f'{ALERT_FRAMES_DIR}/blacklist_{timestamp}.jpg'
        cv2.imwrite(img_path, frame)

        # Log alert to DB
        self.db.execute(
            'INSERT INTO alerts (alert_type, person_id, person_type, image_path) VALUES (?,?,?,?)',
            ('blacklist', person_id, 'blacklisted', img_path)
        )

        # Get blacklist info
        person = self.db.fetch_one(
            'SELECT * FROM blacklisted_persons WHERE id=?', (person_id,)
        )
        if person:
            subject = f'ALERT: Blacklisted Person Detected - {person["name"]}'
            body = (
                f'SECURITY ALERT\n\n'
                f'A blacklisted individual has been detected.\n'
                f'Name: {person["name"]}\n'
                f'Reason: {person["reason"]}\n'
                f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                f'Take immediate action.'
            )
            sent = self._send_email(WARDEN_EMAIL, subject, body, img_path)
            if sent:
                self.db.execute(
                    'UPDATE alerts SET email_sent=1 WHERE image_path=?', (img_path,)
                )
        print(f'[Alert] Blacklist alert logged for person_id={person_id}')

    def log_unknown(self, frame):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        img_path = f'{UNKNOWN_CAPTURES}/unknown_{timestamp}.jpg'
        cv2.imwrite(img_path, frame)

        self.db.execute(
            'INSERT INTO alerts (alert_type, person_type, image_path) VALUES (?,?,?)',
            ('unknown', 'unknown', img_path)
        )
        print(f'[Alert] Unknown person logged → {img_path}')

    def _send_email(self, to, subject, body, attachment_path=None):
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    msg.attach(img)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, to, msg.as_string())

            print(f'[Alert] Email sent to {to}')
            return True

        except Exception as e:
            print(f'[Alert] Email failed (not configured yet): {e}')
            return False