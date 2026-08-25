"""
Safe SQL Execution Module.
Validates input SQL using validator module and executes read-only queries against SQLite database workday_hr.db.
"""

import os
import sys
import sqlite3
from typing import Any, Dict, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.connection import get_db_connection
from backend.sql.validator import validate_sql

DEFAULT_MAX_ROWS = 100


def execute_safe_query(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> Dict[str, Any]:
    """
    Validate and execute a read-only SQLite SQL query safely.

    Args:
        sql: Input SQL statement string.
        max_rows: Maximum number of rows to return before truncating.

    Returns:
        Structured dictionary: {
            "columns": List[str],
            "rows": List[Dict[str, Any]],
            "row_count": int,
            "truncated": bool,
            "error": str or None
        }
    """
    # Step 1: Validate SQL safety and schema
    val_res = validate_sql(sql)
    if not val_res["valid"]:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "truncated": False,
            "error": val_res["error"]
        }

    validated_sql = val_res["sql"]
    conn = None

    try:
        # Step 2: Connect to SQLite database using reusable module
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Step 3: Execute query
        cursor.execute(validated_sql)

        # Extract column names from description
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        # Fetch up to max_rows + 1 to detect truncation
        raw_rows = cursor.fetchmany(max_rows + 1)
        truncated = len(raw_rows) > max_rows
        actual_rows = raw_rows[:max_rows] if truncated else raw_rows

        # Convert sqlite3.Row objects to standard Python dicts
        dict_rows = [dict(row) for row in actual_rows]

        return {
            "columns": columns,
            "rows": dict_rows,
            "row_count": len(dict_rows),
            "truncated": truncated,
            "error": None
        }

    except Exception as e:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "truncated": False,
            "error": f"Execution error: {str(e)}"
        }

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    test_sql = "SELECT department_name, budget FROM departments ORDER BY budget DESC;"
    res = execute_safe_query(test_sql)
    print("Execution Result Columns:", res["columns"])
    print("Row Count:", res["row_count"])
    print("Truncated:", res["truncated"])
    print("Sample Row:", res["rows"][0] if res["rows"] else None)
