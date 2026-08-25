"""
Query Endpoint Route.
Delegates natural language HR query execution to the compiled LangGraph workflow.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import QueryRequest, QueryResponse
from backend.workflow.graph import run_query_workflow

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Executes end-to-end HR query via LangGraph StateGraph workflow.
    """
    cleaned_question = request.question.strip()
    if not cleaned_question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Invoke compiled LangGraph workflow
        workflow_res = run_query_workflow(cleaned_question)

        query_result = workflow_res.get("query_result") or {}
        rows = query_result.get("rows", [])
        row_count = query_result.get("row_count", len(rows))
        truncated = query_result.get("truncated", False)

        generated_sql = workflow_res.get("validated_sql") or workflow_res.get("generated_sql")
        error = workflow_res.get("error")
        answer = workflow_res.get("answer")
        current_step = workflow_res.get("current_step", "")

        # Determine API response status
        if error and current_step.startswith("error"):
            status = "error"
        elif error and not answer:
            status = "error"
        else:
            status = "success"

        return QueryResponse(
            question=cleaned_question,
            answer=answer,
            data=rows,
            row_count=row_count,
            generated_sql=generated_sql,
            error=error,
            status=status,
            truncated=truncated
        )

    except HTTPException:
        raise
    except Exception as e:
        # Catch unexpected internal exceptions safely without exposing stack traces
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the query."
        )
