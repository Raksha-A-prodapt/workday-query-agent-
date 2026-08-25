"""
Pydantic Request and Response Schemas for Workday Data Query API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural-language question for HR database")


class QueryResponse(BaseModel):
    question: str
    answer: Optional[str] = None
    data: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    generated_sql: Optional[str] = None
    error: Optional[str] = None
    status: str = "success"  # "success" or "error"
    truncated: Optional[bool] = False
