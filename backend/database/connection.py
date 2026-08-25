"""
SQLite Database Connection Management.
"""

import os
import sqlite3
from backend.core.config import settings


def get_db_connection():
    """Verify and open SQLite database connection using configured DB_PATH."""
    abs_db_path = os.path.abspath(settings.DB_PATH)
    if not os.path.exists(abs_db_path):
        raise FileNotFoundError(f"Database file not found at {abs_db_path}")
    conn = sqlite3.connect(abs_db_path)
    return conn


def check_db_health() -> str:
    """Execute simple test query to verify database accessibility."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
        return "connected"
    except Exception as e:
        return f"disconnected: {str(e)}"
