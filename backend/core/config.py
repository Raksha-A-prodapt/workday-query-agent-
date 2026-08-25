"""
Centralized Configuration for Workday Data Query Agent.
Loads environment variables from .env if present.
"""

import os
from dotenv import load_dotenv

# Load .env file from project root or backend directory if present
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)


class Settings:
    PROJECT_NAME: str = "Workday Data Query Agent API"
    PROJECT_DESCRIPTION: str = "Backend foundation for Workday-style HR query & reporting agent"
    VERSION: str = "0.1.0"

    # Base Directory (backend/)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Database Directory & File Path
    DB_DIR: str = os.path.join(BASE_DIR, "database")
    DB_PATH: str = os.path.join(DB_DIR, "workday_hr.db")

    # LLM Settings (properties dynamically fetch from environment)
    @property
    def LLM_PROVIDER(self) -> str:
        return os.getenv("LLM_PROVIDER", "openai")

    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def OPENAI_MODEL(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def OPENAI_BASE_URL(self) -> str:
        return os.getenv("OPENAI_BASE_URL", "")

    # LangSmith Settings
    @property
    def LANGSMITH_TRACING(self) -> str:
        return os.getenv("LANGSMITH_TRACING", "false")

    @property
    def LANGSMITH_API_KEY(self) -> str:
        return os.getenv("LANGSMITH_API_KEY", "")

    @property
    def LANGSMITH_PROJECT(self) -> str:
        return os.getenv("LANGSMITH_PROJECT", "workday-hr-ai-assistant")

    @property
    def LANGSMITH_ENDPOINT(self) -> str:
        return os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")


    @property
    def is_langsmith_enabled(self) -> bool:
        tracing = str(self.LANGSMITH_TRACING).strip().lower() in ("true", "1", "yes")
        api_key = bool(self.LANGSMITH_API_KEY and self.LANGSMITH_API_KEY.strip())
        return tracing and api_key


settings = Settings()


def configure_langsmith():
    """
    Synchronizes LangSmith and LangChain environment variables based on current Settings.
    Sets standard LANGCHAIN_TRACING_V2 and LANGSMITH_TRACING variables when tracing is enabled
    with a valid API key, or unsets/disables them safely when disabled or missing API key.
    """
    if settings.is_langsmith_enabled:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    else:
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"

