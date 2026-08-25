"""
API Integration Tests for FastAPI Backend End-to-End Workflow Integration.
Mocks run_query_workflow to test response serialization, input validation, error handling, and status codes.
"""

import os
import sys
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app

client = TestClient(app)


class TestAPIEndpoints(unittest.TestCase):

    def test_01_health_check_success(self):
        """Test GET /health returns HTTP 200 and healthy database status."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")

    @patch("backend.api.routes.query.run_query_workflow")
    def test_02_post_query_successful_workflow(self, mock_workflow):
        """Test POST /query returns HTTP 200 with status='success', answer, data, and SQL."""
        mock_workflow.return_value = {
            "question": "How many employees are currently on leave?",
            "schema_context": [{"id": "chunk_guide_employees_on_leave"}],
            "generated_sql": "SELECT COUNT(*) AS employees_on_leave FROM employees WHERE employment_status = 'On Leave';",
            "validated_sql": "SELECT COUNT(*) AS employees_on_leave FROM employees WHERE employment_status = 'On Leave';",
            "query_result": {
                "columns": ["employees_on_leave"],
                "rows": [{"employees_on_leave": 50}],
                "row_count": 1,
                "truncated": False,
                "error": None
            },
            "answer": "There are 50 employees currently on leave.",
            "error": None,
            "current_step": "answer_generated"
        }

        payload = {"question": "How many employees are currently on leave?"}
        response = client.post("/query", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["question"], "How many employees are currently on leave?")
        self.assertEqual(data["answer"], "There are 50 employees currently on leave.")
        self.assertEqual(data["data"], [{"employees_on_leave": 50}])
        self.assertEqual(data["row_count"], 1)
        self.assertEqual(
            data["generated_sql"],
            "SELECT COUNT(*) AS employees_on_leave FROM employees WHERE employment_status = 'On Leave';"
        )
        self.assertIsNone(data["error"])
        # Ensure internal state fields are NOT exposed
        self.assertNotIn("schema_context", data)
        self.assertNotIn("current_step", data)

    def test_03_post_query_empty_question_returns_400(self):
        """Test empty question returns HTTP 400."""
        payload = {"question": ""}
        response = client.post("/query", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Question cannot be empty", data["detail"])

    def test_04_post_query_whitespace_question_returns_400(self):
        """Test whitespace question returns HTTP 400."""
        payload = {"question": "   \n\t  "}
        response = client.post("/query", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Question cannot be empty", data["detail"])

    def test_05_post_query_missing_question_body_returns_422(self):
        """Test missing question key returns Pydantic validation HTTP 422."""
        payload = {"invalid_field": "text"}
        response = client.post("/query", json=payload)
        self.assertEqual(response.status_code, 422)

    @patch("backend.api.routes.query.run_query_workflow")
    def test_06_post_query_validation_failure_returns_200_error_status(self, mock_workflow):
        """Test workflow SQL validation failure returns HTTP 200 with status='error'."""
        mock_workflow.return_value = {
            "question": "Delete all records",
            "schema_context": [],
            "generated_sql": "DROP TABLE employees;",
            "validated_sql": None,
            "query_result": None,
            "answer": "Unable to process query: Only read-only SELECT or WITH statements are allowed.",
            "error": "Only read-only SELECT or WITH statements are allowed.",
            "current_step": "error_validation_failed"
        }

        payload = {"question": "Delete all records"}
        response = client.post("/query", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["error"], "Only read-only SELECT or WITH statements are allowed.")

    @patch("backend.api.routes.query.run_query_workflow")
    def test_07_post_query_execution_failure_returns_200_error_status(self, mock_workflow):
        """Test workflow execution failure returns HTTP 200 with status='error'."""
        mock_workflow.return_value = {
            "question": "Show fake col",
            "schema_context": [],
            "generated_sql": "SELECT fake_col FROM employees;",
            "validated_sql": "SELECT fake_col FROM employees;",
            "query_result": {"columns": [], "rows": [], "row_count": 0, "error": "no such column: fake_col"},
            "answer": "Unable to process query: Database validation error: no such column: fake_col",
            "error": "Database validation error: no such column: fake_col",
            "current_step": "error_execution_failed"
        }

        payload = {"question": "Show fake col"}
        response = client.post("/query", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("no such column", data["error"])

    @patch("backend.api.routes.query.run_query_workflow")
    def test_08_post_query_unexpected_exception_returns_500(self, mock_workflow):
        """Test unexpected internal server exception returns safe HTTP 500 without stack trace leakage."""
        mock_workflow.side_effect = RuntimeError("Fatal internal crash")

        payload = {"question": "How many employees?"}
        response = client.post("/query", json=payload)

        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["detail"], "An internal error occurred while processing the query.")
        self.assertNotIn("Fatal internal crash", str(data))


if __name__ == "__main__":
    unittest.main()
