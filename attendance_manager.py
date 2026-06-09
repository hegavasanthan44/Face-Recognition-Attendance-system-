from database import AttendanceDatabase
from config import ATTENDANCE_STATUS_PRESENT, ATTENDANCE_STATUS_LATE
from datetime import datetime, timedelta

class AttendanceManager:
    def __init__(self):
        self.db = AttendanceDatabase()

    def register_user(self, name, email=""):
        if self.db.user_exists(name):
            return False, f"User '{name}' already exists"

        user_id = self.db.add_user(name, email)
        if user_id:
            return True, f"User '{name}' registered successfully"
        return False, "Error registering user"

    def mark_attendance(self, name, status=ATTENDANCE_STATUS_PRESENT):
        user_id = self.db.get_user_id(name)
        if not user_id:
            return False, f"User '{name}' not found"

        today = datetime.now().date()
        records = self.db.get_attendance_records(user_id, days=1)

        for record in records:
            record_date = datetime.fromisoformat(record[1]).date()
            if record_date == today:
                return False, f"Attendance already marked for {name} today"

        self.db.log_attendance(user_id, status)
        return True, f"Attendance marked for {name}"

    def get_user_attendance_history(self, name, days=30):
        user_id = self.db.get_user_id(name)
        if not user_id:
            return []

        records = self.db.get_attendance_records(user_id, days)
        return records

    def get_all_users(self):
        return self.db.get_all_users()

    def get_user_statistics(self, name):
        user_id = self.db.get_user_id(name)
        if not user_id:
            return None

        stats = self.db.get_user_statistics(user_id)
        total = sum(stats.values())

        return {
            "name": name,
            "total_days": total,
            "present": stats.get("Present", 0),
            "late": stats.get("Late", 0),
            "absent": stats.get("Absent", 0),
            "percentage": round((stats.get("Present", 0) / total * 100) if total > 0 else 0, 2)
        }

    def get_all_statistics(self):
        all_stats = self.db.get_all_statistics()
        formatted_stats = []

        for row in all_stats:
            name, total, present, late = row
            present = present or 0
            late = late or 0

            formatted_stats.append({
                "name": name,
                "total_days": total,
                "present": present,
                "late": late,
                "percentage": round((present / total * 100) if total > 0 else 0, 2)
            })

        return sorted(formatted_stats, key=lambda x: x["percentage"], reverse=True)

    def get_attendance_summary(self):
        all_stats = self.get_all_statistics()

        if not all_stats:
            return None

        total_people = len(all_stats)
        avg_attendance = sum(stat["percentage"] for stat in all_stats) / total_people if total_people > 0 else 0

        return {
            "total_registered": total_people,
            "average_attendance": round(avg_attendance, 2),
            "details": all_stats
        }
