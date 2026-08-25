"""
LangGraph Workflow State Definition for Workday Data Query Agent.
"""

from typing import Any, Dict, List, Optional, TypedDict


class QueryState(TypedDict):
    """
    State dictionary passed between LangGraph workflow nodes.
    """
    question: str
    schema_context: List[Dict[str, Any]]
    generated_sql: Optional[str]
    validated_sql: Optional[str]
    query_result: Optional[Dict[str, Any]]
    answer: Optional[str]
    error: Optional[str]
    current_step: str
