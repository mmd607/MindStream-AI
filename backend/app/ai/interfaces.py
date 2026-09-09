from typing import Protocol

from app.ai.schemas import Blueprint


class AIProvider(Protocol):
    name: str

    def generate_blueprint(self, project_name: str, description: str, preferred_stack: list[str]) -> Blueprint:
        """Return validated structured data. Implementations must not execute generated content."""

