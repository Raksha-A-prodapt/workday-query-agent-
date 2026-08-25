"""
SQL Generator Module.
Retrieves schema context via RAG (or reuses provided context), formats prompts, and calls LLM service to generate SQLite SQL.
"""

import os
import sys
import re
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.rag.retriever import retrieve_schema_context
from backend.sql.prompts import SQL_SYSTEM_PROMPT, build_sql_prompt
from backend.services.llm import generate_completion


def clean_generated_sql(raw_sql: str) -> str:
    """
    Clean up raw LLM response by stripping markdown code fences, preambles, and extra whitespace.
    """
    if not raw_sql or not isinstance(raw_sql, str):
        return ""

    text = raw_sql.strip()

    # Remove Markdown code blocks ```sql ... ``` or ``` ... ```
    code_block_match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()

    # Remove common leading conversational preambles
    text = re.sub(r"^(?:here\s+is\s+(?:the\s+)?(?:sql\s+)?(?:query|statement)?:\s*|sql:\s*)", "", text, flags=re.IGNORECASE).strip()

    # Remove inline backticks if any remain around single statement
    if text.startswith("`") and text.endswith("`"):
        text = text.strip("`").strip()

    return text


def generate_sql(question: str, schema_context: Optional[List[Dict[str, Any]]] = None, top_k: int = 4) -> Dict[str, Any]:
    """
    Generate SQLite SQL from a natural language HR question using Schema RAG.

    Args:
        question: User query string.
        schema_context: Optional pre-retrieved schema context list to prevent duplicate retrieval.
        top_k: Number of schema context chunks to retrieve if schema_context is None.

    Returns:
        Structured dictionary containing question, sql, schema_context, and error.
    """
    if not question or not isinstance(question, str) or not question.strip():
        return {
            "question": question or "",
            "sql": None,
            "schema_context": [],
            "error": "Question cannot be empty."
        }

    cleaned_question = question.strip()

    try:
        # Step 1: Retrieve schema context via RAG only if not already provided
        if schema_context is not None:
            chunks = schema_context
        else:
            chunks = retrieve_schema_context(cleaned_question, top_k=top_k)

        # Step 2: Build prompt
        user_prompt = build_sql_prompt(cleaned_question, chunks)

        # Step 3: Call LLM service
        raw_response = generate_completion(user_prompt, system_prompt=SQL_SYSTEM_PROMPT)

        # Step 4: Clean output
        cleaned_sql = clean_generated_sql(raw_response)

        if not cleaned_sql:
            return {
                "question": cleaned_question,
                "sql": None,
                "schema_context": chunks,
                "error": "LLM returned an empty SQL string."
            }

        return {
            "question": cleaned_question,
            "sql": cleaned_sql,
            "schema_context": chunks,
            "error": None
        }

    except Exception as e:
        return {
            "question": cleaned_question,
            "sql": None,
            "schema_context": schema_context or [],
            "error": str(e)
        }


if __name__ == "__main__":
    test_q = "How many employees are currently on leave by region?"
    print(f"Testing generate_sql() structure for: '{test_q}'")
    res = generate_sql(test_q)
    print("Result keys:", list(res.keys()))
    print("Error:", res["error"])
    print("SQL:", res["sql"])
