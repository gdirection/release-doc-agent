from typing import Protocol


class LLMClient(Protocol):
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict | None = None,
    ) -> dict:
        ...
