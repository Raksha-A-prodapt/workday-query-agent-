"""
Unit and Integration Tests for Human-Readable Answer Generator Module.
Tests prompt assembly, numeric accuracy preservation, empty result handling, LLM mocks,
fallback formatting, DB isolation, and controlled end-to-end pipeline compatibility.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.answer_generator import format_fallback_answer, generate_answer
from backend.sql.executor import execute_safe_query
from backend.sql.generator import generate_sql


class TestAnswerGenerator(unittest.TestCase):

    def test_01_empty_result_returns_no_records_without_calling_llm(self):
        """Test empty query results return immediate 'No matching records were found' without calling LLM."""
        empty_res = {"columns": ["employee_name"], "rows": [], "row_count": 0, "truncated": False, "error": None}

        with patch("backend.services.answer_generator.generate_completion") as mock_llm:
            res = generate_answer("Show employees in fictional dept", empty_res)
            mock_llm.assert_not_called()
            self.assertEqual(res["answer"], "No matching records were found.")
            self.assertEqual(res["row_count"], 0)
            self.assertEqual(res["data"], [])
            self.assertIsNone(res["error"])

    @patch("backend.services.answer_generator.generate_completion")
    def test_02_single_aggregate_result_success(self, mock_llm):
        """Test single aggregate count result is converted to natural language answer."""
        mock_llm.return_value = "There are 425 active employees."
        headcount_res = {
            "columns": ["active_headcount"],
            "rows": [{"active_headcount": 425}],
            "row_count": 1,
            "truncated": False,
            "error": None
        }

        res = generate_answer("How many employees are there?", headcount_res)

        mock_llm.assert_called_once()
        self.assertEqual(res["answer"], "There are 425 active employees.")
        self.assertEqual(res["row_count"], 1)
        self.assertEqual(res["data"], [{"active_headcount": 425}])
        self.assertIsNone(res["error"])

    @patch("backend.services.answer_generator.generate_completion")
    def test_03_multiple_grouped_results_success(self, mock_llm):
        """Test multiple department salary rows are converted to clear answer."""
        mock_llm.return_value = "The average salary for Engineering is $102,791.05 and for Sales is $95,000.00."
        salary_res = {
            "columns": ["department_name", "avg_salary"],
            "rows": [
                {"department_name": "Engineering", "avg_salary": 102791.05},
                {"department_name": "Sales", "avg_salary": 95000.00}
            ],
            "row_count": 2,
            "truncated": False,
            "error": None
        }

        res = generate_answer("What is the average salary by department?", salary_res)

        self.assertEqual(res["row_count"], 2)
        self.assertIn("Engineering", res["answer"])
        self.assertIsNone(res["error"])

    @patch("backend.services.answer_generator.generate_completion")
    def test_04_llm_receives_question_and_structured_data(self, mock_llm):
        """Test LLM prompt receives original question and structured result data."""
        mock_llm.return_value = "50 employees are currently on leave."
        leave_res = {
            "columns": ["employees_on_leave"],
            "rows": [{"employees_on_leave": 50}],
            "row_count": 1,
            "truncated": False,
            "error": None
        }

        generate_answer("How many employees are currently on leave?", leave_res)

        args, kwargs = mock_llm.call_args
        prompt_text = args[0]
        self.assertIn("How many employees are currently on leave?", prompt_text)
        self.assertIn("employees_on_leave", prompt_text)
        self.assertIn("50", prompt_text)

    def test_05_missing_llm_configuration_triggers_fallback(self):
        """Test missing API key triggers accurate deterministic fallback without crashing."""
        headcount_res = {
            "columns": ["active_headcount"],
            "rows": [{"active_headcount": 425}],
            "row_count": 1,
            "truncated": False,
            "error": None
        }

        with patch("backend.services.answer_generator.generate_completion") as mock_llm:
            mock_llm.side_effect = ValueError("LLM API Key is missing.")
            res = generate_answer("How many employees are there?", headcount_res)

            self.assertEqual(res["answer"], "There are 425 active employees.")
            self.assertIsNotNone(res["error"])
            self.assertEqual(res["row_count"], 1)

    def test_06_llm_error_triggers_fallback(self):
        """Test LLM runtime connection exception triggers deterministic fallback."""
        dept_res = {
            "columns": ["department_name", "headcount"],
            "rows": [
                {"department_name": "Engineering", "headcount": 53},
                {"department_name": "Sales", "headcount": 45}
            ],
            "row_count": 2,
            "truncated": False,
            "error": None
        }

        with patch("backend.services.answer_generator.generate_completion") as mock_llm:
            mock_llm.side_effect = RuntimeError("OpenAI API unreachable.")
            res = generate_answer("Show employee count by department.", dept_res)

            self.assertIn("Query returned 2 records", res["answer"])
            self.assertIn("Engineering: 53", res["answer"])
            self.assertIsNotNone(res["error"])

    def test_07_malformed_llm_response_triggers_fallback(self):
        """Test empty/whitespace response from LLM triggers fallback."""
        headcount_res = {
            "columns": ["active_headcount"],
            "rows": [{"active_headcount": 425}],
            "row_count": 1,
            "truncated": False,
            "error": None
        }

        with patch("backend.services.answer_generator.generate_completion") as mock_llm:
            mock_llm.return_value = "   \n  "
            res = generate_answer("How many employees are there?", headcount_res)

            self.assertEqual(res["answer"], "There are 425 active employees.")
            self.assertIn("fallback used", res["error"])

    def test_08_answer_generator_does_not_execute_sql(self):
        """Test generate_answer does not call database connection or execute SQL."""
        sample_res = {
            "columns": ["open_jobs"],
            "rows": [{"open_jobs": 20}],
            "row_count": 1,
            "truncated": False,
            "error": None
        }

        with patch("sqlite3.connect") as mock_db_connect:
            with patch("backend.services.answer_generator.generate_completion") as mock_llm:
                mock_llm.return_value = "There are 20 open job positions."
                generate_answer("How many open job positions are there?", sample_res)
                mock_db_connect.assert_not_called()

    def test_09_structured_output_fields(self):
        """Test output dictionary contains answer, data, row_count, and error keys."""
        sample_res = {
            "columns": ["open_jobs"],
            "rows": [{"open_jobs": 20}],
            "row_count": 1,
            "truncated": False,
            "error": None
        }

        with patch("backend.services.answer_generator.generate_completion") as mock_llm:
            mock_llm.return_value = "There are 20 open job positions."
            res = generate_answer("How many open job positions are there?", sample_res)

            self.assertIn("answer", res)
            self.assertIn("data", res)
            self.assertIn("row_count", res)
            self.assertIn("error", res)

    @patch("backend.sql.generator.retrieve_schema_context")
    @patch("backend.sql.generator.generate_completion")
    @patch("backend.services.answer_generator.generate_completion")
    def test_10_controlled_full_pipeline_integration(self, mock_answer_llm, mock_sql_llm, mock_rag):
        """Test Question -> SQL Gen -> Validation -> Execution -> Answer Gen full pipeline."""
        mock_rag.return_value = [
            {"id": "chunk_table_departments", "content": "Departments table", "metadata": {"section": "departments"}}
        ]
        mock_sql_llm.return_value = "SELECT department_name, budget FROM departments ORDER BY budget DESC;"
        mock_answer_llm.return_value = "Engineering has the highest budget at $12,000,000.00."

        question = "Show departments by budget."

        # Step 1: SQL Generation
        sql_gen_res = generate_sql(question)
        self.assertIsNone(sql_gen_res["error"])

        # Step 2 & 3: Validation and Execution
        exec_res = execute_safe_query(sql_gen_res["sql"])
        self.assertIsNone(exec_res["error"])
        self.assertEqual(exec_res["row_count"], 8)

        # Step 4: Answer Generation
        answer_res = generate_answer(question, exec_res)
        self.assertIsNone(answer_res["error"])
        self.assertEqual(answer_res["answer"], "Engineering has the highest budget at $12,000,000.00.")
        self.assertEqual(len(answer_res["data"]), 8)


if __name__ == "__main__":
    unittest.main()
