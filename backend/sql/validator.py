"""
SQL Validator Module.
Enforces read-only SELECT rules, checks for forbidden mutation keywords, single-statement constraints,
and validates syntax/schema using SQLite EXPLAIN query planning.
"""

import os
import sys
import re
import sqlite3
from typing import Any, Dict

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.connection import get_db_connection

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE",
    "VACUUM", "ATTACH", "DETACH", "PRAGMA", "BEGIN", "COMMIT", "ROLLBACK",
    "TRANSACTION", "GRANT", "REVOKE", "EXEC", "EXECUTE", "EXPLAIN", "CALL",
    "TRUNCATE", "UPSERT", "IMPORT"
}


def strip_sql_comments(sql: str) -> str:
    """
    Strip single-line (-- ...) and multi-line (/* ... */) SQL comments.
    """
    if not sql:
        return ""
    # Remove multi-line comments
    sql = re.sub(r"/\*[\s\S]*?\*/", " ", sql)
    # Remove single-line comments
    lines = [re.sub(r"--.*$", "", line) for line in sql.splitlines()]
    return " ".join(lines).strip()


def validate_sql(sql: str) -> Dict[str, Any]:
    """
    Validate that generated SQL is a single, safe, read-only SQLite SELECT/WITH query
    and that all referenced tables and columns exist in the actual database.

    Args:
        sql: Input SQL string.

    Returns:
        Structured dictionary: {"valid": bool, "sql": str or None, "error": str or None}
    """
    if not sql or not isinstance(sql, str) or not sql.strip():
        return {
            "valid": False,
            "sql": None,
            "error": "SQL statement cannot be empty."
        }

    # Step 1: Strip comments and clean whitespace
    cleaned = strip_sql_comments(sql)
    if not cleaned:
        return {
            "valid": False,
            "sql": None,
            "error": "SQL statement contains only comments or whitespace."
        }

    # Step 2: Multi-statement check (split by semicolon)
    statements = [s.strip() for s in cleaned.split(";") if s.strip()]
    if len(statements) > 1:
        return {
            "valid": False,
            "sql": None,
            "error": "Multiple SQL statements are not allowed."
        }

    single_statement = statements[0]

    # Step 3: Must start with SELECT or WITH
    upper_stmt = single_statement.upper()
    if not (upper_stmt.startswith("SELECT") or upper_stmt.startswith("WITH")):
        return {
            "valid": False,
            "sql": None,
            "error": "Only read-only SELECT or WITH statements are allowed."
        }

    # Step 4: Token inspection for forbidden mutation keywords
    words = set(re.findall(r"\b[A-Z_]+\b", upper_stmt))
    found_forbidden = words.intersection(FORBIDDEN_KEYWORDS)

    # Allow WITH keyword if it's the start keyword
    if found_forbidden:
        forbidden_list = ", ".join(sorted(found_forbidden))
        return {
            "valid": False,
            "sql": None,
            "error": f"Forbidden keyword(s) detected: '{forbidden_list}'. Only read-only SELECT queries are allowed."
        }

    # Normalize trailing semicolon
    final_sql = single_statement + ";"

    # Step 5: Schema and syntax validation using SQLite EXPLAIN
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN {single_statement};")
        conn.close()
    except sqlite3.OperationalError as e:
        return {
            "valid": False,
            "sql": None,
            "error": f"Database validation error: {str(e)}"
        }
    except Exception as e:
        return {
            "valid": False,
            "sql": None,
            "error": f"Validation failed: {str(e)}"
        }

    return {
        "valid": True,
        "sql": final_sql,
        "error": None
    }


if __name__ == "__main__":
    valid_q = "SELECT department_name FROM departments;"
    print("Valid Q Test:", validate_sql(valid_q))

    invalid_q = "DROP TABLE employees;"
    print("Invalid Q Test:", validate_sql(invalid_q))

    multi_q = "SELECT 1; SELECT 2;"
    print("Multi Q Test:", validate_sql(multi_q))
