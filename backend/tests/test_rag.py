"""
Unit and Integration Tests for Schema RAG Implementation.
Tests data dictionary ingestion, ChromaDB persistence, deduplication, and schema retrieval across 8+ HR queries.
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.rag.ingest import ingest_data_dictionary
from backend.rag.retriever import retrieve_schema_context, get_chroma_collection


class TestSchemaRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure ChromaDB collection is initialized before testing."""
        cls.collection = get_chroma_collection()

    def test_01_ingest_data_dictionary_success(self):
        """Test data dictionary ingestion returns 12 distinct chunks."""
        count = ingest_data_dictionary()
        self.assertEqual(count, 12)

    def test_02_chromadb_collection_created_and_count(self):
        """Test ChromaDB collection exists and contains exactly 12 items."""
        collection = get_chroma_collection()
        self.assertEqual(collection.count(), 12)

    def test_03_reingestion_deduplication(self):
        """Test running ingestion multiple times does not duplicate entries."""
        ingest_data_dictionary()
        ingest_data_dictionary()
        collection = get_chroma_collection()
        self.assertEqual(collection.count(), 12)

    def test_04_retrieve_headcount_question(self):
        """Test headcount query retrieves employee/headcount schema."""
        results = retrieve_schema_context("How many employees are there?", top_k=3)
        self.assertGreater(len(results), 0)
        retrieved_ids = [r["id"] for r in results]
        self.assertTrue(
            "chunk_guide_headcount" in retrieved_ids or "chunk_table_employees" in retrieved_ids
        )

    def test_05_retrieve_department_question(self):
        """Test department query retrieves department or employee relationships."""
        results = retrieve_schema_context("Show employees by department.", top_k=3)
        self.assertGreater(len(results), 0)
        retrieved_sections = [r["metadata"].get("section") for r in results]
        self.assertTrue(
            "departments" in retrieved_sections or "employee_headcount" in retrieved_sections or "salary_analytics" in retrieved_sections
        )

    def test_06_retrieve_leave_question(self):
        """Test leave query retrieves leave-related business rules."""
        results = retrieve_schema_context("How many employees are currently on leave?", top_k=3)
        self.assertGreater(len(results), 0)
        retrieved_ids = [r["id"] for r in results]
        self.assertTrue(
            "chunk_guide_employees_on_leave" in retrieved_ids or "chunk_guide_leave_analytics" in retrieved_ids
        )

    def test_07_retrieve_salary_question(self):
        """Test salary query retrieves salary analytics schema."""
        results = retrieve_schema_context("What is the average salary by department?", top_k=3)
        self.assertGreater(len(results), 0)
        retrieved_ids = [r["id"] for r in results]
        self.assertIn("chunk_guide_salary", retrieved_ids)

    def test_08_retrieve_job_opening_question(self):
        """Test job opening query retrieves job requisition schema."""
        results = retrieve_schema_context("How many open job positions are there?", top_k=3)
        self.assertGreater(len(results), 0)
        retrieved_ids = [r["id"] for r in results]
        self.assertTrue(
            "chunk_guide_job_openings" in retrieved_ids or "chunk_table_job_openings" in retrieved_ids
        )

    def test_09_retrieve_time_to_fill_question(self):
        """Test time-to-fill query retrieves job opening analytics."""
        results = retrieve_schema_context("What is the average time to fill a role?", top_k=3)
        self.assertGreater(len(results), 0)
        retrieved_ids = [r["id"] for r in results]
        self.assertIn("chunk_guide_job_openings", retrieved_ids)

    def test_10_retrieve_empty_or_invalid_question(self):
        """Test empty question returns empty list safely."""
        self.assertEqual(retrieve_schema_context(""), [])
        self.assertEqual(retrieve_schema_context("   \t\n  "), [])
        self.assertEqual(retrieve_schema_context(None), [])

    def test_11_structured_result_fields(self):
        """Test retrieved output dictionary structure contains required keys."""
        results = retrieve_schema_context("Show employees reporting to a manager.", top_k=2)
        self.assertGreater(len(results), 0)
        first = results[0]
        self.assertIn("id", first)
        self.assertIn("content", first)
        self.assertIn("metadata", first)
        self.assertIn("distance", first)
        self.assertIsInstance(first["metadata"], dict)
        self.assertIn("section", first["metadata"])
        self.assertIn("type", first["metadata"])


if __name__ == "__main__":
    unittest.main()
