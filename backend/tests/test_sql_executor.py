"""
Unit and Integration Tests for Safe SQL Executor Module.
Tests query execution, result dict formatting, row limiting/truncation, error handling,
database immutability, and controlled RAG -> SQL -> Validation -> Execution pipeline.
"""

import os
import sys
import sqlite3
import unittest
from unittest.mock import patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.connection import get_db_connection
from backend.sql.executor import execute_safe_query
from backend.sql.generator import generate_sql


class TestSQLExecutor(unittest.TestCase):

    def get_row_counts(self):
        """Get baseline counts for all tables."""
        conn = get_db_connection()
        cursor = conn.cursor()
        counts = {}
        for table in ["regions", "departments", "employees", "leave_records", "job_openings"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        conn.close()
        return counts

    def setUp(self):
        """Record baseline row counts before each test."""
        self.baseline_counts = self.get_row_counts()

    def tearDown(self):
        """Verify database data remains completely unchanged after each test."""
        current_counts = self.get_row_counts()
        self.assertEqual(
            current_counts, self.baseline_counts,
            f"Database mutated! Baseline: {self.baseline_counts}, Current: {current_counts}"
        )

    def test_01_valid_count_query_executes(self):
        """Test valid COUNT query executes and returns correct structure."""
        sql = "SELECT COUNT(*) AS total_employees FROM employees;"
        res = execute_safe_query(sql)

        self.assertIsNone(res["error"])
        self.assertEqual(res["columns"], ["total_employees"])
        self.assertEqual(res["row_count"], 1)
        self.assertFalse(res["truncated"])
        self.assertGreaterEqual(res["rows"][0]["total_employees"], 500)

    def test_02_valid_join_query_executes(self):
        """Test valid JOIN query executes and returns formatted rows."""
        sql = """
        SELECT d.department_name, COUNT(e.employee_id) AS emp_count
        FROM departments d
        LEFT JOIN employees e ON d.department_id = e.department_id
        GROUP BY d.department_id, d.department_name
        ORDER BY emp_count DESC;
        """
        res = execute_safe_query(sql)

        self.assertIsNone(res["error"])
        self.assertEqual(res["columns"], ["department_name", "emp_count"])
        self.assertEqual(res["row_count"], 8)
        self.assertIsInstance(res["rows"][0], dict)
        self.assertIn("department_name", res["rows"][0])

    def test_03_result_columns_and_dicts(self):
        """Test result output dictionary format."""
        sql = "SELECT region_id, region_name, country FROM regions ORDER BY region_id;"
        res = execute_safe_query(sql)

        self.assertIsNone(res["error"])
        self.assertEqual(res["columns"], ["region_id", "region_name", "country"])
        self.assertEqual(res["row_count"], 6)
        self.assertEqual(res["rows"][0]["region_name"], "North America")

    def test_04_invalid_sql_handled_gracefully(self):
        """Test malformed SQL returns error string without crashing."""
        res = execute_safe_query("SELECT FROM WHERE WHERE;")
        self.assertIsNotNone(res["error"])
        self.assertEqual(res["row_count"], 0)

    def test_05_nonexistent_table_handled_safely(self):
        """Test nonexistent table is rejected safely."""
        res = execute_safe_query("SELECT * FROM non_existent_table;")
        self.assertIsNotNone(res["error"])
        self.assertIn("no such table", res["error"])

    def test_06_nonexistent_column_handled_safely(self):
        """Test nonexistent column is rejected safely."""
        res = execute_safe_query("SELECT fake_col FROM regions;")
        self.assertIsNotNone(res["error"])
        self.assertIn("no such column", res["error"])

    def test_07_unsafe_sql_rejected_before_execution(self):
        """Test DROP / INSERT statements are blocked before execution."""
        res_drop = execute_safe_query("DROP TABLE employees;")
        self.assertIsNotNone(res_drop["error"])

        res_insert = execute_safe_query("INSERT INTO regions (region_name, country) VALUES ('X', 'Y');")
        self.assertIsNotNone(res_insert["error"])

    def test_08_multiple_statements_rejected(self):
        """Test multi-statement injection attempt is blocked."""
        res = execute_safe_query("SELECT COUNT(*) FROM employees; DROP TABLE employees;")
        self.assertIsNotNone(res["error"])
        self.assertIn("Multiple SQL statements", res["error"])

    def test_09_row_limiting_and_truncation(self):
        """Test row limiting sets truncated flag when max_rows threshold is exceeded."""
        sql = "SELECT department_name FROM departments;"
        res = execute_safe_query(sql, max_rows=3)

        self.assertIsNone(res["error"])
        self.assertEqual(res["row_count"], 3)
        self.assertTrue(res["truncated"])

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    def test_10_controlled_pipeline_verification(self, mock_llm, mock_rag):
        """Test end-to-end question -> generate_sql -> validate -> execute pipeline."""
        mock_rag.return_value = [
            {"id": "chunk_table_departments", "content": "Departments table", "metadata": {"section": "departments"}}
        ]
        mock_llm.return_value = "SELECT department_name, budget FROM departments ORDER BY budget DESC;"

        question = "Show departments by budget."

        # Step A: Generate SQL
        gen_res = generate_sql(question)
        self.assertIsNone(gen_res["error"])
        sql = gen_res["sql"]

        # Step B: Execute safe query (which validates inside execute_safe_query)
        exec_res = execute_safe_query(sql)

        self.assertIsNone(exec_res["error"])
        self.assertEqual(exec_res["columns"], ["department_name", "budget"])
        self.assertEqual(exec_res["row_count"], 8)
        self.assertEqual(exec_res["rows"][0]["department_name"], "Engineering")


if __name__ == "__main__":
    unittest.main()
