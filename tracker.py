import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import Config
import win32gui, win32process, psutil


class WindowTracker:
    def __init__(self, config: Config):
        self.config = config
        self.current_session_id: Optional[int] = None
        self.running = False
        self.last_window: Optional[tuple[str, str]] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.config.path_db.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()


    def _init_database(self):
        with sqlite3.connect(self.config.path_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    window_title TEXT,
                    category TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds REAL
            """)
    def _get_current_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)

            if not title:
                title = "[No Title]"

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name()

            return(app_name, title)
        except Exception as e:
            print(f"ERROR: {e}")
            return ("Unknown", "")
        