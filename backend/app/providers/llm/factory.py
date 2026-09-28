from app.core.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.claude_provider import ClaudeProvider
from app.providers.llm.gemini_provider import GeminiProvider
from app.providers.llm.mock_provider import MockLLMProvider

def get_llm_provider(provider_override: str = None) -> LLMProvider:
    """
    Returns the appropriate LLM provider based on settings or explicit override.
    Defaults to MockLLMProvider if MOCK_MODE is enabled or API keys are missing.
    """
    selected = (provider_override or settings.PRIMARY_LLM_PROVIDER).lower()

    if settings.MOCK_MODE:
        return MockLLMProvider()

    if selected == "claude":
        if settings.ANTHROPIC_API_KEY:
            return ClaudeProvider()
        return MockLLMProvider()
    elif selected == "gemini":
        if settings.GEMINI_API_KEY:
            return GeminiProvider()
        return MockLLMProvider()
    
    return MockLLMProvider()
