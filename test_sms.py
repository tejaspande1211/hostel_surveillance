import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

try:
    client = Client(
        os.environ['TWILIO_SID'],
        os.environ['TWILIO_TOKEN']
    )

    message = client.messages.create(
        body="✅ SMS working! Hostel alert system ready.",
        from_=os.environ['TWILIO_FROM'],
        to=os.environ['WARDEN_PHONE']
    )

    print("✅ SMS sent! SID:", message.sid)

except Exception as e:
    print("❌ SMS failed:", e)