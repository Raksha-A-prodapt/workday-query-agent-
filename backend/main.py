"""
FastAPI Main Entry Point for Workday Data Query and Reporting Agent.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.routes import health, query

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router)
app.include_router(query.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
