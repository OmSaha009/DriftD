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
                    duration_seconds REAL)
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
        
        
    def _start_new_session(self, app_name: str, window_title: str):
        """Begin a new session for the current window"""
        print(f"🔵 STARTING session for: {app_name}")
        category = self.config.get_category(app_name, window_title)
        print(f"DEBUG: Starting session - App:{app_name}, Title:{window_title}, Category:{category}")
        with self._lock:
            with sqlite3.connect(self.config.path_db) as conn:
                cursor = conn.execute("""INSERT INTO sessions (app_name, window_title, category, start_time) VALUES (?, ?, ?, ?)""", (app_name, window_title, category, datetime.now()))
                self.current_session_id = cursor.lastrowid

            print(f"DEBUG: Session ID = {self.current_session_id}")

    def _close_current_session(self):
        """End the current active session"""

        if self.current_session_id is None:
            return
        print(f"🔴 CLOSING session {self.current_session_id}")
        with self._lock:
            with sqlite3.connect(self.config.path_db) as conn:
                row = conn.execute("SELECT start_time FROM sessions WHERE id = ?", (self.current_session_id,)).fetchone()
                if row:
                    start = datetime.fromisoformat(row[0])
                    duration = (datetime.now() - start).total_seconds()

                    conn.execute("UPDATE sessions SET end_time = ?, duration_seconds = ? WHERE id = ?", (datetime.now(), duration, self.current_session_id))

                    self.current_session_id = None

    def _track_loop(self):
        print("LOOP STARTED")
        """Background thread that watches for window change"""
        while self.running:
            try:
                current = self._get_current_window()
                print(f"DEBUG: Current = {current}")  # ADD THIS
                print(f"DEBUG: Last = {self.last_window}")  # ADD THIS

                if self.last_window != current:
                    print("DEBUG: WINDOW CHANGED!")
                    """Window has been changed, a new session has been activated"""
                    self._close_current_session()
                    self._start_new_session(current[0], current[1])
                    self.last_window = current
                    print(f"Switched to {current[0]} - {current[1]}")
                
                time.sleep(2)

            except Exception as e:
                print(f"Tracking loop error occurred: {e}")
                time.sleep(5)

    def start(self):
        """Start tracker loop"""
        if self.running:
            print("Tracker already running")
            return
        self.running = True
        self._thread = threading.Thread(target=self._track_loop, daemon=True)
        self._thread.start()
        print("Tracker Started")

    def stop(self):
        """Stop tracker loop"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=3)

        self._close_current_session()

        print("Tracker Stopped")