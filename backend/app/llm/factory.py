import os

from dotenv import load_dotenv

from app.llm.gemini_client import GeminiClient
from app.llm.mock_client import MockLLMClient


def create_llm_client():
    load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "mock")
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        return GeminiClient(api_key=api_key)
    return MockLLMClient()


def get_llm_client():
    return create_llm_client()
