from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SearchProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def search_opportunities(
        self,
        roles: List[str],
        locations: List[str],
        companies: List[str] = None,
        keywords: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Searches legitimate public web sources for internship listings."""
        pass

    @abstractmethod
    async def search_contacts(
        self,
        company_name: str,
        target_roles: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Searches legitimate public sources for early career/university recruiting contacts."""
        pass
