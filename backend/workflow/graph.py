"""
LangGraph StateGraph Workflow Orchestrator for Workday Data Query Agent.
Connects RAG schema retrieval, SQL generation, validation, safe execution, and answer synthesis into a compiled graph.
"""

import os
import sys
from typing import Any, Dict
from langgraph.graph import StateGraph, START, END

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.config import configure_langsmith
from backend.workflow.state import QueryState
from backend.workflow.nodes import (
    retrieve_context_node,
    generate_sql_node,
    validate_sql_node,
    execute_sql_node,
    generate_answer_node,
    error_handler_node
)

try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator



def route_after_validation(state: QueryState) -> str:
    """
    Conditional routing edge checking if SQL validation passed.
    """
    if state.get("error") or state.get("current_step") == "validation_failed":
        return "error_handler"
    return "execute_sql"


def route_after_execution(state: QueryState) -> str:
    """
    Conditional routing edge checking if SQL execution succeeded.
    """
    if state.get("error") or state.get("current_step") == "execution_failed":
        return "error_handler"
    return "generate_answer"


def build_workflow_graph():
    """
    Constructs and compiles the LangGraph StateGraph pipeline.
    """
    builder = StateGraph(QueryState)

    # Register workflow nodes
    builder.add_node("retrieve_context", retrieve_context_node)
    builder.add_node("generate_sql", generate_sql_node)
    builder.add_node("validate_sql", validate_sql_node)
    builder.add_node("execute_sql", execute_sql_node)
    builder.add_node("generate_answer", generate_answer_node)
    builder.add_node("error_handler", error_handler_node)

    # Define graph edges
    builder.add_edge(START, "retrieve_context")
    builder.add_edge("retrieve_context", "generate_sql")
    builder.add_edge("generate_sql", "validate_sql")

    # Conditional routing after validation
    builder.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {
            "execute_sql": "execute_sql",
            "error_handler": "error_handler"
        }
    )

    # Conditional routing after execution
    builder.add_conditional_edges(
        "execute_sql",
        route_after_execution,
        {
            "generate_answer": "generate_answer",
            "error_handler": "error_handler"
        }
    )

    # Terminal node edges
    builder.add_edge("generate_answer", END)
    builder.add_edge("error_handler", END)

    return builder.compile()


# Compile graph singleton
workflow_app = build_workflow_graph()


def get_workflow_mermaid() -> str:
    """
    Generate Mermaid graph diagram representation of the workflow.
    """
    return """graph TD
    START([START]) --> retrieve_context[1. Retrieve Schema RAG Context]
    retrieve_context --> generate_sql[2. Generate SQLite SQL]
    generate_sql --> validate_sql[3. Validate Read-Only SQL]
    
    validate_sql -->|SQL Valid| execute_sql[4. Execute Safe Query]
    validate_sql -->|SQL Invalid / Error| error_handler[Error Handler]
    
    execute_sql -->|Execution Success| generate_answer[5. Generate Human Answer]
    execute_sql -->|Execution Failure| error_handler
    
    generate_answer --> END([END])
    error_handler --> END
"""


@traceable(name="Workday HR Query")
def run_query_workflow(question: str) -> Dict[str, Any]:
    """
    Public entry point for running the end-to-end LangGraph query workflow.

    Args:
        question: User natural-language HR query.

    Returns:
        Final state dictionary containing question, sql, results, answer, error, and current_step.
    """
    configure_langsmith()

    initial_state: QueryState = {
        "question": question,
        "schema_context": [],
        "generated_sql": None,
        "validated_sql": None,
        "query_result": None,
        "answer": None,
        "error": None,
        "current_step": "started"
    }

    final_state = workflow_app.invoke(initial_state, config={"run_name": "Workday HR Query"})
    return dict(final_state)



if __name__ == "__main__":
    test_q = "How many employees are currently on leave?"
    print(f"Executing workflow for: '{test_q}'")
    res = run_query_workflow(test_q)
    print("Final Step:", res["current_step"])
    print("Answer:", res["answer"])
    print("Error:", res["error"])
    print("SQL:", res["validated_sql"])
