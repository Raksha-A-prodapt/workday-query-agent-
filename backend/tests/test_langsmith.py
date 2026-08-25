"""
Tests for LangSmith Observability and Tracing Configuration & Workflow Integration.
Verifies setting resolution, process env sync, key non-exposure, and workflow execution under various LangSmith states.
"""

import os
import sys
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.config import settings, configure_langsmith
from backend.workflow.graph import run_query_workflow


def test_langsmith_config_disabled_by_default(monkeypatch):
    """
    Test that is_langsmith_enabled is False when LANGSMITH_TRACING is false or API key is empty.
    """
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGSMITH_API_KEY", "")
    assert not settings.is_langsmith_enabled

    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "")
    assert not settings.is_langsmith_enabled


def test_langsmith_config_enabled_when_valid(monkeypatch):
    """
    Test that is_langsmith_enabled is True when LANGSMITH_TRACING=true and API key is present.
    """
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls__test_api_key_12345")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    monkeypatch.setenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

    assert settings.is_langsmith_enabled
    assert settings.LANGSMITH_PROJECT == "test-project"

    configure_langsmith()
    assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
    assert os.environ.get("LANGSMITH_TRACING") == "true"
    assert os.environ.get("LANGCHAIN_API_KEY") == "ls__test_api_key_12345"


def test_workflow_runs_with_langsmith_disabled(monkeypatch):
    """
    Test that run_query_workflow completes normally when LangSmith tracing is explicitly disabled.
    """
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGSMITH_API_KEY", "")

    configure_langsmith()
    assert os.environ.get("LANGSMITH_TRACING") == "false"

    res = run_query_workflow("How many active employees are there?")
    assert isinstance(res, dict)
    assert res["current_step"] in ("answer_generated", "sql_executed")
    assert res["error"] is None or isinstance(res["error"], str)
    assert "answer" in res


def test_workflow_runs_with_missing_api_key(monkeypatch):
    """
    Test that run_query_workflow completes normally when LANGSMITH_TRACING=true but API key is missing.
    """
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "")

    configure_langsmith()
    assert os.environ.get("LANGSMITH_TRACING") == "false"

    res = run_query_workflow("How many employees are on leave?")
    assert isinstance(res, dict)
    assert "answer" in res


def test_no_api_key_exposed_in_responses(monkeypatch):
    """
    Ensure LANGSMITH_API_KEY is never exposed in returned workflow dictionaries or answers.
    """
    secret_key = "ls__secret_key_never_leak_999"
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", secret_key)

    res = run_query_workflow("List department names")
    str_res = str(res)

    assert secret_key not in str_res
    assert secret_key not in (res.get("answer") or "")


def test_existing_workflow_behavior_unchanged(monkeypatch):
    """
    Verify existing workflow outputs and structure remain identical.
    """
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    res = run_query_workflow("What is the headcount of active employees?")
    assert "question" in res
    assert "schema_context" in res
    assert "validated_sql" in res
    assert "query_result" in res
    assert "answer" in res
    assert "error" in res
    assert "current_step" in res
