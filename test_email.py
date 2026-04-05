import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = os.environ['SMTP_USER']
SMTP_PASS = os.environ['SMTP_PASS']
TO_EMAIL = os.environ.get('WARDEN_EMAIL', SMTP_USER)

msg = MIMEText("✅ Email working! Hostel system test successful.")
msg['Subject'] = "Test Email"
msg['From'] = SMTP_USER
msg['To'] = TO_EMAIL

try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("✅ Email sent successfully!")

except Exception as e:
    print("❌ Email failed:", e)