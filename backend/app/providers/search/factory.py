from app.core.config import settings
from app.providers.search.base import SearchProvider
from app.providers.search.tavily_provider import TavilySearchProvider
from app.providers.search.mock_provider import MockSearchProvider

def get_search_provider(provider_override: str = None) -> SearchProvider:
    selected = (provider_override or settings.SEARCH_PROVIDER).lower()

    if settings.MOCK_MODE:
        return MockSearchProvider()

    if selected == "tavily" and settings.SEARCH_PROVIDER_API_KEY:
        return TavilySearchProvider()

    return MockSearchProvider()
