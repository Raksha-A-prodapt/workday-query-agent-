"""
Unit and Integration Tests for LangGraph Workflow Orchestration.
Mocks LLM calls to test node execution order, conditional routing, error termination, fallback handling,
and prevention of duplicate RAG retrieval.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.connection import get_db_connection
from backend.workflow.graph import run_query_workflow, get_workflow_mermaid


class TestWorkflowOrchestration(unittest.TestCase):

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
        """Record baseline database counts."""
        self.baseline_counts = self.get_row_counts()

    def tearDown(self):
        """Verify database integrity and immutability after each test."""
        current_counts = self.get_row_counts()
        self.assertEqual(
            current_counts, self.baseline_counts,
            f"Database mutated! Baseline: {self.baseline_counts}, Current: {current_counts}"
        )

    @patch("backend.sql.generator.generate_completion")
    @patch("backend.services.answer_generator.generate_completion")
    def test_01_successful_complete_workflow(self, mock_answer_llm, mock_sql_llm):
        """Test full successful workflow execution from RAG to Answer Generation."""
        mock_sql_llm.return_value = "SELECT COUNT(*) AS active_headcount FROM employees WHERE employment_status = 'Active';"
        mock_answer_llm.return_value = "There are 425 active employees."

        question = "How many employees are there?"
        res = run_query_workflow(question)

        self.assertEqual(res["question"], question)
        self.assertIsNotNone(res["validated_sql"])
        self.assertEqual(res["query_result"]["row_count"], 1)
        self.assertEqual(res["answer"], "There are 425 active employees.")
        self.assertIsNone(res["error"])
        self.assertEqual(res["current_step"], "answer_generated")

    @patch("backend.workflow.nodes.retrieve_schema_context")
    def test_02_context_retrieval_failure_handling(self, mock_rag):
        """Test RAG retrieval exception is caught safely without crashing workflow."""
        mock_rag.side_effect = RuntimeError("ChromaDB storage error")

        res = run_query_workflow("How many employees are there?")

        self.assertIsNotNone(res["error"])
        self.assertIn("Schema retrieval failed", res["error"])
        self.assertIn("error", res["current_step"])

    @patch("backend.sql.generator.generate_completion")
    def test_03_sql_generation_failure_handling(self, mock_sql_llm):
        """Test LLM SQL generation failure sets error state and routes cleanly."""
        mock_sql_llm.side_effect = ValueError("LLM API Key is missing.")

        res = run_query_workflow("Show salary by department.")

        self.assertIsNotNone(res["error"])
        self.assertIn("LLM API Key is missing", res["error"])
        self.assertIsNone(res["validated_sql"])
        self.assertIn("error", res["current_step"])

    @patch("backend.sql.generator.generate_completion")
    def test_04_validation_failure_blocks_execution(self, mock_sql_llm):
        """Test invalid/unsafe generated SQL is caught by validator and stops execution."""
        mock_sql_llm.return_value = "DROP TABLE employees;"

        with patch("backend.workflow.nodes.execute_safe_query") as mock_exec:
            res = run_query_workflow("Delete all employees.")

            # Executor must NEVER be called if validation fails
            mock_exec.assert_not_called()
            self.assertIsNotNone(res["error"])
            self.assertIn("error", res["current_step"])
            self.assertIsNone(res["validated_sql"])

    @patch("backend.sql.generator.generate_completion")
    @patch("backend.workflow.nodes.execute_safe_query")
    def test_05_execution_failure_stops_answer_generation(self, mock_exec, mock_sql_llm):
        """Test DB execution failure routes to error handler and stops normal answer generation."""
        mock_sql_llm.return_value = "SELECT non_existent_col FROM employees;"
        mock_exec.return_value = {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "truncated": False,
            "error": "Database error: no such column: non_existent_col"
        }

        with patch("backend.services.answer_generator.generate_completion") as mock_answer_llm:
            res = run_query_workflow("Show non existent column.")

            mock_answer_llm.assert_not_called()
            self.assertIsNotNone(res["error"])
            self.assertIn("no such column", res["error"])
            self.assertIn("error", res["current_step"])

    @patch("backend.sql.generator.generate_completion")
    @patch("backend.services.answer_generator.generate_completion")
    def test_06_answer_generation_failure_uses_fallback(self, mock_answer_llm, mock_sql_llm):
        """Test answer LLM failure uses accurate deterministic fallback."""
        mock_sql_llm.return_value = "SELECT COUNT(*) AS total FROM employees WHERE employment_status = 'On Leave';"
        mock_answer_llm.side_effect = RuntimeError("Answer LLM timeout")

        res = run_query_workflow("How many employees are currently on leave?")

        self.assertIsNotNone(res["query_result"])
        self.assertEqual(res["query_result"]["row_count"], 1)
        self.assertIn("50", res["answer"])
        self.assertEqual(res["current_step"], "answer_generated")

    @patch("backend.sql.generator.generate_completion")
    @patch("backend.services.answer_generator.generate_completion")
    @patch("backend.workflow.nodes.retrieve_schema_context")
    def test_07_no_duplicate_rag_retrieval(self, mock_rag, mock_answer_llm, mock_sql_llm):
        """Test schema context is retrieved exactly ONCE per workflow execution."""
        mock_rag.return_value = [
            {"id": "chunk_table_employees", "content": "Employees schema", "metadata": {"section": "employees"}}
        ]
        mock_sql_llm.return_value = "SELECT COUNT(*) FROM employees;"
        mock_answer_llm.return_value = "There are 500 total employees."

        run_query_workflow("How many total employees?")

        # Assert retrieve_schema_context was called exactly ONCE
        self.assertEqual(mock_rag.call_count, 1)

    def test_08_mermaid_workflow_visualization(self):
        """Test Mermaid workflow diagram string representation is returned."""
        mermaid = get_workflow_mermaid()
        self.assertIn("graph TD", mermaid)
        self.assertIn("retrieve_context", mermaid)
        self.assertIn("validate_sql", mermaid)
        self.assertIn("execute_sql", mermaid)


if __name__ == "__main__":
    unittest.main()
