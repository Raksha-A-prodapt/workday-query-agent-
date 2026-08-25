"""
Health Check Route.
"""

from fastapi import APIRouter, HTTPException
from backend.database.connection import check_db_health

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint confirming API status and SQLite database connectivity."""
    db_status = check_db_health()
    if db_status != "connected":
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": db_status}
        )

    return {
        "status": "healthy",
        "database": "connected"
    }
