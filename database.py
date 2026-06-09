import sqlite3
from datetime import datetime
from config import DATABASE_PATH, USERS_TABLE, ATTENDANCE_TABLE

class AttendanceDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {USERS_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {ATTENDANCE_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES {USERS_TABLE}(id)
            )
        """)

        conn.commit()
        conn.close()

    def user_exists(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def add_user(self, name, email=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"INSERT INTO {USERS_TABLE} (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_user_id(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, name FROM {USERS_TABLE}")
        users = cursor.fetchall()
        conn.close()
        return users

    def log_attendance(self, user_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {ATTENDANCE_TABLE} (user_id, timestamp, status) VALUES (?, ?, ?)",
            (user_id, datetime.now(), status)
        )
        conn.commit()
        conn.close()

    def get_attendance_records(self, user_id=None, days=30):
        conn = self.get_connection()
        cursor = conn.cursor()

        if user_id:
            query = f"""
                SELECT u.name, a.timestamp, a.status
                FROM {ATTENDANCE_TABLE} a
                JOIN {USERS_TABLE} u ON a.user_id = u.id
                WHERE a.user_id = ? AND a.timestamp >= datetime('now', '-{days} days')
                ORDER BY a.timestamp DESC
            """
            cursor.execute(query, (user_id,))
        else:
            query = f"""
                SELECT u.name, a.timestamp, a.status
                FROM {ATTENDANCE_TABLE} a
                JOIN {USERS_TABLE} u ON a.user_id = u.id
                WHERE a.timestamp >= datetime('now', '-{days} days')
                ORDER BY a.timestamp DESC
            """
            cursor.execute(query)

        records = cursor.fetchall()
        conn.close()
        return records

    def get_user_statistics(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM {ATTENDANCE_TABLE}
            WHERE user_id = ?
            GROUP BY status
        """, (user_id,))

        stats = cursor.fetchall()
        conn.close()
        return {status: count for status, count in stats}

    def get_all_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT u.name, COUNT(*) as total,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) as late
            FROM {ATTENDANCE_TABLE} a
            JOIN {USERS_TABLE} u ON a.user_id = u.id
            GROUP BY u.id, u.name
        """)

        stats = cursor.fetchall()
        conn.close()
        return stats
