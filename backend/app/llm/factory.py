import os

from app.llm.gemini_client import GeminiLLMClient
from app.llm.mock_client import MockLLMClient


def get_llm_client():
    provider = os.getenv("LLM_PROVIDER", "mock")
    if provider == "gemini":
        return GeminiLLMClient(api_key=os.getenv("GEMINI_API_KEY", ""))
    return MockLLMClient()
