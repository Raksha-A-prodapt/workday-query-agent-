"""
Unit Tests for SQL Validator Module.
Verifies read-only rules, keyword blocklists, comment stripping, multi-statement blocking, and schema validation.
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.sql.validator import validate_sql, strip_sql_comments


class TestSQLValidator(unittest.TestCase):

    def test_01_valid_simple_select(self):
        """Test valid simple SELECT query is accepted."""
        res = validate_sql("SELECT COUNT(*) FROM employees;")
        self.assertTrue(res["valid"])
        self.assertIsNone(res["error"])
        self.assertTrue(res["sql"].endswith(";"))

    def test_02_valid_select_with_join(self):
        """Test valid SELECT query with JOIN is accepted."""
        sql = """
        SELECT d.department_name, COUNT(e.employee_id) AS total
        FROM departments d
        JOIN employees e ON d.department_id = e.department_id
        GROUP BY d.department_id, d.department_name;
        """
        res = validate_sql(sql)
        self.assertTrue(res["valid"])
        self.assertIsNone(res["error"])

    def test_03_valid_select_with_aggregation(self):
        """Test valid SELECT query with aggregate functions (AVG, SUM, ROUND, julianday) is accepted."""
        sql = """
        SELECT d.department_name, ROUND(AVG(julianday(j.closed_date) - julianday(j.posted_date)), 1) AS avg_days
        FROM job_openings j
        JOIN departments d ON j.department_id = d.department_id
        WHERE j.job_status = 'Filled' AND j.closed_date IS NOT NULL
        GROUP BY d.department_id, d.department_name;
        """
        res = validate_sql(sql)
        self.assertTrue(res["valid"])

    def test_04_insert_rejected(self):
        """Test INSERT statement is rejected."""
        res = validate_sql("INSERT INTO regions (region_name, country) VALUES ('Test', 'TestCountry');")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_05_update_rejected(self):
        """Test UPDATE statement is rejected."""
        res = validate_sql("UPDATE employees SET salary = 200000 WHERE employee_id = 1;")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_06_delete_rejected(self):
        """Test DELETE statement is rejected."""
        res = validate_sql("DELETE FROM leave_records WHERE leave_id = 1;")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_07_drop_rejected(self):
        """Test DROP statement is rejected."""
        res = validate_sql("DROP TABLE employees;")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_08_create_rejected(self):
        """Test CREATE statement is rejected."""
        res = validate_sql("CREATE TABLE hack (id INT);")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_09_pragma_rejected(self):
        """Test PRAGMA statement is rejected."""
        res = validate_sql("PRAGMA foreign_keys = OFF;")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_10_multiple_statements_rejected(self):
        """Test multiple statements separated by semicolon are rejected."""
        res = validate_sql("SELECT COUNT(*) FROM employees; DROP TABLE employees;")
        self.assertFalse(res["valid"])
        self.assertIn("Multiple SQL statements", res["error"])

    def test_11_empty_sql_rejected(self):
        """Test empty SQL input is rejected safely."""
        self.assertFalse(validate_sql("")["valid"])
        self.assertFalse(validate_sql("   \t\n ")["valid"])
        self.assertFalse(validate_sql(None)["valid"])

    def test_12_sql_comments_cannot_bypass_validation(self):
        """Test SQL comments do not bypass mutation keyword checks."""
        sql = "-- comment \n DROP TABLE employees;"
        res = validate_sql(sql)
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_13_mixed_case_forbidden_keywords_rejected(self):
        """Test mixed-case forbidden keywords are rejected."""
        res = validate_sql("SeLeCt * FrOm employees; DeLeTe FrOm employees;")
        self.assertFalse(res["valid"])

    def test_14_nonexistent_table_rejected(self):
        """Test nonexistent table is caught during database schema validation."""
        res = validate_sql("SELECT * FROM non_existent_dummy_table;")
        self.assertFalse(res["valid"])
        self.assertIn("Database validation error", res["error"])

    def test_16_valid_union_all_with_subqueries(self):
        """Test UNION ALL wrapped in subqueries is accepted by SQLite validator."""
        sql = """
        SELECT * FROM (
            SELECT employee_id, COUNT(leave_id) AS leave_count FROM leave_records GROUP BY employee_id ORDER BY leave_count DESC LIMIT 1
        ) UNION ALL SELECT * FROM (
            SELECT employee_id, COUNT(leave_id) AS leave_count FROM leave_records GROUP BY employee_id ORDER BY leave_count ASC LIMIT 1
        );
        """
        res = validate_sql(sql)
        self.assertTrue(res["valid"])
        self.assertIsNone(res["error"])

    def test_17_invalid_union_all_without_subqueries_rejected(self):
        """Test un-parenthesized ORDER BY before UNION ALL is caught and rejected by database validator."""
        sql = """
        SELECT employee_id, COUNT(leave_id) AS leave_count FROM leave_records GROUP BY employee_id ORDER BY leave_count DESC LIMIT 1
        UNION ALL
        SELECT employee_id, COUNT(leave_id) AS leave_count FROM leave_records GROUP BY employee_id ORDER BY leave_count ASC LIMIT 1;
        """
        res = validate_sql(sql)
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])
        self.assertIn("ORDER BY clause should come after UNION ALL not before", res["error"])


if __name__ == "__main__":
    unittest.main()

