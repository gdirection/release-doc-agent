class GeminiLLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_json(self, prompt: str, context: dict):
        raise NotImplementedError("Gemini adapter is optional and not implemented yet.")
