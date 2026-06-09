import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
KNOWN_FACES_DIR = DATA_DIR / "known_faces"
REPORTS_DIR = DATA_DIR / "reports"
DATABASE_PATH = DATA_DIR / "attendance.db"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"

os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)

FACE_RECOGNITION_TOLERANCE = 0.5
FACE_RECOGNITION_THRESHOLD = 0.5
FRAMES_PER_SECOND = 30
CAMERA_ID = 0

DATABASE_FILENAME = "attendance.db"
USERS_TABLE = "users"
ATTENDANCE_TABLE = "attendance"

ATTENDANCE_STATUS_PRESENT = "Present"
ATTENDANCE_STATUS_ABSENT = "Absent"
ATTENDANCE_STATUS_LATE = "Late"
