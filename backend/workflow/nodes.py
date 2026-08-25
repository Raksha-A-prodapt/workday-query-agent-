"""
LangGraph Workflow Nodes for Workday Data Query Agent.
Encapsulates individual execution steps: RAG retrieval, SQL generation, validation, safe execution, and answer synthesis.
"""

import os
import sys
from typing import Any, Dict

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.rag.retriever import retrieve_schema_context
from backend.sql.generator import generate_sql
from backend.sql.validator import validate_sql
from backend.sql.executor import execute_safe_query
from backend.services.answer_generator import generate_answer, format_fallback_answer
from backend.workflow.state import QueryState

try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator


@traceable(name="Retrieve Schema Context")
def retrieve_context_node(state: QueryState) -> Dict[str, Any]:

    """
    Node 1: Retrieve schema and business rules context using RAG.
    Reuses existing state['schema_context'] if already present to avoid redundant RAG calls.
    """
    try:
        existing_context = state.get("schema_context")
        if existing_context and len(existing_context) > 0:
            context = existing_context
        else:
            question = state.get("question", "")
            context = retrieve_schema_context(question, top_k=4)

        return {
            "schema_context": context,
            "current_step": "context_retrieved",
            "error": None
        }
    except Exception as e:
        return {
            "schema_context": [],
            "error": f"Schema retrieval failed: {str(e)}",
            "current_step": "retrieval_failed"
        }


@traceable(name="Generate SQL")
def generate_sql_node(state: QueryState) -> Dict[str, Any]:
    """
    Node 2: Generate SQLite SQL query using retrieved schema context.
    Passes pre-retrieved schema_context to generate_sql to avoid duplicate retrieval.
    """
    if state.get("error"):
        return {"current_step": "sql_generation_bypassed"}

    try:
        question = state.get("question", "")
        schema_context = state.get("schema_context", [])

        res = generate_sql(question, schema_context=schema_context)
        if res.get("error"):
            return {
                "generated_sql": None,
                "error": res["error"],
                "current_step": "sql_generation_failed"
            }

        return {
            "generated_sql": res.get("sql"),
            "current_step": "sql_generated",
            "error": None
        }
    except Exception as e:
        return {
            "generated_sql": None,
            "error": f"SQL generation error: {str(e)}",
            "current_step": "sql_generation_failed"
        }


@traceable(name="Validate SQL")
def validate_sql_node(state: QueryState) -> Dict[str, Any]:
    """
    Node 3: Validate generated SQL for read-only safety, keywords, and database schema compliance.
    """
    if state.get("error"):
        return {"current_step": "validation_bypassed"}

    generated_sql = state.get("generated_sql")
    if not generated_sql:
        return {
            "validated_sql": None,
            "error": "No SQL statement available for validation.",
            "current_step": "validation_failed"
        }

    val_res = validate_sql(generated_sql)
    if not val_res["valid"]:
        return {
            "validated_sql": None,
            "error": val_res["error"],
            "current_step": "validation_failed"
        }

    return {
        "validated_sql": val_res["sql"],
        "current_step": "sql_validated",
        "error": None
    }


@traceable(name="Execute Safe SQL")
def execute_sql_node(state: QueryState) -> Dict[str, Any]:
    """
    Node 4: Execute validated read-only SQL query against SQLite database workday_hr.db.
    """
    if state.get("error"):
        return {"current_step": "execution_bypassed"}

    validated_sql = state.get("validated_sql")
    if not validated_sql:
        return {
            "query_result": None,
            "error": "No validated SQL available for execution.",
            "current_step": "execution_failed"
        }

    exec_res = execute_safe_query(validated_sql)
    if exec_res.get("error"):
        return {
            "query_result": exec_res,
            "error": exec_res["error"],
            "current_step": "execution_failed"
        }

    return {
        "query_result": exec_res,
        "current_step": "sql_executed",
        "error": None
    }


@traceable(name="Generate Answer")
def generate_answer_node(state: QueryState) -> Dict[str, Any]:
    """
    Node 5: Synthesize human-readable answer from question and query execution result.
    """
    question = state.get("question", "")
    query_result = state.get("query_result") or {"rows": [], "columns": [], "row_count": 0}

    ans_res = generate_answer(question, query_result)

    # Preserve answer even if LLM completion logged a warning/error (uses deterministic fallback)
    return {
        "answer": ans_res.get("answer"),
        "current_step": "answer_generated",
        "error": None
    }


@traceable(name="Error Handler")
def error_handler_node(state: QueryState) -> Dict[str, Any]:
    """
    Terminal node handling workflow errors cleanly without exposing raw stack traces.
    """
    err = state.get("error") or "An unexpected workflow error occurred."
    step = state.get("current_step", "error_occurred")

    query_result = state.get("query_result")
    if query_result and query_result.get("rows"):
        fallback = format_fallback_answer(state.get("question", ""), query_result)
        answer_text = f"{fallback} (Note: {err})"
    else:
        answer_text = f"Unable to process query: {err}"

    return {
        "answer": answer_text,
        "current_step": f"error_{step}",
        "error": err
    }
