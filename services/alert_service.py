import smtplib
import os
import cv2
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from twilio.rest import Client
from db.db_manager import DatabaseManager
from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS,
    WARDEN_EMAIL, ALERT_FRAMES_DIR, UNKNOWN_CAPTURES,
    TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, WARDEN_PHONE, SMS_GATEWAY_DOMAIN
)

class AlertService:
    def __init__(self):
        self.db = DatabaseManager()
        os.makedirs(ALERT_FRAMES_DIR, exist_ok=True)
        os.makedirs(UNKNOWN_CAPTURES, exist_ok=True)
        self.unknown_count = 0
        self.unknown_window_start = datetime.now()
        self.unknown_threshold = 3
        self.unknown_window = timedelta(seconds=12)
        self.last_unknown_alert_time = None

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
            subject = f'ALERT: Restricted Person Detected - {person["name"]}'
            body = (
                'SECURITY ALERT\n\n'
                'A restricted/blacklisted person entered the area.\n'
                f'Name: {person["name"]}\n'
                f'Reason: {person["reason"]}\n'
                f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                'Please respond immediately.'
            )
            email_sent = self._send_email(WARDEN_EMAIL, subject, body, img_path)
            sms_sent = self._send_sms(f'RESTRICTED PERSON ENTERED: {person["name"]} at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            self.db.execute(
                'UPDATE alerts SET email_sent=?, sms_sent=? WHERE image_path=?',
                (int(email_sent), int(sms_sent), img_path)
            )
        print(f'[Alert] Blacklist alert logged for person_id={person_id}')

    def log_unknown(self, frame):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        img_path = f'{UNKNOWN_CAPTURES}/unknown_{timestamp}.jpg'
        cv2.imwrite(img_path, frame)

        alert_id = self.db.execute(
            'INSERT INTO alerts (alert_type, person_type, image_path) VALUES (?,?,?)',
            ('unknown', 'unknown', img_path)
        )

        if self._should_send_unknown_notification():
            self._send_unknown_alert(alert_id, img_path)

        print(f'[Alert] Unknown person logged → {img_path}')

    def _should_send_unknown_notification(self):
        now = datetime.now()
        if now - self.unknown_window_start > self.unknown_window:
            self.unknown_count = 0
            self.unknown_window_start = now

        self.unknown_count += 1
        if self.unknown_count >= self.unknown_threshold:
            if not self.last_unknown_alert_time or (now - self.last_unknown_alert_time) >= self.unknown_window:
                self.last_unknown_alert_time = now
                self.unknown_count = 0
                self.unknown_window_start = now
                return True
        return False

    def _send_unknown_alert(self, alert_id, img_path):
        subject = 'ALERT: Unknown Person Detected'
        body = (
            'SECURITY ALERT\n\n'
            'An unknown/unrestricted person has been detected in multiple frames.\n'
            f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.\n\n'
            'Please review the capture and acknowledge the alert.'
        )
        email_sent = self._send_email(WARDEN_EMAIL, subject, body, img_path)
        sms_sent = self._send_sms(f'UNKNOWN PERSON ENTERED at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.')
        self.db.execute(
            'UPDATE alerts SET email_sent=?, sms_sent=? WHERE id=?',
            (int(email_sent), int(sms_sent), alert_id)
        )

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
            print(f'[Alert] Email failed: {e}')
            return False

    def _send_sms(self, message):
        if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and WARDEN_PHONE:
            try:
                client = Client(TWILIO_SID, TWILIO_TOKEN)
                client.messages.create(
                    body=message,
                    from_=TWILIO_FROM,
                    to=WARDEN_PHONE
                )
                print(f'[Alert] SMS sent to {WARDEN_PHONE} via Twilio')
                return True
            except Exception as e:
                print(f'[Alert] Twilio SMS failed: {e}')

        if SMS_GATEWAY_DOMAIN and WARDEN_PHONE:
            try:
                sms_address = f'{WARDEN_PHONE}@{SMS_GATEWAY_DOMAIN}'
                return self._send_email(sms_address, 'SMS Alert', message)
            except Exception as e:
                print(f'[Alert] SMS gateway email failed: {e}')

        print('[Alert] SMS not sent - Twilio or SMS gateway not configured')
        return False
