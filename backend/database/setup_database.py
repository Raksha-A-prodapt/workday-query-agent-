"""
Database Setup Script for Workday HR Agent.
Reads schema.sql, initializes SQLite database workday_hr.db, and seeds synthetic data.
"""

import os
import sqlite3
from seed_data import seed_database


def init_db(db_path: str, schema_path: str):
    """Initialize database from schema.sql and seed data."""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database schema applied successfully.")

    # Seed data
    seed_database(db_path)


def verify_counts(db_path: str):
    """Print record counts for verification."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["regions", "departments", "employees", "leave_records", "job_openings"]
    print("\n--- Database Verification Counts ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table '{table}': {count} records")

    conn.close()


if __name__ == "__main__":
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(db_dir, "workday_hr.db")
    schema_file = os.path.join(db_dir, "schema.sql")

    init_db(db_file, schema_file)
    verify_counts(db_file)
