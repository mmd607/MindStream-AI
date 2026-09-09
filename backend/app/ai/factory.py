from app.ai.interfaces import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.real_provider import RealLLMProvider
from app.core.config import settings


def get_provider() -> AIProvider:
    if settings.ai_provider == "real":
        return RealLLMProvider()
    return MockAIProvider()

