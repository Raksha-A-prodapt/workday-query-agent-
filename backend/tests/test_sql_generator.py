"""
Unit Tests for SQL Generator Module.
Mocks LLM service to test RAG retrieval integration, prompt construction, SQL cleaning, and error handling.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.sql.generator import clean_generated_sql, generate_sql


class TestSQLGenerator(unittest.TestCase):

    def test_01_empty_question_handling(self):
        """Test empty or whitespace questions are rejected safely."""
        res1 = generate_sql("")
        self.assertIsNotNone(res1["error"])
        self.assertIsNone(res1["sql"])
        self.assertEqual(res1["schema_context"], [])

        res2 = generate_sql("   \t\n  ")
        self.assertIsNotNone(res2["error"])
        self.assertIsNone(res2["sql"])

    def test_02_clean_generated_sql_formatting(self):
        """Test markdown code fence and preamble stripping."""
        raw_markdown = "```sql\nSELECT COUNT(*) FROM employees;\n```"
        cleaned = clean_generated_sql(raw_markdown)
        self.assertEqual(cleaned, "SELECT COUNT(*) FROM employees;")

        raw_preamble = "Here is the SQL query:\nSELECT * FROM regions;"
        cleaned_preamble = clean_generated_sql(raw_preamble)
        self.assertEqual(cleaned_preamble, "SELECT * FROM regions;")

        raw_backticks = "`SELECT 1;`"
        self.assertEqual(clean_generated_sql(raw_backticks), "SELECT 1;")

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    def test_03_mock_employee_headcount_sql(self, mock_llm, mock_rag):
        """Test employee headcount query generates expected mocked SQL."""
        mock_rag.return_value = [
            {"id": "chunk_guide_headcount", "content": "Headcount rules", "metadata": {"section": "employee_headcount"}}
        ]
        mock_llm.return_value = "SELECT COUNT(*) FROM employees WHERE employment_status = 'Active';"

        res = generate_sql("How many employees are there?")

        self.assertEqual(res["question"], "How many employees are there?")
        self.assertEqual(res["sql"], "SELECT COUNT(*) FROM employees WHERE employment_status = 'Active';")
        self.assertIsNone(res["error"])
        self.assertEqual(len(res["schema_context"]), 1)
        mock_rag.assert_called_once()
        mock_llm.assert_called_once()

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    def test_04_mock_department_join_sql(self, mock_llm, mock_rag):
        """Test department query produces SQL containing expected JOIN departments."""
        mock_rag.return_value = [
            {"id": "chunk_table_departments", "content": "Departments table", "metadata": {"section": "departments"}}
        ]
        mock_llm.return_value = (
            "SELECT d.department_name, COUNT(e.employee_id) FROM employees e "
            "JOIN departments d ON e.department_id = d.department_id GROUP BY d.department_name;"
        )

        res = generate_sql("Show employee count by department.")

        self.assertIsNotNone(res["sql"])
        self.assertIn("JOIN departments", res["sql"])
        self.assertIsNone(res["error"])

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    def test_05_mock_leave_records_sql(self, mock_llm, mock_rag):
        """Test leave query produces SQL referencing leave tables."""
        mock_rag.return_value = [
            {"id": "chunk_guide_employees_on_leave", "content": "On leave rules", "metadata": {"section": "employees_on_leave"}}
        ]
        mock_llm.return_value = "SELECT COUNT(*) FROM employees WHERE employment_status = 'On Leave';"

        res = generate_sql("How many employees are currently on leave?")

        self.assertIsNotNone(res["sql"])
        self.assertIn("On Leave", res["sql"])
        self.assertIsNone(res["error"])

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    def test_06_llm_error_handling(self, mock_llm, mock_rag):
        """Test LLM service exception is caught and returned as structured error."""
        mock_rag.return_value = []
        mock_llm.side_effect = ValueError("LLM API key is missing.")

        res = generate_sql("What is the average salary?")

        self.assertIsNone(res["sql"])
        self.assertIsNotNone(res["error"])
        self.assertIn("LLM API key is missing", res["error"])

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    def test_07_empty_llm_response_handling(self, mock_llm, mock_rag):
        """Test empty string returned from LLM is handled safely."""
        mock_rag.return_value = []
        mock_llm.return_value = "   "

        res = generate_sql("How many open job positions are there?")

        self.assertIsNone(res["sql"])
        self.assertIsNotNone(res["error"])
        self.assertIn("LLM returned an empty SQL string", res["error"])


if __name__ == "__main__":
    unittest.main()
