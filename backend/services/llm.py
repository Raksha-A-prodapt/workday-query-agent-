"""
LLM Service Module isolating provider implementation (OpenAI).
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import openai
from backend.core.config import settings

try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator


@traceable(name="LLM Completion", run_type="llm")
def generate_completion(prompt: str, system_prompt: str = None) -> str:

    """
    Generate completion using configured LLM provider (OpenAI).

    Args:
        prompt: Main user/context prompt text.
        system_prompt: System prompt instructing LLM role and constraints.

    Returns:
        String completion response.
    """
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("LLM API Key is missing. Please set OPENAI_API_KEY in your environment or .env file.")

    client_args = {"api_key": api_key}
    if settings.OPENAI_BASE_URL:
        client_args["base_url"] = settings.OPENAI_BASE_URL

    client = openai.OpenAI(**client_args)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.0
    )

    return response.choices[0].message.content.strip()
