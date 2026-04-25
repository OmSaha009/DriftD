from config import Config
import sqlite3
import threading
import time
from datetime import datetime, timedelta


class Analyzer:
    def __init__(self, config: Config):
        self.config = config

    def _format_duration(self, seconds: float) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        formatted_time = ""
        if h>0:
            formatted_time += f"{h}h"
        if m>0:
            formatted_time += f"{m}m"
        if s>0:
            formatted_time += f"{s}s"
        return formatted_time
    
    def _print_report(self, cur: list[tuple[str, float]], title: str) -> str:
        if not cur:
            return f"===={title.upper()}====\n\nNo activity recorded\n"
            
        data = f"===={title.upper()}====\n\n"
        total = 0
        
        for category, duration in cur:
            duration_int = int(duration)
            total += duration_int
            data += f"{category}: {self._format_duration(duration_int)}\n"
        
        data += f"\nTOTAL: {self._format_duration(total)}\n"
        return data

    def report_today(self) -> str:
        """Return today's report as string."""
        today_date = datetime.now().date().isoformat()
        with sqlite3.connect(self.config.path_db) as conn:
            cursor = conn.execute("""
                SELECT category, SUM(duration_seconds) 
                FROM sessions 
                WHERE DATE(start_time) = ? 
                GROUP BY category
            """, (today_date,))
            return self._print_report(cursor.fetchall(), "Today")

    def report_week(self) -> str:
        """Return weekly report as string."""
        today = datetime.now().date().isoformat()
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        with sqlite3.connect(self.config.path_db) as conn:
            cursor = conn.execute("""
                SELECT category, SUM(duration_seconds) 
                FROM sessions 
                WHERE DATE(start_time) BETWEEN ? AND ? 
                GROUP BY category
            """, (week_ago, today))
            return self._print_report(cursor.fetchall(), "This Week")