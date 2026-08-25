"""
Human-Readable Answer Generator Module.
Synthesizes accurate natural-language answers from structured SQL query results using LLM completions.
Features strict zero-hallucination prompts and deterministic fallback formatting with semantic alias mappings.
"""

import os
import sys
from typing import Any, Dict, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.llm import generate_completion

ANSWER_SYSTEM_PROMPT = """You are a precise Workday HR data assistant.
Your task is to convert structured SQL query results into a clear, concise, natural-language answer responding directly to the user's question.

CRITICAL ACCURACY RULES:
1. Answer using ONLY the supplied query result data. Do NOT use outside knowledge or make ungrounded assumptions.
2. Do NOT invent figures, statistics, trends, rankings, causes, or comparisons not explicitly supported by the returned rows.
3. Preserve exact numerical figures. Do NOT arbitrarily round numbers unless the database result itself is already rounded.
4. Do NOT mention SQL syntax, table names, or database internals.
5. Keep answers concise, professional, and clear for business leaders.
6. If the result reflects active employee headcount, explicitly state "active employees" in your response.
7. If no rows are returned, state clearly: "No matching records were found."
8. Do NOT output meta-commentary or statements like "A bar graph can be created based on this data". The user interface automatically renders visual charts from the data.
"""

# Semantic fallback templates for common aggregate column aliases
FALLBACK_ALIAS_MAP = {
    "active_headcount": "There are {val} active employees.",
    "employees_on_leave": "There are {val} employees currently on leave.",
    "open_jobs": "There are {val} open job positions.",
    "employee_count": "There are {val} employees.",
    "headcount": "There are {val} active employees.",
    "total_employees": "There are {val} employees.",
    "approved_leave_count": "There are {val} approved leave requests.",
    "approved_leaves": "There are {val} approved leave requests.",
    "total_leaves": "There are {val} leave records."
}


def format_fallback_answer(question: str, query_result: Dict[str, Any]) -> str:
    """
    Generate an accurate, deterministic, non-LLM fallback answer directly from query results,
    using semantic alias mappings for clear human readability.
    """
    rows = query_result.get("rows", [])
    columns = query_result.get("columns", [])
    row_count = query_result.get("row_count", len(rows))

    if not rows or row_count == 0:
        return "No matching records were found."

    # Single aggregate row with 1 column
    if row_count == 1 and len(columns) == 1:
        col_name = columns[0].lower()
        val = rows[0][columns[0]]
        if col_name in FALLBACK_ALIAS_MAP:
            return FALLBACK_ALIAS_MAP[col_name].format(val=val)
        readable_label = col_name.replace("_", " ")
        return f"The total {readable_label} is {val}."

    # Single row with multiple columns (e.g. employee details)
    if row_count == 1:
        items = [f"{k.replace('_', ' ').title()}: {v}" for k, v in rows[0].items()]
        return "Query result: " + ", ".join(items) + "."

    # Multiple rows summary
    summaries = []
    for r in rows[:5]:
        vals = list(r.values())
        if len(vals) >= 2:
            summaries.append(f"{vals[0]}: {vals[1]}")
        else:
            summaries.append(str(vals[0]))

    summary_text = ", ".join(summaries)
    if row_count > 5:
        summary_text += f" (and {row_count - 5} more)"

    return f"Query returned {row_count} records: {summary_text}."


def generate_answer(question: str, query_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a faithful human-readable answer from structured SQL execution results.

    Args:
        question: Original natural-language question.
        query_result: Output dictionary from execute_safe_query().

    Returns:
        Structured dictionary: {
            "answer": str,
            "data": List[Dict[str, Any]],
            "row_count": int,
            "error": str or None
        }
    """
    if not question or not isinstance(question, str) or not question.strip():
        return {
            "answer": "Question cannot be empty.",
            "data": [],
            "row_count": 0,
            "error": "Question cannot be empty."
        }

    cleaned_question = question.strip()

    # Handle query execution error input
    exec_error = query_result.get("error") if query_result else None
    if exec_error:
        return {
            "answer": f"Unable to generate answer due to query error: {exec_error}",
            "data": [],
            "row_count": 0,
            "error": exec_error
        }

    rows = query_result.get("rows", []) if query_result else []
    columns = query_result.get("columns", []) if query_result else []
    row_count = query_result.get("row_count", len(rows)) if query_result else 0

    # Rule: Empty result check (Do not call LLM for empty results)
    if not rows or row_count == 0:
        return {
            "answer": "No matching records were found.",
            "data": [],
            "row_count": 0,
            "error": None
        }

    user_prompt = f"""USER QUESTION:
"{cleaned_question}"

STRUCTURED QUERY RESULT:
Columns: {columns}
Row Count: {row_count}
Rows Data: {rows}

Generate a clear, natural-language answer responding directly to the question:"""

    try:
        # Call LLM service for natural-language answer synthesis
        answer_text = generate_completion(user_prompt, system_prompt=ANSWER_SYSTEM_PROMPT)

        if not answer_text or not answer_text.strip():
            fallback_text = format_fallback_answer(cleaned_question, query_result)
            return {
                "answer": fallback_text,
                "data": rows,
                "row_count": row_count,
                "error": "LLM returned empty completion; fallback used."
            }

        return {
            "answer": answer_text.strip(),
            "data": rows,
            "row_count": row_count,
            "error": None
        }

    except Exception as e:
        # Graceful fallback on API key missing or network error
        fallback_text = format_fallback_answer(cleaned_question, query_result)
        return {
            "answer": fallback_text,
            "data": rows,
            "row_count": row_count,
            "error": str(e)
        }


if __name__ == "__main__":
    sample_result = {
        "columns": ["active_headcount"],
        "rows": [{"active_headcount": 425}],
        "row_count": 1,
        "truncated": False,
        "error": None
    }
    q = "How many employees are there?"
    print("Testing generate_answer() fallback mapping:")
    ans = generate_answer(q, sample_result)
    print("Answer:", ans["answer"])
