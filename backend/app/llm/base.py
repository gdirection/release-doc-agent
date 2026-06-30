from typing import Protocol


class LLMClient(Protocol):
    def generate_json(self, prompt: str, context: dict):
        ...
