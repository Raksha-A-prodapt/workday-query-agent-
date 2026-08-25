"""
Prompt Templates and Prompt Construction for SQL Generation.
"""

from typing import Any, Dict, List

SQL_SYSTEM_PROMPT = """You are an expert SQLite SQL generator for a Workday-style HR database.
Your task is to convert the user's natural-language question into a single, valid, read-only SQLite SQL statement.

CRITICAL RULES:
1. Use ONLY the tables and columns present in the retrieved schema context provided below.
2. NEVER invent tables, columns, or relationships that are not documented in the schema context.
3. Use SQLite syntax ONLY (e.g. use julianday() for date math, || for string concatenation).
4. Generate exactly ONE SQL statement starting with SELECT or WITH.
5. The statement must be strictly READ-ONLY.
6. COLUMN & JOIN MAPPINGS:
   - Employee names are stored as `first_name` and `last_name` (there is NO `name` column). Concatenate using `e.first_name || ' ' || e.last_name AS employee_name`.
   - Employee job title / role is stored as `job_title` (there is NO `role` column).
   - Department Heads / Department Directors / Department Leaders are the top-level employees where `e.manager_id IS NULL` ONLY. Do NOT use `OR e.job_title LIKE '%Director%'` because multiple non-head employees share director titles. Using `e.manager_id IS NULL` guarantees exactly 1 head per department.
   - department_name does NOT exist in employees or job_openings. Join departments ON department_id.
   - region_name does NOT exist in employees or job_openings. Join regions ON region_id.
   - Manager names do NOT exist directly on employees. Perform a self-join ON e.manager_id = m.employee_id.
7. DATE & TENURE CALCULATIONS IN SQLITE:
   - To calculate tenure / years of experience from hire_date, use:
     `ROUND((julianday('now') - julianday(hire_date)) / 365.25, 1) AS tenure_years`
   - NEVER output raw `julianday(hire_date)` or `julianday('now')` alone without subtracting and dividing by 365.25.
8. Return ONLY raw SQL text.
9. Do NOT wrap SQL in Markdown code fences (e.g. no ```sql or ```).
10. Do NOT include any explanations, preamble, or commentary.
11. Do NOT use PostgreSQL, MySQL, SQL Server, or Oracle syntax.
12. When combining queries using UNION or UNION ALL where individual branches require ORDER BY and LIMIT, ALWAYS wrap each branch in a subquery `SELECT * FROM (SELECT ...) UNION ALL SELECT * FROM (SELECT ...)` or use WITH / CTE blocks. NEVER place ORDER BY/LIMIT directly before UNION or UNION ALL.
"""


def build_sql_prompt(question: str, schema_context_chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved RAG schema context snippets and user question into a prompt.
    """
    context_blocks = []
    for i, chunk in enumerate(schema_context_chunks, 1):
        sec = chunk.get("metadata", {}).get("section", "unknown")
        c_type = chunk.get("metadata", {}).get("type", "schema")
        content = chunk.get("content", "").strip()
        context_blocks.append(f"--- CONTEXT BLOCK {i} [{sec} | {c_type}] ---\n{content}")

    formatted_context = "\n\n".join(context_blocks)

    user_prompt = f"""RETRIEVED DATABASE SCHEMA & BUSINESS CONTEXT:
{formatted_context}

USER QUESTION:
"{question}"

Generate the exact SQLite SQL query to answer this question:"""

    return user_prompt
