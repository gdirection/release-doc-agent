import json


class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

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
        config_kwargs = {"response_mime_type": "application/json"}
        if schema is not None:
            config_kwargs["response_schema"] = schema

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(**config_kwargs),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        try:
            parsed = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise RuntimeError("Gemini JSON response must be an object")

        return parsed


GeminiLLMClient = GeminiClient
