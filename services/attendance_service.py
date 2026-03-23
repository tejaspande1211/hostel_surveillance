import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from db.db_manager import DatabaseManager
from config import DUPLICATE_WINDOW_MINUTES

class AttendanceService:
    def __init__(self):
        self.db = DatabaseManager()

    def mark_attendance(self, student_id):
        today = datetime.now().date()
        now = datetime.now()
        window_start = now - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)

        # Check if already marked within time window
        existing = self.db.fetch_one(
            'SELECT * FROM attendance_records WHERE student_id=? AND date=? AND time_in > ?',
            (student_id, today, window_start)
        )
        if existing:
            print(f'[Attendance] Duplicate skipped for student_id={student_id}')
            return False

        # First time today → insert, else update time_out
        daily_record = self.db.fetch_one(
            'SELECT * FROM attendance_records WHERE student_id=? AND date=?',
            (student_id, today)
        )
        if daily_record:
            self.db.execute(
                'UPDATE attendance_records SET time_out=? WHERE student_id=? AND date=?',
                (now, student_id, today)
            )
            print(f'[Attendance] time_out updated for student_id={student_id}')
        else:
            self.db.execute(
                'INSERT INTO attendance_records (student_id, date, time_in) VALUES (?,?,?)',
                (student_id, today, now)
            )
            print(f'[Attendance] Marked PRESENT for student_id={student_id}')

        return True