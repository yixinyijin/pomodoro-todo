"""
Database module for Pomodoro Todo application.
Handles all SQLite database operations.
"""
import sqlite3
from datetime import datetime
from pathlib import Path


class Database:
    """Database manager for SQLite operations."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "app.db"
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 2,
                status INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create pomodoros table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                duration INTEGER,
                start_time DATETIME,
                end_time DATETIME,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Create settings table for theme
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()

    # Task operations
    def create_task(self, title: str, description: str = "", priority: int = 2) -> int:
        """Create a new task and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
            (title, description, priority)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_task(self, task_id: int) -> dict:
        """Get task by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_tasks(self) -> list:
        """Get all tasks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_tasks_by_status(self, status: int) -> list:
        """Get tasks by status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY priority, created_at", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_task(self, task_id: int, **kwargs):
        """Update task fields."""
        if not kwargs:
            return
        kwargs["updated_at"] = datetime.now().isoformat()
        conn = self._get_connection()
        cursor = conn.cursor()
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        cursor.execute(f"UPDATE tasks SET {fields} WHERE id = ?", list(kwargs.values()) + [task_id])
        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        """Delete task by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    # Pomodoro operations
    def create_pomodoro(self, task_id: int, duration: int, start_time: datetime, end_time: datetime) -> int:
        """Create a new pomodoro record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pomodoros (task_id, duration, start_time, end_time) VALUES (?, ?, ?, ?)",
            (task_id, duration, start_time, end_time)
        )
        pomodoro_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pomodoro_id

    def get_pomodoros_by_task(self, task_id: int) -> list:
        """Get all pomodoro records for a task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pomodoros WHERE task_id = ? ORDER BY start_time DESC", (task_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_today_pomodoros(self) -> list:
        """Get today's pomodoro records."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM pomodoros WHERE DATE(start_time) = DATE('now', 'localtime') ORDER BY start_time DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_pomodoros(self) -> list:
        """Get all pomodoro records."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pomodoros ORDER BY start_time DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_pomodoro(self, pomodoro_id: int):
        """Delete pomodoro record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pomodoros WHERE id = ?", (pomodoro_id,))
        conn.commit()
        conn.close()

    # Statistics
    def get_pomodoro_stats(self) -> dict:
        """Get pomodoro statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Today's count
        cursor.execute(
            "SELECT COUNT(*) as count FROM pomodoros WHERE DATE(start_time) = DATE('now', 'localtime')"
        )
        today_count = cursor.fetchone()["count"]

        # Today's total duration
        cursor.execute(
            "SELECT SUM(duration) as total FROM pomodoros WHERE DATE(start_time) = DATE('now', 'localtime')"
        )
        today_duration = cursor.fetchone()["total"] or 0

        # All-time total duration
        cursor.execute("SELECT SUM(duration) as total FROM pomodoros")
        all_time_duration = cursor.fetchone()["total"] or 0

        conn.close()
        return {
            "today_count": today_count,
            "today_duration": today_duration,
            "all_time_duration": all_time_duration
        }

    # Settings operations
    def get_setting(self, key: str, default: str = None) -> str:
        """Get setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        """Set setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
