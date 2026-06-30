import json
import re

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class GeminiClient:
    def __init__(self, api_key: str, model: str = DEFAULT_GEMINI_MODEL):
        self.api_key = api_key
        self.model = model

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict | None = None,
    ) -> dict:
        # The project runs in mock mode by default. Verify this adapter against
        # the installed google-genai SDK version before enabling live Gemini use.
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("google-genai is required for LLM_PROVIDER=gemini") from exc

        client = genai.Client(api_key=self.api_key)

        # Request JSON output via the mime type only. A free-form schema dict is
        # not a valid response_schema for the SDK, so we enforce the shape with
        # Pydantic after parsing instead of relying on constrained decoding here.
        response = client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        parsed = _parse_json_object(response.text)
        if parsed is None:
            raise RuntimeError("Gemini returned invalid JSON")

        return parsed


def _parse_json_object(text: str) -> dict | None:
    candidate = _strip_code_fences(text).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        parsed = _parse_first_json_object(candidate)

    if isinstance(parsed, dict):
        return parsed
    return None


def _strip_code_fences(text: str) -> str:
    fence = re.match(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", text, re.DOTALL)
    if fence:
        return fence.group(1)
    return text


def _parse_first_json_object(text: str) -> dict | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : index + 1])
                except json.JSONDecodeError:
                    return None
    return None


GeminiLLMClient = GeminiClient
